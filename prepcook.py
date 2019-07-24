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

from apiclient import discovery
from httplib2 import Http
from oauth2client import client
from oauth2client import file
from oauth2client import tools

import click

import googleapiclient

SCOPES = 'https://www.googleapis.com/auth/documents.readonly'
DISCOVERY_DOC = 'https://docs.googleapis.com/$discovery/rest?version=v1'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth 2.0 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    store = file.Storage('token.json')
    credentials = store.get()

    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        credentials = tools.run_flow(flow, store)
    return credentials

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
                # Our header is finished with a ----- line, so we just keep reading until we find that.
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

    file_handler = open("solr_output.txt", "w")
    for key in results:
        flattend_values = ",".join(results[key])
        file_handler.write(f"{key},{flattend_values}\n")
    file_handler.close()

    click.echo(f"☀️   Solr synonyms saved in {file_name}")


@click.command()
@click.option('--id', prompt='Document ID',
              help='Get this from the URL of the document.')
@click.option('--solr', default='solr_output.txt', help='The name of the Solr output file')
def main(id, solr):
    """Uses the Docs API to print out the text of a document."""
    credentials = get_credentials()
    http = credentials.authorize(Http())
    docs_service = discovery.build(
        'docs', 'v1', http=http, discoveryServiceUrl=DISCOVERY_DOC)

    try:
        doc = docs_service.documents().get(documentId=id).execute()
    except googleapiclient.errors.HttpError as error:
        click.echo("Error fetching document. You probably have the wrong document ID or you don't have access it.")
        click.echo(error)
        exit()

    doc_content = doc.get('body').get('content')
    results = parse_document(doc_content)
    format_for_solr(results, solr)

if __name__ == '__main__':
    main()