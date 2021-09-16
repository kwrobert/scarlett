import io
import os
import pathlib
import argparse
import csv
import gpt_2_simple as gpt2
import numpy as np

from datetime import datetime
from shutil import make_archive
from pydantic import BaseModel, Field

from opyrator.components.types import FileContent
from tempfile import NamedTemporaryFile, TemporaryDirectory


SCRIPT_DIR = pathlib.Path(__file__).parent.absolute()
DEFAULT_RESULTS_DIR = SCRIPT_DIR.joinpath("..", "data", "raw")
CHECKPOINT_DIR = SCRIPT_DIR.joinpath("..", "checkpoint")

class PromptCSVInput(BaseModel):
    csv_file: FileContent = Field(
        ..., description="Prompt file as a CSV", mime_type="text/csv"
    )


class GeneratedArticlesZipOutput(BaseModel):
    generated_articles: FileContent = Field(
        ...,
        mime_type="application/zip",
        description="ZIP archive containing text files of generated articles",
    )


def generate_prompts_from_csv(path):

    path = pathlib.Path(path)
    prompts = []
    with open(path, "r", encoding="utf-8-sig") as f:
        fieldnames = f.readline().lstrip("#").strip().split(",")
        print("fieldnames = {}".format(fieldnames))
        reader = csv.DictReader(f, fieldnames=fieldnames)
        for row in reader:
            if not any(v for v in row.values()):
                continue
            print("row = {}".format(row))
            prompt = f"""
[LABELS]

title: {row['title']}

store_name: {row['store_name']}

store_location: {row['store_location']}

page_template: {row['page_template']}

keywords: {row['keywords']}
"""
            prompts.append((row["file_name"], prompt))
    return prompts


def generate_prompts(
    input: PromptCSVInput,
) -> GeneratedArticlesZipOutput:
    """
    Given a CSV file of prompts, generate articles for each prompt
    """

    with NamedTemporaryFile(suffix=".csv", mode="w") as csv_file:
        csv_file.write(input.csv_file.as_str())
        csv_file.seek(0)
        print("CSV file name:")
        print(csv_file.name)
        prompts = generate_prompts_from_csv(csv_file.name)

    print("prompts:")
    print(prompts)

    # gpt2.generate(sess, run_name='first_test', prefix="Luxury Vinyl Plank Flooring")
    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess, run_name="experiment_3_355M", checkpoint_dir=CHECKPOINT_DIR)
    with TemporaryDirectory() as tmp_dir:
        for fname, prefix in prompts:
            fname += ".txt"
            print(f"Saving samples for prefix {prefix} to {fname}")
            articles_dir = os.path.join(tmp_dir, "articles") 
            if not os.path.isdir(articles_dir):
                os.makedirs(articles_dir)
            gen_file = os.path.join(articles_dir, fname)
            print("gen_file = {}".format(gen_file))
            gpt2.generate_to_file(
                sess,
                prefix=prefix,
                destination_path=gen_file,
                checkpoint_dir=CHECKPOINT_DIR,
                # length=500,
                temperature=0.7,
                nsamples=5,
                batch_size=1,
                run_name="experiment_3_355M",
            )
        zip_name = os.path.join(tmp_dir, "generated-articles") 
        print("zip_name = {}".format(zip_name))	
        zip_path = make_archive(
            zip_name,
            "zip",
            root_dir=tmp_dir,
            base_dir="articles",
        )
        print("zip_path = {}".format(zip_path))	
        with open(zip_path, 'rb') as f:
            zip_bytes = f.read()
        print("len(zip_bytes) = {}".format(len(zip_bytes)))
        return GeneratedArticlesZipOutput(generated_articles=zip_bytes) 
