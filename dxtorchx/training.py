from __future__ import division, print_function, annotations

import csv
import math
import os
import os.path
import time
from abc import ABC, abstractmethod
from shutil import rmtree

import numpy as np
import pandas as pd
import sklearn.metrics as metrics
import torch
import torch.nn as nn
import torch.optim as optim
from PIL import Image
from torch.optim.lr_scheduler import ReduceLROnPlateau
from torch.utils.data import Dataset

from dxtorchx.logging import Logger
from dxtorchx.model_const import NORMALIZER, NORMALIZER_TRAIN, NUMBER_OF_CLASSES, PREDICTABLE_CLASSES, \
    DEVICE, is_gpu

# katalog ze wszystkimi zdjęciami
IMAGES_DIR = "images"

# nazwa kolumny z pliku CSV, w której znajduję się nazwa pliku obrazu
DATASET_IMAGE_NAME_COLUMN = "Image Index"

TRAIN = "train"
VAL = "val"

# maksymalna ilość epok treningu
NUM_EPOCHS = 100
# parameter momentum algorytmu Stochastic Gradient Descent
SGD_MOMENTUM = 0.9
# cierpliwość mechanizmu "EarlyStopping" jeśli wartość funkcji kosztu nie maleje od 3 epok to przerywamy trenowanie sieci
PATIENCE = 3

# wybieramy model do treningu
CNN_ARCHITECTURE = "DENSENET_121"
# prefix plików ze zbiorami treningowym i walidującym
LABEL_FILE_PREFIX = "nih_labels"

# plik ze zbiorem testowym
TEST_SET_FILE = f"{LABEL_FILE_PREFIX}_test.csv"
# plik ze zbiorem treningowo walidującym
TRAIN_VAL_SET_FILE = f"{LABEL_FILE_PREFIX}_train_val.csv"


# funkcja zwraca nazwe pliku ze zbiorem treningowym dla danego fold'a
def fold_train_set_file(fold):
    return f"{LABEL_FILE_PREFIX}_train_f{fold}.csv"


# funkcja zwraca nazwe pliku ze zbiorem walidującym dla danego fold'a
def fold_val_set_file(fold):
    return f"{LABEL_FILE_PREFIX}_val_f{fold}.csv"


# funkcja zwraca nazwę katalogu z wynikami treningu dla danego fold'a i wersji modelu
def fold_results_dir(fold, version):
    return f"results_{CNN_ARCHITECTURE}_f{fold}_{version}"


# funkcja zwraca nazwę pliku z wagami dla danego fold'a i wersji modelu
def fold_model_checkpoint(fold, version):
    return f"checkpoint_{CNN_ARCHITECTURE}_f{fold}_{version}.pth"


# funkcja zwraca log z trenowania modelu, zawiera ilość epok, koszt w epoce itp, dla danego fold'a i wersji modelu
def fold_train_log_file(fold, version):
    return f"train_log_{CNN_ARCHITECTURE}_f{fold}_{version}.log"


# funkcja zwraca nazwę pliku z wartościami prawdziwych etykiet dla zbioru walidującego dla danego fold'a i wersji modelu
def fold_y_true_file(fold, version):
    return f"y_true_{CNN_ARCHITECTURE}_f{fold}_{version}.csv"


# funkcja zwraca nazwę pliku z prawdopodobieństwami wystąpenia każdej klasy dla zbioru walidującego dla danego fold'a i wersji modelu
def fold_y_probability_file(fold, version):
    return f"y_probability_{CNN_ARCHITECTURE}_f{fold}_{version}.csv"


# funkcja zwraca nazwę pliku z metrykami AUC dla każdej klasy dla zbioru walidującego dla danego fold'a i wersji modelu
def fold_auc_metrics_file(fold, version):
    return f"auc_metrics_{CNN_ARCHITECTURE}_f{fold}_{version}.csv"

# Klasa abstrakcyjna reprezentująca zbiór danych
class ChestXrayDataset(Dataset, ABC):
    def __init__(self, filename):
        df = pd.read_csv(filename)
        df = df.set_index(DATASET_IMAGE_NAME_COLUMN)
        self.df = df

    def __len__(self):
        return len(self.df)

    def __getitem__(self, index):
        # etykiety 14 schorzeń dla danego zdjęcia
        labels = np.array(
            [int(self.df[PREDICTABLE_CLASSES[i]].iloc[index]) for i in range(NUMBER_OF_CLASSES)]
        )
        # wczytuje zdjęcie
        img = Image.open(os.path.join(IMAGES_DIR, self.df.index[index])).convert("RGB")
        # normalizuje zdjęcie
        normalized_image = self.preprocess(img)
        return normalized_image, labels, self.df.index[index]

    @abstractmethod
    def preprocess(self, img):
        pass


