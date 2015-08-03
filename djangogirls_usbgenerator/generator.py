import requests
import re
import os
import cgi

def download_steps():
    """Launch the different downloading function"""
    print("First step: tutorial!\nDo you want to download it? Enter yes or no:")
    yes_no(tutorial)
    print("Second step: Bootstrap!\nDo you want to download it? Enter yes or no:")
    yes_no(bootstrap)
    print("You're done! Bye :)")


def download_file(address, folder):
    """Function for downloading stuff"""
    r = requests.get(address, stream=True)
    _, params = cgi.parse_header(r.headers["Content-Disposition"])
    name = params["filename"]
    with open(folder+"/"+name, "wb") as f:
        for chunk in r.iter_content(1024):
            if chunk:
                f.write(chunk)
                f.flush()


def yes_no(function):
    """Function to give user the choice to skip a step"""
    choice = input()
    if choice in ("yes", "y"):
        function()
    elif choice in ("no", "n"):
        print("Ok, let's move to the next step!")
    else:
        print("I didn't understand your answer. Please, enter enter yes or no:")
        yes_no(function)


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
        download_file("https://www.gitbook.com/download/pdf/book/djangogirls/djangogirls-tutorial?lang=%s" %i, "downloads/")
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
        download_file(link, "downloads/")
        print("Bootstrap downloaded.")
    else:
        print("Failed to find download URL for Bootstrap. Falling back to hardcoded download link.")
        download_file("https://github.com/twbs/bootstrap/releases/download/v3.3.5/bootstrap-3.3.5-dist.zip", "downloads/")


if __name__ == '__main__':
    download_steps()
