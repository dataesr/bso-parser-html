import re, bs4
from project.server.main.parsers.strings import get_clean_text, get_doi


# doi 10.7202
def parse_erudit(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    res.update(parse_references(soup))
    return res

def parse_authors(soup):
    res = {}
    
    authors, affiliations = [], []
    
    for author_elem in soup.find_all(class_="auteur-affiliation"):
        author = {}
        name_elem = author_elem.find("strong")
        if name_elem:
            author['full_name'] = get_clean_text(name_elem)
            _ = [e.extract() for e in author_elem.find_all("strong")]

        link_elem = author_elem.find('a')
        if link_elem:
            if 'href' in link_elem.attrs and 'mailto' in link_elem.attrs['href']:
                author['corresponding'] = True
                author['email'] = link_elem.attrs['href'].replace('mailto:', '')
            _ = [e.extract() for e in name_elem.find_all('a')]

        current_affil = {'name': get_clean_text(author_elem)}
        if current_affil not in affiliations:
            affiliations.append(current_affil)
        author['affiliations'] = current_affil

        if author:
            authors.append(author)

    if not authors:
        for author_elem in soup.find_all(class_ = "auteur"):
            author = {}
            name_elem = author_elem.find(class_="nompers")
            if name_elem:
                author['full_name'] = get_clean_text(name_elem)
                authors.append(author)
                
    for ix, a in enumerate(authors):
        a['author_position'] = ix+1

    if affiliations:
        res['affiliations'] = affiliations
    if authors:
        res['authors'] = authors
    return res


def parse_abstract(soup):
    res = {}
    abstracts = []
    for resume_elem in soup.find_all(class_="resume"):
        abstract = {}
        if 'id' in resume_elem.attrs:
            lang = resume_elem.attrs['id'].replace('resume-','')
            abstract['lang'] = lang
        abstract['abstract'] = get_clean_text(resume_elem)
        if abstract:
            abstracts.append(abstract)
    if abstracts:
        res['abstracts'] = abstracts

    return res


def parse_references(soup):
    res = {}
    references = []
    for ref_elem in soup.find_all(class_="refbiblio"):
        ref = {}
        link_elem = ref_elem.find(class_="idpublic")
        if link_elem:
            ref['link'] = link_elem.attrs['href']
            if 'doi' in ref['link']:
                ref['doi'] = get_doi(ref['link'])
        _  = [e.extract() for e in ref_elem.find_all("a")]
        ref['reference'] = get_clean_text(ref_elem)
        if ref:
            references.append(ref)
    if references:
        res["references"] = references
    return res