# Klasa reprezentująca zbiór treningowy
class TrainDataset(ChestXrayDataset):

    def __init__(self, fold):
        dataset_file = TRAIN_VAL_SET_FILE if fold is None else fold_train_set_file(fold)
        super().__init__(dataset_file)

    def preprocess(self, img):
        return NORMALIZER_TRAIN(img)


# Klasa reprezentująca zbiór walidujący
class ValidationDataset(ChestXrayDataset):

    def __init__(self, fold):
        super().__init__(fold_val_set_file(fold))

    def preprocess(self, img):
        return NORMALIZER(img)


# Klasa reprezentująca zbiór testowy
class TestDataset(ChestXrayDataset):

    def __init__(self):
        super().__init__(TEST_SET_FILE)

    def preprocess(self, img):
        return NORMALIZER(img)


# Klasa reprezentująca sieć neuronową
class NeuralNetwork:

    def __init__(
            self,
            learning_rate,
            weight_decay,
            batch_size,
            model,
            train_dataset: TrainDataset,
            validation_dataset: ValidationDataset | None,
            fold,
            version,
    ):
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.model = model
        self.datasets = {TRAIN: train_dataset, VAL: validation_dataset}
        self.dataloaders = {
            TRAIN: torch.utils.data.DataLoader(
                train_dataset, batch_size=batch_size, shuffle=True, num_workers=8
            ),
            # wyłączam mieszanie dla zbioru walidującego
            VAL: torch.utils.data.DataLoader(
                validation_dataset, batch_size=batch_size, shuffle=False, num_workers=8
            ),
        }
        self.fold = fold
        self.version = version
        # katalog z wynikami
        self.RESULTS_DIR = f"results_{CNN_ARCHITECTURE}_{version}"
        # nazwa pliku wag modelu
        self.MODEL_CHECKPOINT = f"checkpoint_{CNN_ARCHITECTURE}_{version}.pth"

    def write_after_validation_phase_log(self, epoch, train_loss, val_loss):
        with open(
                os.path.join(
                    fold_results_dir(self.fold, self.version),
                    fold_train_log_file(self.fold, self.version),
                ),
                "a",
        ) as logfile:
            log_writer = csv.writer(logfile, delimiter=",")
            if epoch == 1:
                log_writer.writerow(["epoch", "train_loss", "val_loss"])
            log_writer.writerow([epoch, train_loss, val_loss])

    def model_checkpoint(self, best_loss, epoch):
        torch.save(
            self.model.state_dict(),
            str(
                os.path.join(
                    fold_results_dir(self.fold, self.version),
                    fold_model_checkpoint(self.fold, self.version),
                )
            ),
        )
        Logger.model_checkpoint_saved(best_loss, epoch)

    def final_model_checkpoint(self, best_loss, epoch):
        torch.save(
            self.model.state_dict(),
            str(os.path.join(self.RESULTS_DIR, self.MODEL_CHECKPOINT)),
        )
        Logger.model_checkpoint_saved(best_loss, epoch)

    def training_phase(self, optimizer, criterion, epoch):
        self.model.train()
        running_loss = 0.0
        total_samples = 0

        for inputs, labels, _ in self.dataloaders[TRAIN]:
            inputs = inputs.to(DEVICE)
            labels = labels.to(DEVICE).float()
            batch_size = inputs.size(0)

            optimizer.zero_grad()
            outputs = self.model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * batch_size
            total_samples += batch_size

        epoch_loss = running_loss / total_samples
        Logger.epoch_result(TRAIN, epoch, epoch_loss, total_samples)
        return epoch_loss

    def validation_phase(self, criterion, scheduler, epoch):
        self.model.eval()
        running_loss = 0.0
        total_samples = 0

        for inputs, labels, _ in self.dataloaders[VAL]:
            inputs = inputs.to(DEVICE)
            labels = labels.to(DEVICE).float()
            batch_size = inputs.size(0)

            with torch.no_grad():
                outputs = self.model(inputs)
                loss = criterion(outputs, labels)

            running_loss += loss.item() * batch_size
            total_samples += batch_size

        epoch_loss = running_loss / total_samples

        scheduler.step(epoch_loss)

        Logger.epoch_result(VAL, epoch, epoch_loss, total_samples)

        return epoch_loss

    def train(self):
        if os.path.exists(fold_results_dir(self.fold, self.version)):
            rmtree(fold_results_dir(self.fold, self.version))
        os.makedirs(fold_results_dir(self.fold, self.version))

        if not is_gpu():
            Logger.display_run_on_cpu_warning()

        criterion = nn.BCELoss()
        optimizer = optim.SGD(
            filter(lambda p: p.requires_grad, self.model.parameters()),
            lr=self.learning_rate,
            momentum=SGD_MOMENTUM,
            weight_decay=self.weight_decay,
        )

        start_date = time.time()

        start_epoch = 1
        best_loss = float("inf")
        best_epoch = -1

        scheduler = ReduceLROnPlateau(
            optimizer, mode="min", factor=0.1, patience=PATIENCE, threshold=1e-4
        )

        for epoch in range(start_epoch, NUM_EPOCHS + 1):
            current_learning_rate = optimizer.param_groups[0]["lr"]
            Logger.epoch_started(epoch, NUM_EPOCHS, current_learning_rate)
            train_loss = self.training_phase(
                optimizer=optimizer, criterion=criterion, epoch=epoch
            )
            val_loss = self.validation_phase(
                criterion=criterion, scheduler=scheduler, epoch=epoch
            )
            if val_loss < best_loss:
                best_loss = val_loss
                best_epoch = epoch
                self.model_checkpoint(best_loss, epoch)

            self.write_after_validation_phase_log(epoch, train_loss, val_loss)

            # Early stopping - jeśli nie mamy postępu
            if (epoch - best_epoch) >= PATIENCE:
                break

        time_elapsed = time.time() - start_date
        Logger.training_completed(time_elapsed)

        checkpoint_best = torch.load(
            str(
                os.path.join(
                    fold_results_dir(self.fold, self.version),
                    fold_model_checkpoint(self.fold, self.version),
                )
            ),
        )
        return checkpoint_best, best_epoch

    def train_final_model(self):
        if os.path.exists(self.RESULTS_DIR):
            rmtree(self.RESULTS_DIR)
        os.makedirs(self.RESULTS_DIR)

        if not is_gpu():
            Logger.display_run_on_cpu_warning()

        criterion = nn.BCELoss()
        optimizer = optim.SGD(
            filter(lambda p: p.requires_grad, self.model.parameters()),
            lr=self.learning_rate,
            momentum=SGD_MOMENTUM,
            weight_decay=self.weight_decay,
        )

        # maksymalna ilość epok treningu
        BEST_NUM_EPOCHS = 5

        start_date = time.time()
        for epoch in range(1, BEST_NUM_EPOCHS + 1):
            current_learning_rate = optimizer.param_groups[0]["lr"]
            Logger.epoch_started(epoch, BEST_NUM_EPOCHS, current_learning_rate)
            train_loss = self.training_phase(
                optimizer=optimizer, criterion=criterion, epoch=epoch
            )
            self.final_model_checkpoint(train_loss, epoch)

        time_elapsed = time.time() - start_date
        Logger.training_completed(time_elapsed)

        checkpoint_best = torch.load(str(os.path.join(self.RESULTS_DIR, self.MODEL_CHECKPOINT)))
        return checkpoint_best


