import sys
import urllib.request
from bs4 import BeautifulSoup as bs
from pylatex import Document, Section, Subsection, Package
from pylatex.utils import italic


def arxiv_search(search_query):

    url = 'http://export.arxiv.org/api/query?search_query=all:' + \
        search_query + '&start=0&max_results=5'
    data = urllib.request.urlopen(url).read()

    soup = bs(data, features='xml')
    title_array = []
    summary_array = []

    for i in soup.findAll('title'):
        title_array.append(i)

    for i in soup.findAll('summary'):
        summary_array.append(i)

    doc = Document()
    doc.packages.append(
        Package(
            'geometry',
            options=[
                'tmargin=1cm',
                'lmargin=1cm',
                'rmargin=1cm']))

    with doc.create(Section('Search results for \"' + search_query + '\"')):

        for i in range(1, 5):
            doc.append(Subsection(italic(title_array[i].string)))
            doc.append(summary_array[i].string)

    doc.generate_pdf()

if __name__ == "__main__":

    arxiv_search(sys.argv[1])
