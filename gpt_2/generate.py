import os
import pathlib
import argparse
import csv
from datetime import datetime
import gpt_2_simple as gpt2

SCRIPT_DIR = pathlib.Path(__file__).parent.absolute()
DEFAULT_RESULTS_DIR = SCRIPT_DIR.joinpath("..", "data", "raw")


def generate_prompts_from_csv(path):
    path = pathlib.Path(path)
    prompts = []
    with open(path, "r", encoding='utf-8-sig') as f:
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


def main():
    parser = argparse.ArgumentParser(description="""""")
    parser.add_argument(
        "-m",
        "--model-name",
        required=True,
        help="""Name of finetuned model run to use for generation""",
    )
    parser.add_argument("-c", "--csv", help="""Path to CSV with prompt metadata""")
    parser.add_argument(
        "-o",
        "--output-dir",
        default=DEFAULT_RESULTS_DIR,
        help="""Directory to save generated samples to""",
    )
    args = parser.parse_args()

    prompts = generate_prompts_from_csv(args.csv)

    # gen_file = "generated_samples/gpt2_gentext_{:%Y%m%d_%H%M%S}.txt".format(
    #     datetime.utcnow()
    # )
    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess, run_name=args.model_name)
    # gpt2.generate(sess, run_name='first_test', prefix="Luxury Vinyl Plank Flooring")
    for fname, prefix in prompts:
        print(f"Saving samples for prefix {prefix} to {fname}")
        gen_file = os.path.join(args.output_dir, fname)
        gpt2.generate_to_file(
            sess,
            prefix=prefix,
            destination_path=gen_file,
            # length=500,
            temperature=0.7,
            nsamples=5,
            batch_size=1,
            run_name=args.model_name,
        )


if __name__ == "__main__":
    main()
