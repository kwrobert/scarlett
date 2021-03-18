import csv
import pathlib
import argparse
import re
import pprint
import geograpy
import nltk
from nltk import pos_tag, ne_chunk
from nltk.tokenize import SpaceTokenizer


SCRIPT_DIR = pathlib.Path(__file__).parent.absolute()
DEFAULT_DATA_DIR = SCRIPT_DIR.joinpath("..", "data", "raw")
DEFAULT_EXT_DIR = SCRIPT_DIR.joinpath("..", "data", "external")
DEFAULT_KEYWORDS_DIR = SCRIPT_DIR.joinpath("..", "data", "interim", "keyword_corpus")


def get_title_word_histogram(names):
    hist = {}
    for name in names:
        cleaned_name = " ".join(name.split(" ")[1:])
        words = cleaned_name.split()
        print("words = {}".format(words))
        for w in words:
            if w in hist:
                hist[w] += 1
            else:
                hist[w] = 1
    return hist


def extract_store_name_and_page_template_from_title(name):
    # Remove serial number
    cleaned_name = name
    page_template = ""
    page_modfifiers = (
        "MULTI-MAIN",
        "MULTI-ADDON",
        "MULTI-LOC",
        "MULTI SINGLE",
        "MULTI",
    )
    for page_modifier in page_modfifiers:
        if page_modifier in name:
            page_template = page_modifier
            cleaned_name = cleaned_name.replace(page_modifier, "")
            break
    possible_store_suffixes = (
        "Carpet One Floor & Home - Asheville",
        "Carpet One Floor & Home of Billings",
        "Carpet One Floor & Home",
        "Carpet One Belleville",
        "Rochester Flooring",
        "Nice Carpets",
        "Fox Floors",
        "Northeast Flooring and Kitchens",
        "Carpet & Flooring",
        "Carpet One & Paint",
        "Flooring & Kitchens",
        "Carpet One",
        "Carpet",
    )
    store_suffix = ""
    for possible_suffix in possible_store_suffixes:
        index = cleaned_name.find(possible_suffix)
        if index >= 0:
            store_suffix = possible_suffix
            break

    store_name = cleaned_name[0:index].strip() + " " + store_suffix
    page_template = page_template + cleaned_name[index + len(store_suffix) :]
    return store_name.strip(), page_template.strip()


def get_page_title_from_path(path):
    name = path.with_suffix("").name
    return " ".join(name.split(" ")[1:])


def write_csv(files, outfile, keyword_corpus):
    # titles = [get_page_title_from_path(p) for p in files]
    print("Extracting store locations, this could take awhile ...")
    # locations = [extract_store_location(t, p.read_text()) for (t, p) in zip(titles,
    #     files)]
    fieldnames = [
        "file_name",
        "title",
        "store_name",
        "store_location",
        "page_template",
        "keywords",
    ]
    # print(len(files))
    # print(len(titles))
    # print(len(locations))
    with open(outfile, "w") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for path in files:
            print("-"*25)
            print(f"Loading {path} ...")
            body = path.read_text()
            print("Extracting title ...")
            title = get_page_title_from_path(path)
            print("Extracting store location ...")
            location = extract_store_location(title, body)
        # for path, title, location in zip(files, titles, locations):
            (
                store_name,
                page_template,
            ) = extract_store_name_and_page_template_from_title(title)
            print("Matching keywords ...")
            keywords = get_keywords_in_body(keyword_corpus, body) 
            keyword_str = ":".join(keywords)
            writer.writerow(
                {
                    "file_name": path.with_suffix("").name,
                    "title": title,
                    "store_name": store_name,
                    "store_location": location,
                    "page_template": page_template,
                    "keywords": keyword_str
                }
            )

def extract_entity_names(t):
    entity_names = []

    if hasattr(t, 'label') and t.label:
        if t.label() == 'NE':
            entity_names.append(' '.join([child[0] for child in t]))
        else:
            for child in t:
                entity_names.extend(extract_entity_names(child))

    return entity_names

