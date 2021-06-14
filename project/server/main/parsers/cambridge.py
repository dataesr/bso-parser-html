from bs4 import *
import re, bs4
from project.server.main.parsers.strings import get_clean_text, get_doi, get_orcid


# doi 10.1017
def parse_cambridge(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    res.update(parse_references(soup))
    return res

def parse_abstract(soup):
    res = {}
    abstracts = []
    for resume_elem in soup.find_all(class_="abstract"):
        abstract = {}
        abstract['abstract'] = get_clean_text(resume_elem)
        if abstract:
            abstracts.append(abstract)
    if abstracts:
        res['abstracts'] = abstracts

    return res

def parse_references(soup):
    res = {}
    references = []
    for ref_elem in soup.find_all(id=re.compile("reference-.*-content")):
        ref = {}
        for a_elem in ref_elem.find_all('a'):
            if 'doi.org' in a_elem.attrs.get('href', ''):
                ref['link'] = a_elem.attrs['href']
                ref['doi'] = get_doi(a_elem.attrs['href'])

        _ = [e.extract() for e in ref_elem.find_all("a")]

        current_ref = get_clean_text(ref_elem)

        if current_ref:
            ref['reference'] = current_ref


        if ref:
            references.append(ref)
    if references:
        res['references'] = references
    return res

def parse_authors(soup):
    res = {}
    affiliations_dict = {}
    for elt in soup.find_all(class_="contributor-affiliation"):
        if 'id' in elt.attrs:
            aff_id = elt.attrs['id']
        current_aff = []
        for addr in elt.find_all("addrline"):
            current_aff.append(get_clean_text(addr))
        if not current_aff:
            current_aff = [get_clean_text(elt.find(class_="aff"))]
        if not current_aff:
            current_aff = [get_clean_text(elt.find(class_="affiliation"))]
        current_affiliation = {"name": " ".join(current_aff)}
        affiliations_dict[aff_id] = current_affiliation
    affiliations = list(affiliations_dict.values())


    authors_dict = {}
    author_elt = None
    for author_elt in soup.find_all(class_='author'):
        author = {}
        title_elem = author_elt.find(class_="title")
        if title_elem:
            full_name = get_clean_text(title_elem)
            author['full_name'] = full_name
            author['author_position'] = len(authors_dict) + 1
        col_elem = author_elt.find(class_='col')
        if col_elem:
            current_affil = {"name": get_clean_text(col_elem).replace("Affiliation:", "").strip()}
            author['affiliations'] = [current_affil]
            if current_affil not in affiliations:
                affiliations.append(current_affil)
        if author and full_name:
            authors_dict[full_name] = author

    if author_elt:
        for a_elem in author_elt.find_all('a'):

            full_name = get_clean_text(a_elem)

            if  full_name and full_name not in authors_dict:
                author = {}
                author['full_name'] = full_name
                author['author_position'] = len(authors_dict) + 1
                authors_dict[full_name] = author
            elif full_name:
                author = authors_dict[full_name]

            author_affiliations = author.get('affiliations', [])

            if 'href' in a_elem.attrs and 'orcid' in a_elem.attrs['href']:
                author['orcid'] = get_orcid(a_elem.attrs['href'])

            sup_elem = a_elem.findNext('sup')
            if sup_elem:
                aff_id = get_clean_text(sup_elem).replace('(','').replace(')','')
                if aff_id in affiliations_dict and affiliations_dict[aff_id] not in author_affiliations:
                    author_affiliations.append(affiliations_dict[aff_id])

            if author_affiliations:
                author['affiliations'] = author_affiliations

    authors = list(authors_dict.values())


    if affiliations:
        res["affiliations"] = affiliations

    if authors:
        res["authors"] = authors

    return res

