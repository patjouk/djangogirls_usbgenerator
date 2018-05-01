import cgi
from collections import OrderedDict
import os
import re
import subprocess

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

import click
from lxml import html
from pyfiglet import figlet_format
import requests
from tqdm import tqdm


try:
    FileExistsError
except NameError:
    FileExistsError = Exception


BOOTSTRAP_DOWNLOAD_PAGE = 'https://getbootstrap.com/getting-started'
SUBLIME_DOWNLOAD_PAGE = 'https://www.sublimetext.com/2'
ATOM_DOWNLOAD_PAGE = 'https://github.com/atom/atom/releases/latest'
ATOM_DOWLOAD_URL = 'https://github.com/atom/atom/releases/download/v{version}/{platform}'
TUTORIAL_DOWNLOAD_PAGE = 'https://www.gitbook.com/download/pdf/book/djangogirls/djangogirls-tutorial'


def parse_url(*args, **kwargs):
    """
    A tiny utility function that passes all its arguments to `requests.get()`
    then parses the resulting HTML with lxml.
    """
    response = requests.get(*args, **kwargs)
    response.raise_for_status()
    return html.fromstring(response.text)


def introduction():
    print(figlet_format('Django Girls'))
    print("""This script will help you to download everything you need for the workshop in case there is no Internet.
Valid answers for each step: yes, y, enter or no, n.
Enter q to quit.\n""")

def create_directory():
    try:
        os.mkdir("downloads")
    except FileExistsError:
        pass

def download_file(address, folder):
    """Function for downloading stuff"""
    create_directory()
    r = requests.get(address, stream=True)
    if "Content-Disposition" in r.headers:
        _, params = cgi.parse_header(r.headers["Content-Disposition"])
        name = params["filename"]
    else:
        name = address.split("/")[-1]
    content_length = r.headers.get('content-length')
    if content_length:
        total = int(content_length) // 1024 +1
    else:
        total = None
    download_file_path = os.path.join(folder, name)
    with open(download_file_path, "wb") as f:
        chunks = tqdm(r.iter_content(1024), total=total)
        for chunk in chunks:
            f.write(chunk)
            f.flush()


def yes_no(message, function):
    """Function to give user the choice to skip a step"""
    choice = click.prompt(message)
    if choice in ("yes", "y", ""):
        function()
    elif choice in ("no", "n"):
        print("Ok, let's move to the next step!")
    elif choice in ("q"):
        print("Goodbye :)")
        exit()
    else:
        yes_no("I didn't understand your answer. Please, enter yes or no:", function)



def tutorial():
    """Gitbook made their page difficult to parse :'(. Hardcoding links to tutorial pdf while working on a better solution."""
    url = "https://www.gitbook.com/download/pdf/book/djangogirls/djangogirls-tutorial?lang="
    languages = {"cs": "Czech", "en": "English", "es": "Spanish", "fr": "French", "hu": "Hungarian", "it": "Italian", "ko": "Korean", "pl": "Polish", "pt": "Portuguese", "ru": "Russian", "sk": "Slovak", "tr": "Turkish", "uk": "Ukrainian", "zh": "Chinese"}
    print("Translations available:")
    print(", ".join("%s: %s" %(k, v) for k, v in sorted(languages.items())))
    print("Please, enter your choice (2 letters language code). If multiple choices, use space as a separator.")
    while True:
         choice = click.prompt('').split()
         if all(i in languages for i in choice):
             break
         else:
             print("2 letters code not recognized. Choose again in this list: %s" % ', '.join(languages))

    for lang in choice:
        lang_name = languages[lang]
        download_file(url + lang, "downloads/")
        print("%s tutorial downloaded" % lang_name)


def bootstrap():
    """
    Download Bootstrap

    Works by scraping the bootstrap download page which has some HTML that looks
    somewhat like this:

        <div>
            <h3 id="download-bootstrap">...</h3>
            ...
            <p>
                <a href="...">...</a>
            </p>
        </div>
"""
    parsed = parse_url(BOOTSTRAP_DOWNLOAD_PAGE)
    header = parsed.get_element_by_id('download-bootstrap')
    anchor = header.getparent().xpath('.//a')[0]
    link = anchor.attrib['href']
    print(link)
    download_file(link, "downloads/")
    print("Bootstrap downloaded.")