def get_keywords_in_body(corpus, body):
    keywords = []
    for keyword in corpus:
        klower = keyword.lower() 
        if klower in keywords:
            continue
        if klower in body.lower():
            keywords.append(klower)
    return keywords

def load_keyword_corpus(folder):
    files = pathlib.Path(folder).glob("**/*.txt")

    corpus = []
    for f in files:
        for line in f.read_text().splitlines():
            if line:
                corpus.append(line)
    return corpus


def extract_store_location(title, body):
    # First try to grab it from the title
    compiled_re = re.compile('\([\w ]+\)')
    match = re.search(compiled_re, title)
    location = ''
    if match is not None:
        location += match.group(0).strip('()')
        location += " "
    # If that didn't work we need to search the body
    # capital_words = re.findall('([A-Z][a-z]+)', body)
    # print("capital_words = {}".format(capital_words))
    places = geograpy.get_geoPlace_context(text=body)
    # for attr in ("countries", "regions", "cities", "other", "country_regions",
    #         "country_cities", "address_strings"):
    #     print(f"places.{attr}")
    #     pprint.pprint(getattr(places, attr))
    allowed_countries = {"Canada", "United States"}
    all_locs = []
    for attr in ('country_regions', 'country_cities'):
        for k, v in getattr(places, attr).items():
            if k not in allowed_countries: 
                continue
            for subloc in v:
                all_locs.append(f"{subloc} {k}")
    location += ",".join(all_locs)
    print("location = {}".format(location))
    # all_cities = ' '.join(places.cities).strip()
    # all_regions = ' '.join(places.regions).strip()
    # all_countries = ' '.join(places.countries).strip()
    # location += f"{all_cities} {all_regions} {all_countries}"

    # print("propernouns:")
    # pprint.pprint(propernouns)

    # tokenizer = SpaceTokenizer()
    # toks = tokenizer.tokenize(body)
    # pos = pos_tag(toks)
    # chunked_nes = ne_chunk(pos) 

    # nes = set(' '.join(map(lambda x: x[0], ne.leaves())) for ne in chunked_nes if isinstance(ne, nltk.tree.Tree))
    # print("nes:")
    # pprint.pprint(nes)
    # entities = []
    # sentences = nltk.sent_tokenize(body)
    # tokenized_sentences = [nltk.word_tokenize(sentence) for sentence in sentences]
    # tagged_sentences = [nltk.pos_tag(sentence) for sentence in tokenized_sentences]
    # chunked_sentences = nltk.ne_chunk_sents(tagged_sentences, binary=True)

    # for tree in chunked_sentences:
    #     entities.extend(extract_entity_names(tree))
    # print("entities:")
    # pprint.pprint(entities)
    # print("common:")
    # common = nes & propernouns
    # print(common)
    return location 


def main():
    parser = argparse.ArgumentParser(description="Download utility for Google Docs")
    parser.add_argument(
        "-d",
        "--data-dir",
        type=str,
        default=DEFAULT_DATA_DIR,
        help="Path to directory containing raw downloaded data",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        default=DEFAULT_EXT_DIR,
        help="Path to directory for output CSV",
    )
    parser.add_argument(
        "-k",
        "--keyword-corpus",
        type=str,
        default=DEFAULT_KEYWORDS_DIR,
        help="Path to directory containing text files of keywords and phrases",
    )
    args = parser.parse_args()
    files = list(pathlib.Path(args.data_dir).glob("*.txt"))
    out_path = pathlib.Path(args.output_dir).joinpath("metadata.csv")
    # hist = get_title_word_histogram(names)
    # pprint.pprint(hist)
    keyword_corpus = load_keyword_corpus(args.keyword_corpus)
    write_csv(files, out_path, keyword_corpus)


if __name__ == "__main__":
    main()
