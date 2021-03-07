import os.path
import pprint
import csv
import re
import argparse
import pathlib

from googleapiclient import errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/documents",
    "https://www.googleapis.com/auth/drive.readonly",
]

SCRIPT_DIR = pathlib.Path(__file__).parent.absolute()
DEFAULT_DATA_DIR = SCRIPT_DIR.joinpath( "..", "data", "raw")


def read_paragraph_element(element):
    """Returns the text in the given ParagraphElement.

    Args:
        element: a ParagraphElement from a Google Doc.
    """
    text_run = element.get("textRun")
    if not text_run:
        return ""
    return text_run.get("content")


def read_structural_elements(elements):
    """Recurses through a list of Structural Elements to read a document's text where text may be
    in nested elements.

    Args:
        elements: a list of Structural Elements.
    """
    text = ""
    for value in elements:
        if "paragraph" in value:
            elements = value.get("paragraph").get("elements")
            for elem in elements:
                text += read_paragraph_element(elem)
        elif "table" in value:
            # The text in table cells are in nested Structural Elements and tables may be
            # nested.
            table = value.get("table")
            for row in table.get("tableRows"):
                cells = row.get("tableCells")
                for cell in cells:
                    text += read_structural_elements(cell.get("content"))
        elif "tableOfContents" in value:
            # The text in the TOC is also in a Structural Element.
            toc = value.get("tableOfContents")
            text += read_structural_elements(toc.get("content"))
    return text


def get_google_drive_folders(service):
    all_files = dict()
    page_token = None
    while True:
        # print("page_token = {}".format(page_token))
        response = (
            service.files()
            .list(
                q="mimeType = 'application/vnd.google-apps.folder'",
                pageSize=10,
                fields="nextPageToken, files(id, name)",
                pageToken=page_token,
            )
            .execute()
        )
        for f in response.get("files", []):
            # Process change
            # print("Found file: %s (%s)" % (f.get("name"), f.get("id")))
            all_files[f.get("name")] = f
        page_token = response.get("nextPageToken", None)
        if page_token is None:
            break
    return all_files


def get_google_drive_files(service, folder_id='', regex='', prefix=''):
    """
    Get file objects from Google Drive API with optional filters

    Parameters
    ----------
    service : 
        Drive API service instance
    folder : str
        Folder ID of folder to restrict list of files to
    regex : str
        A regex that must be contained within the file name
    prefix : str
        A prefix that must match the beginning of the file name
    """
    if regex:
        compiled_re = re.compile(regex)
        has_regex = lambda name: re.search(compiled_re, name) is not None
    else:
        has_regex = lambda name: True
    query = "mimeType != 'application/vnd.google-apps.folder'"
    if folder_id:
        query += f" and '{folder_id}' in parents"
    if prefix:
        query += f"  and name contains '{prefix}'"
    page_token = None
    files = {}
    while True:
        try:
            param = {
                "q": query,
                "fields": "nextPageToken, files(id, name)",
            }
            if page_token:
                param["pageToken"] = page_token
            response = service.files().list(**param).execute()
            for f in response.get("files", []):
                # print("File Id: %s" % child["id"])
                if not has_regex(f.get('name')):
                    continue
                files[f.get("name")] = f
            page_token = response.get("nextPageToken")
            if page_token is None:
                break
        except errors.HttpError as error:
            print("An error occurred: %s" % error)
            break
    return files


def get_creds(creds_path, token_path):
    # creds_file = "dlahoodbb_at_gmail_dot_com_creds.json"
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, "w") as token:
            token.write(creds.to_json())
    return creds


def write_csv(files):
    fieldnames = [
        "file_name",
        "file_id",
        "store_name",
        "store_location",
        "page_template",
    ]
    with open("flooring_pages.csv", "a") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for name, f in files.items():
            if name[0] != "C":
                print(f"Skipping file name: {name}")
                continue
            print("-" * 25)
            print(f"File Name: {f['name']}")
            print(f"File ID: {f['id']}")
            data = {"file_name": f["name"], "file_id": f["id"]}
            writer.writerow(data)


def download_files(docs, files, out_dir):
    for name, f in files.items():
        print("-" * 25)
        try:
            doc = docs.documents().get(documentId=f["id"]).execute()
        except Exception as e:
            print(f"Could not retrieve document {name}")
            print("Exception raised:")
            print(e)
            continue
        print(f"Downloading document: {doc['title']}")
        doc_content = doc.get('body').get('content')
        body = read_structural_elements(doc_content)
        fname = f"{name}.txt".replace("/", "")
        out_path = pathlib.Path(out_dir).joinpath(fname)
        with open(out_path, 'w') as out_f:
            out_f.write(body)