def lobster():
    download_file("http://dl.dafont.com/dl/?f=lobster", "downloads/")
    print("Lobster font downloaded.")


def python():
    download_file("https://www.python.org/ftp/python/3.5.2/python-3.5.2.exe", "downloads/")
    print("Python for Windows 32bits downloaded.")
    download_file("https://www.python.org/ftp/python/3.5.2/python-3.5.2-amd64.exe", "downloads/")
    print("Python for Windows 64bits downloaded.")
    download_file("https://www.python.org/ftp/python/3.5.2/python-3.5.2-macosx10.6.pkg", "downloads/")
    print("Python for Mac downloaded.")


def django():
    create_directory()
    subprocess.check_call(['pip', 'download', 'django~=1.11', '-d', 'downloads'])
    print("Django downloaded.")


def code_editors():
    yes_no("Do you want to download Sublime Text 2?", sublime_text)
    yes_no("Do you want to download Atom (64bits)?", atom)


def sublime_text():
    """
    Download multiple code editor

    Sublime's download page looks somewhat like this:
        <ul id="dl">
            <li id="dl_osx"><a href="...">OS X</a></li>
            <li id="dl_win_32">...</li>
            ...
        </ul>
    """
    PLATFORM_IDS = {
        'dl_osx': 'Mac',
        'dl_win_32': 'Windows (32 bits)',
        'dl_win_64': 'Windows (64 bits)',
        'dl_linux_32': 'Linux (32 bits)',
        'dl_linux_64': 'Linux (64 bits)',
    }
    parsed = parse_url(SUBLIME_DOWNLOAD_PAGE)

    for platform_id, platform_name in PLATFORM_IDS.items():
        element = parsed.get_element_by_id(platform_id)
        anchor = element.find('a')
        url = anchor.attrib['href']
        download_file(url, 'downloads/')
        print("Sublime Text 2 for %s downloaded." % platform_name)


def atom():
    """
    Download multiple code editor

    The download URL for a given platform is predictable provided you know
    which version you want.
    To determine the version, we hit ATOM_DOWNLOAD_PAGE which is a 302 redirect
    to a URL that contains the latest version. We match that URL against a
    regex to check it looks like what we're expecting and to extract the version
    number.
"""
    RELEASES = {
        'AtomSetup.exe': 'Windows',
        'atom-mac.zip': 'Mac',
        'atom-mac-symbols.zip': 'Mac (symbols)',
        'atom.x86_64.rpm': 'Fedora',
        'atom-amd64.deb': 'Debian/Ubuntu',
    }
    RELEASE_URL_RE = r'^https://github\.com/atom/atom/releases/tag/v(?P<version>[0-9.]+)$'

    response = requests.head(ATOM_DOWNLOAD_PAGE)
    assert response.status_code == 302
    redirect_url = response.headers['location']
    match = re.search(RELEASE_URL_RE, redirect_url)
    assert match is not None
    latest_version = match.group('version')

    for platform_filename, platform_name in RELEASES.items():
        url = ATOM_DOWLOAD_URL.format(version=latest_version, platform=platform_filename)
        download_file(url, 'downloads/')
        print("Atom for %s downloaded." % platform_name)


OPERATIONS = OrderedDict([
    ("the tutorial", tutorial),
    ("Bootstrap", bootstrap),
    ("Lobster font", lobster),
    ("Python", python),
    ("Django", django),
    ("code editors", code_editors),
])


@click.command()
@click.option("--all", is_flag=True, help="Download everything but still prompts for tutorial languages.")
def download_steps(all):
    """Launch the different downloading function"""
    introduction()
    if all:
        do_it = lambda _, function: function()
    else:
        do_it = yes_no

    for label, fn in OPERATIONS.items():
        do_it("Do you want to download %s?" % label, fn)

if __name__ == '__main__':
    download_steps()
