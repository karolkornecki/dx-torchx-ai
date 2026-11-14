import torch

# Klasa pomocnicza, zawiera funkcje do logowania różnych zdarzeń.
class Logger:

    @staticmethod
    def log_number_of_gpu():
        print("Number of available GPUs: " + str(torch.cuda.device_count()))

    @staticmethod
    def model_checkpoint_saved(best_loss, epoch):
        print(f"Model checkpoint! best_val_loss=[{best_loss}], epoch=[{epoch}]")

    @staticmethod
    def epoch_started(current_epoch, num_epochs, current_learning_rate):
        print("-" * 70)
        print(
            f"Epoch {current_epoch}/{num_epochs} | Learning rate: {current_learning_rate}"
        )

    @staticmethod
    def display_run_on_cpu_warning():
        print(
            "WARNING: There are no GPUs available. It will be run on CPU. It can be extremely slow!"
        )

    @staticmethod
    def epoch_result(phase, epoch, epoch_loss, dataset_size):
        print(
            f"PHASE[{phase}]: "
            f"epoch:[{epoch}] "
            f"{phase}_loss: [{epoch_loss:.5f}] "
            f"dataset_size: {dataset_size}"
        )

    @staticmethod
    def training_completed(time_elapsed):
        print("-" * 70)
        print(f"COMPLETED! in {(time_elapsed // 60):.0f}m {(time_elapsed % 60):.0f}s")

    @staticmethod
    def batches_processed(batch_number, total_number_of_batches):
        print(f"{batch_number + 1}/{total_number_of_batches} batches processed.")
