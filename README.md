# DX-TorchX-AI

An academic project for multi-label classification of chest X-ray images using deep learning. The repository covers the workflow from dataset exploration and model training to evaluation and a web application for exploring predictions.

**Language note:** This project was developed for a Polish university as part of a diploma thesis. Much of the repository is therefore in Polish, including notebook explanations, code comments, application labels, and the thesis itself. This README provides an English overview.

## What the project does

- Trains a DenseNet-121 model to classify 14 chest X-ray findings using the NIH ChestX-ray14 dataset.
- Compares hyperparameters with five-fold cross-validation, keeping each patient's images within the same split.
- Evaluates predictions using ROC AUC, precision–recall curves, calibration plots, and classification metrics.
- Provides a web interface with login, PNG image upload, test-set browsing, and comparisons between model predictions and dataset labels.
- Serves predictions through a Python inference API connected to a TypeScript backend.

The application is an academic demonstration of the trained model.

## Model and dataset

The model starts from ImageNet-pretrained DenseNet-121 weights and replaces the classifier with 14 sigmoid outputs. Each image can receive multiple positive labels:

> Atelectasis, Cardiomegaly, Effusion, Infiltration, Mass, Nodule, Pneumonia, Pneumothorax, Consolidation, Edema, Emphysema, Fibrosis, Pleural Thickening, and Hernia.

Images are converted to RGB, resized, center-cropped to 224 × 224 pixels, and normalized using ImageNet statistics. Training also applies random horizontal flips. Predictions are converted to binary labels using a separate saved threshold for each class.

The included metadata describes **112,120 images from 30,805 patients**. The saved split contains 101,170 training/validation images and 10,950 test images, with no patient overlap between those sets.

The final training notebook uses a learning rate of `0.01`, weight decay of `1e-4`, batch size of `16`, and five epochs. The saved final-model results report a **mean per-class ROC AUC of 0.8292** on the test set. See the [per-class AUC results](final_model/results_DENSENET_121_RELEASE/auc_metrics_DENSENET_121_RELEASE.csv) and [classification metrics](final_model/results_DENSENET_121_RELEASE/performance_metrics.csv). Notebook 5 selects classification thresholds from the test-set predictions; its threshold-based metrics reflect that choice.

Dataset metadata, label splits, model weights, and prediction results are included. The full X-ray image dataset is not included and must be supplied separately to rerun training or browse test images.

## Repository layout

| Path | Contents |
| --- | --- |
| `1_dataset_exploration.ipynb` | Dataset analysis, label preparation, and patient-based splits. |
| `2_model_training.ipynb` | Training and evaluation across cross-validation folds. |
| `3_k_cross_validation_metrics.ipynb` | Comparison of hyperparameter configurations. |
| `4_final_model_training.ipynb` | Final training with the selected hyperparameters. |
| `5_performance_metrics.ipynb` | Evaluation plots, metrics, confidence intervals, and threshold selection. |
| `6_predictions.ipynb` | Examples of predictions from the saved model. |
| `dxtorchx/` | Shared Python code for preprocessing, training, evaluation, and prediction. |
| `dataset_labels/` | Training, validation, and test label CSV files. |
| `kfold_results/` | Checkpoints and evaluation outputs for seven experiment configurations. |
| `final_model/` | Final model checkpoint, probabilities, labels, thresholds, and metrics. |
| `application/` | Web frontend, backend, inference service, database initialization, and Docker Compose configuration. |
| `praca_dyplomowa/` | [Polish diploma thesis](praca_dyplomowa/praca_dyplomowa_kkornecki2025.pdf) and supporting figures. |

## Application architecture

| Component | Technology | Responsibility |
| --- | --- | --- |
| Frontend | Angular 19, Angular Material, TypeScript | Login, image upload, patient/test-image browsing, and prediction display. |
| Backend | Node.js, Koa, TypeScript | Session authentication, patient metadata, image delivery, and requests to the inference service. |
| ML engine | Python 3.11, FastAPI, PyTorch, torchvision | Loads the saved DenseNet-121 model and returns per-class predictions. |
| Database | PostgreSQL 14 | Stores the demo user and test-set metadata. |
| Database administration | pgAdmin | Provides a browser interface to PostgreSQL. |

The backend serves the built Angular application and exposes routes under `/api`. It forwards prediction requests to the ML engine's `POST /model/predict` endpoint, which accepts a base64-encoded image and an optional filename for looking up test-set labels.

## Running the web application

You need Node.js and npm, plus Docker with Docker Compose. The existing application notes specify Node.js `22.14.0`. Docker supplies Python and PostgreSQL.

Run the following commands from the repository root to build the frontend and backend:

```sh
cd application/dx-torchx-ui
npm ci
npm run build -- --configuration production

cd ../dx-torchx-ai-server
npm ci
npm run build
mkdir -p dist/frontend src/test_images
cp -R ../dx-torchx-ui/dist/dx-torchx-ui/browser/. dist/frontend/
```

To use test-set browsing, place the original PNG files listed in `dataset_labels/nih_labels_test.csv` into `application/dx-torchx-ai-server/src/test_images/`, preserving their filenames. The backend Dockerfile copies this directory into the image. An empty directory lets the image build, but browsing those X-rays requires the corresponding files.

The inference service already includes `trained_model.pth`, `optimal_class_thresholds.csv`, and `y_true.csv` under its `src/` directory. Its model initialization also requests torchvision's default pretrained weights, so the first startup may download them.

From `application/dx-torchx-ai-server`, start the services:

```sh
cd ..
docker compose up --build
```

| Service | Local address |
| --- | --- |
| Web application | http://localhost:8080 |
| ML API documentation | http://localhost:8081/docs |
| pgAdmin | http://localhost:5050 |
| PostgreSQL | `localhost:5432` |

On the first database initialization, the SQL scripts create a demo account with email `karol.kornecki@gmail.com` and password `lekarz`. The pgAdmin login is `admin@admin.com` / `admin`; the database name is `dx_torchx_ai`, with username and password `postgres`. These values come from the included local demo configuration.

Stop the services with `docker compose down`. Database contents persist in the Compose volume; initialization scripts run only when that volume is first created.

## Working with the notebooks

Follow the numbered notebooks in order to explore the full research workflow. Training notebooks were written for Google Colab and use Google Drive paths under `/content/drive/MyDrive/_DATA_/nih_chest_x_ray_dataset/`; adapt these paths to your environment.

For local analysis, use Python 3.11, create an environment, and install the inference dependencies plus the notebook libraries:

```sh
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r application/dx-torchx-ai-ml-engine/requirements.txt
python -m pip install jupyter matplotlib seaborn scikit-learn
jupyter notebook
```

Run notebooks from the repository root so that imports from `dxtorchx` resolve. Training code expects images in `images/` and label CSV files in the working directory; copy the needed files from `dataset_labels/` or adjust the paths. The Colab-specific cells also need adaptation for local execution. Existing result CSVs support inspecting saved evaluations without retraining.
