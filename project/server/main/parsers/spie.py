import re, bs4
from project.server.main.parsers.strings import get_clean_text


# doi 10.1117
def parse_spie(soup, doi):
    res = {"doi": doi}
   # res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    #res.update(parse_references(soup))
    return res

def parse_abstract(soup):
    res = {}
    keywords = []
    for k in soup.find_all(class_="keywordsText"):
        keywords.append({'keyword': get_clean_text(k)})
    if keywords:
        res['keywords'] = keywords

    return res



