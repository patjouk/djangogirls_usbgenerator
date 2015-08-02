import requests
import re
import os


def download_file(address, filename):
    """Generic function for downloading stuff"""
    r = requests.get(address, stream=True)
    with open(filename, "wb") as f:
        for chunk in r.iter_content(1024):
            if chunk:
                f.write(chunk)
                f.flush()


def download_steps():
    print("First step: tutorial!")
    tutorial()
    print("Second step: Bootstrap!")
    bootstrap()


def list_tutorial_languages():
    """Create a list with all the languages available for the tutorial"""
    r = requests.get("https://www.gitbook.com/download/pdf/book/djangogirls/djangogirls-tutorial")
    tutorials = re.findall(r"\?lang=(.{2})\">([^<]*)<", r.text)
    return dict(tutorials)


def tutorial():
    """Download tutorial, multiple languages possible"""
    try:
        os.mkdir("downloads")
    except FileExistsError:
        pass
    tutorials = list_tutorial_languages()
    print("Translations available %s. \nPlease, enter your choice (2 letters language code). If multiple choices, use space as a separator." %tutorials)
    while True:
        choice = input().split()
        if all(i in tutorials for i in choice):
            break
        else:
            print("2 letters code not recognized. Choose again in this list: %s" %tutorials)
    for i in choice:
        download_file("https://www.gitbook.com/download/pdf/book/djangogirls/djangogirls-tutorial?lang=%s" %i, "downloads/tutorial_%s.pdf" %i)
        print("%s tutorial downloaded" %tutorials[i])


def bootstrap():
    """Download Bootstrap"""
    try:
        os.mkdir("downloads")
    except FileExistsError:
        pass
    r = requests.get("http://getbootstrap.com/getting-started")
    m = re.search(r'<a href="([^"]*)"[^>]*>Download Bootstrap</a>', r.text)
    if m:
        link = m.group(1)
        download_file(link, "downloads/bootstrap.zip")
        print("Bootstrap downloaded.")
    else:
        print("Failed to find download URL for Bootstrap.")


if __name__ == '__main__':
    download_steps()
