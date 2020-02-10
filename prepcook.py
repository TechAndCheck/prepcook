# Currently modified from https://developers.google.com/docs/api/quickstart/python?authuser=1
#
# prepcook.py
# Author: Christopher Guess @cguess - 2019-07-24
#
# Borrowed in parts from https://developers.google.com/docs/api/samples/extract-text?authuser=1

"""
Recursively extracts the text from a Google Doc.
"""
from __future__ import print_function

import pdb
import pickle
import os.path
import googleapiclient
import click

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/documents.readonly']
DISCOVERY_DOC = 'https://docs.googleapis.com/$discovery/rest?version=v1'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth 2.0 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return creds


def read_paragraph_element(element):
    """Returns the text in the given ParagraphElement.

        Args:
            element: a ParagraphElement from a Google Doc.
    """
    text_run = element.get('textRun')

    if not text_run:
        return None
    return text_run.get('content').rstrip()



def parse_document(elements):
    """Recurses through a list of Structural Elements to read a document's text where text may be
        in nested elements.

        Args:
            elements: a list of Structural Elements.
    """

    results = {}
    current_headword = None
    passed_header = False

    for value in elements:
        if 'paragraph' in value:
            paragraph_style = value.get('paragraph').get('paragraphStyle').get('namedStyleType')
            text = ''

            # Go through all elements in the document
            for elem in value.get('paragraph').get('elements'):
                # Read the current paragraph element
                text_line = read_paragraph_element(elem)
                # Our header is finished with a ----- line,
                # so we just keep reading until we find that.
                if passed_header is False:
                    if text_line == '-----':
                        passed_header = True
                    continue

                # If a line starts with '#' we'll consider it a comment
                if text_line.rstrip() and not text_line.startswith("#"):
                    text += text_line

            # If a string is empty or a comment, we skip it
            if not text.rstrip() or text_line.startswith("#"):
                continue


            # If the paragraph style is HEADING_2 we replace the headword we're looking at
            if paragraph_style == "HEADING_2":
                current_headword = text
            else:
                # Else we set the headword to the synonym.
                results[current_headword] = [x.lstrip().rstrip() for x in text.split(",")]

    return results


def format_for_solr(results, file_name="solr_output.txt"):
    """Formats results for Solr's synonyms and saves it to the indicated filename.

        Args:
            results: A dictionary of elements parsed from the Google Doc.
            file_name: The name of the file to save.
    """

    file_handler = open(file_name, "w")
    for key in results:
        flattend_values = ",".join(results[key])
        file_handler.write(f"{key},{flattend_values}\n")
    file_handler.close()

    click.echo(f"☀️   Solr synonyms saved in {file_name}")



def format_for_chewy(results, file_name="chewy_output.txt"):
    """Formats results for the Chewy Ruby gem synonyms and saves it to the
    indicated filename.

        Args:
            results: A dictionary of elements parsed from the Google Doc.
            file_name: The name of the file to save.
    """
    flattend_values = []
    for key in results:
        merged_synonyms = ",".join(results[key])
        flattend_values.append(f"\"{key},{merged_synonyms}\"")

    final_values = ",\n".join(flattend_values)

    file_handler = open(file_name, "w")
    file_handler.write(f"[\n{final_values}\n]")
    file_handler.close()

    click.echo(f"🐻    Chewy synonyms saved in {file_name}")



@click.command()
@click.option('--docid', prompt='Document ID',
              help='Get this from the URL of the document.')
@click.option('--solr', default='solr_output.txt', help='The name of the Solr output file')
@click.option('--chewy', default='chewy_output.txt', help='The name of the Chewy output file')
def main(docid=None, solr=None, chewy=None):
    """Uses the Docs API to print out the text of a document."""
    credentials = get_credentials()

    docs_service = build('docs', 'v1', credentials=credentials)

    try:
        doc = docs_service.documents().get(documentId=docid).execute()
    except googleapiclient.errors.HttpError as error:
        click.echo("Error fetching document. You probably have the wrong document ID or you don't have access it.")
        click.echo(error)
        exit()

    doc_content = doc.get('body').get('content')
    results = parse_document(doc_content)
    format_for_solr(results, solr)
    format_for_chewy(results, chewy)

if __name__ == '__main__':
    main()
