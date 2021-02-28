import os.path
import pprint
import csv
import re

from googleapiclient import errors
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/documents.readonly",
    "https://www.googleapis.com/auth/drive.metadata.readonly",
]


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
                    text += read_strucutural_elements(cell.get("content"))
        elif "tableOfContents" in value:
            # The text in the TOC is also in a Structural Element.
            toc = value.get("tableOfContents")
            text += read_structural_elements(toc.get("content"))
    return text


def get_drive_folders(service):
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


def get_files_in_folder(service, folder_id):
    """Print files belonging to a folder.

    Args:
      service: Drive API service instance.
      folder_id: ID of the folder to print files from.
    """
    page_token = None
    files = {}
    while True:
        try:
            param = {
                "q": f"'{folder_id}' in parents",
                "fields": "nextPageToken, files(id, name)",
            }
            if page_token:
                param["pageToken"] = page_token
            response = service.files().list(**param).execute()
            for f in response.get("files", []):
                # print("File Id: %s" % child["id"])
                files[f.get("name")] = f
            page_token = response.get("nextPageToken")
            if page_token is None:
                break
        except errors.HttpError as error:
            print("An error occurred: %s" % error)
            break
    return files


def main():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    drive = build("drive", "v3", credentials=creds)
    docs = build("docs", "v1", credentials=creds)
    # Call the Drive v3 API
    print("Retrieving all folders ...")
    folders = get_drive_folders(drive)
    # for name, f in folders.items():
    #     print("-" * 25)
    #     print(f"Folder Name: {f['name']}")
    #     print(f"Folder ID: {f['id']}")
    pprint.pprint(folders.keys())
    print("Getting all files in folder ...")
    carpet_one_folder_id = folders["Carpet One "]["id"]
    files = get_files_in_folder(drive, carpet_one_folder_id)
    fieldnames = [
        "file_name",
        "file_id",
        "store_name",
        "store_location",
        "page_template",
    ]
    with open("flooring_pages.csv", "w") as csvfile:
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

    serial_re = re.compile("C[a-zA-Z0-9]+-[a-zA-Z0-9]+")
    with open("training_data.csv", "w") as csvfile:
        writer = csv.writer(csvfile)
        for name, f in files.items():
            print("-" * 25)
            try:
                doc = docs.documents().get(documentId=f["id"]).execute()
            except Exception as e:
                print(f"Could not retrieve document {f['name']}")
                print("Exception raised:")
                print(e)
                continue
            print(f"Document: {doc['title']}")
            # print("Body:")
            # print(doc["body"])
            doc_content = doc.get('body').get('content')
            body = read_structural_elements(doc_content)
            header = re.sub(serial_re, "", doc["title"]).lstrip()
            print("Header:")
            print(header)
            full_text = header + '\n' + body
            writer.writerow([full_text])
            # text = name + '\n' + f.get()

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
