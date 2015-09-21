"""
dumpimages.py
    Downloads all the images on the supplied URL, and saves them to the
    specified output file

Usage:
    python dumpimages.py
"""


from bs4 import BeautifulSoup as bs
import urllib.parse
from urllib.request import urlopen
from urllib.request import urlretrieve
import os


def main(url, out_folder="/test/"):

    """Downloads all the images at 'url' to 'out_folder'"""
    soup = bs(urlopen(url))
    parsed = list(urllib.parse.urlparse(url))

    for image in soup.findAll("img"):
        print("Image: %(src)s" % image)
        # filename = image["src"].split("/")[-1]
        parsed[2] = image["src"]
        outpath = os.path.join(out_folder, "apod.jpg")
        if image["src"].lower().startswith("http"):
            urlretrieve(image["src"], outpath)
        else:
            urlretrieve(urllib.parse.urljoin(url, image['src']), outpath)

if __name__ == "__main__":
    url = "<url>"
    out_folder = "<destination path>"
    main(url, out_folder)
