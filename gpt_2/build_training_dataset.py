import csv
import argparse
import pathlib

SCRIPT_DIR = pathlib.Path(__file__).parent.absolute()
DEFAULT_PROCESSED_DIR = SCRIPT_DIR.joinpath("..", "data", "processed")
DEFAULT_DATA_DIR = SCRIPT_DIR.joinpath("..", "data", "raw")


def create_training_text_body(labels, data_dir):
    rawpath = data_dir.joinpath(f"{labels['file_name']}.txt")
    print("rawpath = {}".format(rawpath))
    body = rawpath.read_text()
    fulltext = ""
    fulltext += "[LABELS]\n\n"
    for k, v in labels.items():
        if k == "file_name":
            continue
        fulltext += f"{k}: {v}\n"
        fulltext += "\n"
    fulltext += "[BODY]\n\n"
    fulltext += body
    return fulltext


def main():
    parser = argparse.ArgumentParser(description="""""")
    parser.add_argument(
        "-c", "--label-csv", required=True, help="""CSV file containing label data"""
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default=DEFAULT_PROCESSED_DIR,
        help="""Output directory for training data files""",
    )
    parser.add_argument(
        "-d",
        "--data-dir",
        type=str,
        default=DEFAULT_DATA_DIR,
        help="Path to directory containing raw downloaded data",
    )
    parser.add_argument(
        "-t",
        "--training-csv",
        type=str,
        default=DEFAULT_PROCESSED_DIR.joinpath("training_data.csv"),
        help="Destination CSV file for training",
    )
    args = parser.parse_args()

    fieldnames = [
        "file_name",
        "title",
        "store_name",
        "store_location",
        "page_template",
        "keywords",
    ]

    with open(args.label_csv, "r") as labelcsv:
        with open(args.training_csv, "w") as traincsv:
            traincsv.write("# data\n")
            reader = csv.DictReader(labelcsv, fieldnames=fieldnames)
            writer = csv.writer(traincsv)
            next(reader)
            for row in reader:
                print(row)
                outpath = pathlib.Path(args.output_dir).joinpath(
                    f"{row['file_name']}.txt"
                )
                training_body = create_training_text_body(
                    row, pathlib.Path(args.data_dir)
                )
                outpath.write_text(training_body)
                writer.writerow([training_body])


if __name__ == "__main__":
    main()