def main():

    parser = argparse.ArgumentParser(description="Download utility for Google Docs")
    parser.add_argument('-t', '--token', required=True, type=str, help="Path to API token JSON file")
    parser.add_argument('-c', '--credentials', required=True, type=str, help="Path to API credentials JSON file")
    parser.add_argument('-o', '--output-dir', type=str, default=DEFAULT_DATA_DIR, help="Path to directory for downloading data")
    parser.add_argument('-f', '--folder', type=str, default='', help="Google Docs folder to pull data from")
    parser.add_argument('-r', '--regex', type=str, default='', help="Regex that must match any part of the downloaded file names")
    parser.add_argument('-s', '--skip', action='store_true', default=False, help="Skip file  names that have already been downloaded")
    args = parser.parse_args()

    p = pathlib.Path(args.output_dir).glob('*.txt')
    existing_files = set(x.with_suffix('').name for x in p if x.is_file())
    for arg in (args.token, args.credentials):
        if not os.path.isfile(arg):
            raise ValueError("Argument {arg} is not a valid path")
    creds = get_creds(args.credentials, args.token)
    drive = build("drive", "v3", credentials=creds)
    docs = build("docs", "v1", credentials=creds)

    folder_id = ''
    if args.folder:
        print("Retrieving all folders ...")
        folders = get_google_drive_folders(drive)
        folder_id = folders[args.folder]["id"]

    print("Getting files ...")
    if args.regex:
        print(f"Files must match {args.regex}")
    if args.folder:
        print(f"Files must be in {args.folder}")
    files = get_google_drive_files(drive, folder_id=folder_id, regex=args.regex)
    print(f"Number of files found: {len(files)}")
    if args.skip:
        files = {k: v for k, v in files.items() if k not in existing_files}
    print(f"Number of files to download: {len(files)}")
    download_files(docs, files, args.output_dir)

    # # files = get_files_matching_prefix(drive, "C")
    # creds_file = "dlahood_at_carpetone_dot_com_gmail_creds.json"
    # creds = get_creds(creds_file, "carpetone_token.json")
    # drive = build("drive", "v3", credentials=creds)
    # docs = build("docs", "v1", credentials=creds)
    # # files.update(get_files_matching_regex(drive, "C[a-zA-Z0-9]+-[a-zA-Z0-9]+"))
    # files = get_files_matching_regex(drive, "C[a-zA-Z0-9]+-[a-zA-Z0-9]+")
    # file_names = list(files.keys())
    # # for k in files.keys():
    # #     print(k) 
    # print(f"Number of files: {len(file_names)}")


    # serial_re = re.compile("C[a-zA-Z0-9]+-[a-zA-Z0-9]+")
    # with open("training_data.csv", "a") as csvfile:
    #     writer = csv.writer(csvfile)
    #     for name, f in files.items():
    #         print("-" * 25)
    #         try:
    #             doc = docs.documents().get(documentId=f["id"]).execute()
    #         except Exception as e:
    #             print(f"Could not retrieve document {f['name']}")
    #             print("Exception raised:")
    #             print(e)
    #             continue
    #         print(f"Document: {doc['title']}")
    #         # print("Body:")
    #         # print(doc["body"])
    #         doc_content = doc.get('body').get('content')
    #         body = read_structural_elements(doc_content)
    #         header = re.sub(serial_re, "", doc["title"]).lstrip()
    #         print("Header:")
    #         print(header)
    #         full_text = header + '\n' + body
    #         writer.writerow([full_text])
    #         # text = name + '\n' + f.get()

    # results = (
    #     drive.files()
    #     .list(pageSize=10, fields="nextPageToken, files(id, name)")
    #     .execute()
    # )
    # print(dir(results))
    # items = results.get("files", [])
    # print(dir(results))
    # print(results.keys())

    # if not items:
    #     print("No files found.")
    # else:
    #     print("Files:")
    #     for item in items:
    #         print(u"{0} ({1})".format(item["name"], item["id"]))

    # Retrieve the documents contents from the Docs service.
    # document = service.documents().get(documentId=DOCUMENT_ID).execute()
    # documents = docs.documents()
    # print(documents)
    # print(dir(documents))

    # print('The title of the document is: {}'.format(document.get('title')))


if __name__ == "__main__":
    main()
