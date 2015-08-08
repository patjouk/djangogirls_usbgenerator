import requests
import re
import os
import cgi
from clint.textui import progress
import subprocess


def download_steps():
    """Launch the different downloading function"""
    print("First step: tutorial!\nDo you want to download it? Enter yes or no:")
    yes_no(tutorial)
    print("Second step: Bootstrap!\nDo you want to download it? Enter yes or no:")
    yes_no(bootstrap)
    print("Third step: Django!\nDo you want to download it? Enter yes or no:")
    yes_no(django)
    print("Fourth step: code editor!\nDo you want to download it? Enter yes or no:")
    yes_no(code_editors)
    print("You're done! Bye :)")


def download_file(address, folder):
    """Function for downloading stuff"""
    try:
        os.mkdir("downloads")
    except FileExistsError:
        pass
    r = requests.get(address, stream=True)
    if "Content-Disposition" in r.headers:
        _, params = cgi.parse_header(r.headers["Content-Disposition"])
        name = params["filename"]
    else:
        name = address.split("/")[-1]
    total_length = int(r.headers.get('content-length'))
    with open(folder+"/"+name, "wb") as f:
        for chunk in progress.bar(r.iter_content(1024), expected_size=(total_length/1024) + 1):
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
        print("I didn't understand your answer. Please, enter yes or no:")
        yes_no(function)


def list_tutorial_languages():
    """Create a list with all the languages available for the tutorial"""
    r = requests.get("https://www.gitbook.com/download/pdf/book/djangogirls/djangogirls-tutorial")
    tutorials = re.findall(r"\?lang=(.{2})\">([^<]*)<", r.text)
    return dict(tutorials)


def tutorial():
    """Download tutorial, multiple languages possible"""
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
    r = requests.get("http://getbootstrap.com/getting-started")
    m = re.search(r'<a href="([^"]*)"[^>]*>Download Bootstrap</a>', r.text)
    if m:
        link = m.group(1)
        download_file(link, "downloads/")
        print("Bootstrap downloaded.")
    else:
        print("Failed to find download URL for Bootstrap. Falling back to hardcoded download link.")
        download_file("https://github.com/twbs/bootstrap/releases/download/v3.3.5/bootstrap-3.3.5-dist.zip", "downloads/")


def django():
    subprocess.check_call("pip install django==1.8 --download downloads", shell=True)
    print("Django downloaded.")


def code_editors():
    print("Do you want to download Sublime Text 2? Enter enter yes or no:")
    yes_no(sublime_text)
    print("Do you want to download Atom (64bits)? Enter enter yes or no:")
    yes_no(atom)


def sublime_text():
    """Download multiple code editor"""
    download_file("http://c758482.r82.cf2.rackcdn.com/Sublime Text 2.0.2 Setup.exe", "downloads/")
    print("Sublime Text 2 for windows downloaded.")
    download_file("http://c758482.r82.cf2.rackcdn.com/Sublime Text 2.0.2.dmg", "downloads/")
    print("Sublime Text 2 for mac downloaded.")
    download_file("http://c758482.r82.cf2.rackcdn.com/Sublime Text 2.0.2.tar.bz2", "downloads/")
    print("Sublime Text 2 for linux downloaded.")


def atom():
    """Download multiple code editor"""
    download_file("https://github.com/atom/atom/releases/download/v1.0.5/AtomSetup.exe", "downloads/")
    print("Atom for windows downloaded.")
    download_file("https://github.com/atom/atom/releases/download/v1.0.5/atom-mac.zip", "downloads/")
    print("Atom for mac downloaded.")
    download_file("https://github.com/atom/atom/releases/download/v1.0.5/atom-mac-symbols.zip", "downloads/")
    print("Atom-symbols for mac downloaded.")
    download_file("https://github.com/atom/atom/releases/download/v1.0.5/atom.x86_64.rpm", "downloads/")
    print("Atom.rpm downloaded.")
    download_file("https://github.com/atom/atom/releases/download/v1.0.5/atom-amd64.deb", "downloads/")
    print("Atom.deb downloaded.")

if __name__ == '__main__':
    download_steps()