def evaluate_dataset(trained_model, dataset, batch_size):
    dataloader = torch.utils.data.DataLoader(
        dataset, batch_size, shuffle=False, num_workers=8
    )

    trained_model.eval()
    Y_true = []
    Y_probability = []

    with torch.no_grad():
        for batch_number, [inputs, labels, _] in enumerate(dataloader):
            # ostatni batch może być mniejszy
            current_batch_size, _ = labels.shape
            x, y_true = inputs.to(DEVICE), labels.to(DEVICE).cpu().data.numpy()
            y_probability = trained_model(x).detach().cpu().numpy()

            for image_number in range(current_batch_size):
                filename = dataset.df.index[
                    batch_size * batch_number + image_number
                    ]
                row_probability = {DATASET_IMAGE_NAME_COLUMN: filename}
                row_true = {DATASET_IMAGE_NAME_COLUMN: filename}

                for class_index in range(NUMBER_OF_CLASSES):
                    row_probability[f"prob_{PREDICTABLE_CLASSES[class_index]}"] = (
                        y_probability[image_number, class_index]
                    )
                    row_true[PREDICTABLE_CLASSES[class_index]] = y_true[
                        image_number, class_index
                    ]

                Y_probability.append(row_probability)
                Y_true.append(row_true)

            if batch_number % 10 == 0:
                Logger.batches_processed(batch_number, math.ceil(len(dataloader)))

    return pd.DataFrame(Y_true), pd.DataFrame(Y_probability)


def auc_roc_metric(Y_true, Y_probability):
    assert len(set(Y_true.columns) & (set(PREDICTABLE_CLASSES))) == NUMBER_OF_CLASSES
    auc = []
    for class_name in PREDICTABLE_CLASSES:
        actual = Y_true[class_name]
        probability = Y_probability[f"prob_{class_name}"]
        try:
            auc_for_class = {
                "class_name": class_name,
                "AUC": metrics.roc_auc_score(
                    actual.to_numpy().astype(int), probability.to_numpy()
                ),
            }
            auc.append(auc_for_class)
        except BaseException as e:
            print(f"Error during ROC AUC calculation for class <{class_name}> {e}")

    return pd.DataFrame(auc)
