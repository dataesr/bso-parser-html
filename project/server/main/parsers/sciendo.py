import re, bs4
from project.server.main.parsers.strings import get_clean_text


# doi 10.1515
def parse_sciendo(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    #res.update(parse_abstract(soup))
    #res.update(parse_references(soup))
    return res

def parse_authors(soup):
    res = {}
    authors, affiliations = [], []
    for e in soup.find_all(class_="contrib"):
        author = {}
        current_affiliations = []
        for aff in e.find_all(class_="aff"):
            current_aff = {'name': get_clean_text(aff)}
            current_affiliations.append(current_aff)
            if current_aff not in affiliations:
                affiliations.append(current_aff)

        if current_affiliations:
            author['affiliation'] = current_affiliations
        _  = [e.extract() for e in e.find_all(class_ = "aff")]
        name_elem = e.next
        if name_elem:
            author['full_name'] = name_elem

        a_elem = e.find("a", href=re.compile('mailto'))
        if a_elem:
            author['corresponding'] = True
            author['email'] = a_elem['href'].replace('mailto:', '').split('?')[0]

        if author:
            authors.append(author)

    for ix, a in enumerate(authors):
        a['author_position'] = ix+1

    if affiliations:
        res['affiliations'] = affiliations
    if authors:
        res['authors'] = authors
    return res


