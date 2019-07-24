# Prepcook
A simple script that preps a synonyms list for Solr (and other matchers)

## Setup

This repo includes an Anaconda environment file, along with a requirements.py. I'd suggest the former, but if you want to just go for the latter that's on you.

### File Format

This expects a Google Doc with the following format (just copy and paste this in as the header of a new document)

```
This document is to allow a collaborative curation of synonyms used in our search algorithms. Nicknames, deferential titles, etc. should be added to this as they emerge or we think of them.

Please label the headword in “Heading 2”, followed by a newline (do not put a blank line after the headword), followed by the synonyms separated by commas, followed by a newline (again, do not put a blank line yourself afterwards). Please keep everything in lower case with no punctuation.

-----
```

### Anaconda

1. Clone this repo ```$ https://github.com/TechAndCheck/prepcook.git```
1. Install [Anaconda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) (I prefer [Miniconda](https://docs.conda.io/en/latest/miniconda.html) since it has less packages)
1. Create the Anaconda environment by running the following in a terminal in your repo folder (this takes awhile sometimes) ```$ conda env create --file environment.yml```

### Google Docs

1. Go to the [Google Developer Console](https://console.developers.google.com/) and create a new project.
1. Then go to the [Google Docs API](https://console.developers.google.com/apis/library/docs.googleapis.com)
1. Click "Enable"
1. This should take you back to the home page with a banner at the top and a button on the far right saying "CREATE CREDENTIALS", click that. (If you don't see it, you can go to "Credentials" on the left side.)
1. In the drop down for "Which API are you using?" select "Google Docs API"
1. In the "Where will you be calling this API from?" select "Other UI"
1. In "What data will you be accessing?" select "User data"
1. Configure the consent screen by typing in a name, I use "Prep Cook"
1. When you're configuring everything make sure you add the Google Doc API scopes `../auth/drive.file `
1. Create an OAuth credential, selecting "Other" for client type and name it CLI (or whatever)
1. Click "OK" after it's created.
1. Download the credentials file by click the down arrow on the new credentials line.
1. Then click the "Download Client Configuration" button and save the file to this repo. (**DO NOT CHECK THIS IN IF YOU'RE MODIFYING ANY CODE**)
1. Rename the file to `credentials.json`

### Running

1. Get the document ID from [Chris](@cguess)
1. Run the command `python prepcook.py --id <DOCUMENT_ID>`

### Requirements

- Python 3
- Pip

This has been tested on MacOS, and should work just fine on Linux. Windows is up in the air.

## Contributing

The main thing is that this uses Pylint and has a .pylintrc configuration file in the repository

It also contains an Anaconda setup, so if you use that you can do `conda install --file environment.yml` and it'll all be setup.

If you use just normal Pip then `pip install -r requirements.txt` will do the trick

## Author

**Christopher Guess**
_[@cguess](https://www.twitter.com/cguess)_

Lead Technologist
Duke Reporters' Lab
Duke University
[christopher.guess@duke.edu](mailto:christopher.guess@duke.edu)
