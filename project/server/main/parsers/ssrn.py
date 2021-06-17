import re, bs4
from project.server.main.parsers.strings import get_clean_text


# doi 10.2139
def parse_ssrn(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    res.update(parse_references(soup))
    return res

def parse_references(soup):
    res = {}
    references = []
    refs = soup.find(class_="references-list")
    if refs:
        for ref_elem in refs.find_all("li"):
            ref = {"reference": get_clean_text(ref_elem)}

            if ref:
                references.append(ref)
        if references:
            res['references'] = references
    return res

def parse_abstract(soup):
    res = {}
    abstracts = []
    for resume_elem in soup.find_all(class_="abstract-text"):
        abstract = {}
        abstract['abstract'] = get_clean_text(resume_elem)
        if abstract:
            abstracts.append(abstract)
    if abstracts:
        res['abstract'] = abstracts

    keywords = []
    for e in soup.find_all('strong'):
        if 'Keywords' in get_clean_text(e):
            for k in re.split(';|,|\.', e.next.next):
                keywords.append({'keyword': k.strip()})
    if keywords:
        res['keywords'] = keywords

    jel = []
    for e in soup.find_all('strong'):
        if 'JEL Class' in get_clean_text(e):
            for k in re.split(';|,|\.', e.next.next):
                jel.append({'reference': 'JEL', 'code': k.strip()})
    if jel:
        res['classifications'] = jel


    return res



def parse_authors(soup):
    res = {}
    authors, affiliations = [], []
    e = soup.find(class_="authors")
    if e:
        for elem in e.find_all('h2'):
            author = {}
            full_name = get_clean_text(elem)
            current_affiliations = []
            author['full_name'] = full_name
            for k in elem.findAllNext():
                if get_clean_text(k) == full_name:
                    continue
                if 'href' in k.attrs or 'class'in k.attrs:
                    break
                if k.find('a'):
                    break
                if 'date ' not in get_clean_text(k).lower():
                    current_aff = {'name': get_clean_text(k)}
                    current_affiliations.append(current_aff)
                    if current_aff not in affiliations:
                        affiliations.append(current_aff)
            author['affiliations'] = current_affiliations
            if author:
                authors.append(author)
    for ix, a in enumerate(authors):
        a['author_position'] = ix+1

    if affiliations:
        res['affiliations'] = affiliations
    if authors:
        res['authors'] = authors
    return res

