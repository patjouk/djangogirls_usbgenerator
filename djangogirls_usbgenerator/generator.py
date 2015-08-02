import requests

def download_file(address, filename):
    r = requests.get(address, stream=True)
    with open(filename, "wb") as f:
        for chunk in r.iter_content(1024):
            if chunk:
                f.write(chunk)
                f.flush()

