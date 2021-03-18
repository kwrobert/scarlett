import gpt_2_simple as gpt2
import os
import requests


def build_csv():
    pass


def main():
    model_name = "355M"
    # dataset = "datasets/training_data.csv"
    dataset = "data/processed/training_data_march_17_2021.csv"
    run_name = "experiment_3_355M"
    # dataset = "./datasets/article.txt"
    if not os.path.isdir(os.path.join("models", model_name)):
        print(f"Downloading {model_name} model...")
        gpt2.download_gpt2(
            model_name=model_name
        )  # model is saved into current directory under /models/124M/

    sess = gpt2.start_tf_sess()
    gpt2.finetune(
        sess,
        dataset,
        restore_from="fresh",
        model_name=model_name,
        steps=1000,
        run_name=run_name,
        sample_length=1023,
        multi_gpu=False,
    )


if __name__ == "__main__":
    main()
