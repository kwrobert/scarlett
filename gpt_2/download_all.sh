#!/bin/bash

python gpt_2/download_docs.py -t ./private/gmail_token.json -c ./private/dlahoodbb_at_gmail_dot_com_creds.json -o /Users/kyle/projects/gpt-2/data/raw -f "Carpet One " -r "C[a-zA-Z0-9]+-[a-zA-Z0-9]+"
python gpt_2/download_docs.py -t ./private/carpetone_token.json -c ./private/dlahood_at_carpetone_dot_com_gmail_creds.json -o /Users/kyle/projects/gpt-2/data/raw -r "C[a-zA-Z0-9]+-[a-zA-Z0-9]+"
