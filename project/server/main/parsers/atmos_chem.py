from bs4 import *
import re, bs4
from project.server.main.parsers.strings import get_clean_text, get_orcid, get_doi


# doi 10.5194
def parse_atmos_chem(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    res.update(parse_references(soup))
    return res

def parse_authors(soup):
    
    affiliations_dict = {}
    affil_elem = soup.find(class_="affiliation-list")
    if affil_elem:
        affiliations_list_elem = affil_elem.find_all('li')
        for ix, elem in enumerate(affiliations_list_elem):
            sup_elem = elem.find('sup')
            if sup_elem:
                aff_id = get_clean_text(sup_elem)
            else:
                aff_id = ix
            _ = [k.extract() for k in elem.find_all("sup")]
            affiliations_dict[aff_id] = {"name": get_clean_text(elem)}
    affiliations = list(affiliations_dict.values())
    
    authors = []
    authors_elem = soup.find(class_="authors-full")
    if authors_elem:
        for elem in authors_elem.find_all("nobr"):
            author = {}
            current_affiliations = []
            sup_elem = elem.find('sup')
            if sup_elem:
                sup = get_clean_text(sup_elem)
                for aff_id in sup.split(','):
                    if aff_id in affiliations_dict:
                        current_affiliations.append(affiliations_dict[aff_id])
            else:
                current_affiliations = affiliations
            _ = [k.extract() for k in elem.find_all("sup")]
            author["affiliations"] = current_affiliations
            full_name = get_clean_text(elem).replace(',', '').strip()
            if full_name[0:4] == "and ":
                full_name = full_name[4:]
            author["full_name"] = full_name.strip()
            if elem.find(class_="orcid-authors-logo"):
                try:
                    author['orcid'] = get_orcid(elem.find(class_="orcid-authors-logo").attrs['href'])
                except:
                    pass

            if author:
                authors.append(author)
                
    for ix, a in enumerate(authors):
        a['author_position'] = ix+1

    res = {}
    if affiliations:
        res['affiliations'] = affiliations
    if authors:
        res['authors'] = authors
    return res

def parse_abstract(soup):
    res = {}
    abstract_elem = None
    for abstract_elem in soup.find_all(class_="abstract"):
        if 'class' in abstract_elem.attrs and 'article' in abstract_elem.attrs['class']:
            continue
    if abstract_elem is None:
        abstract_elem = soup.find(class_=re.compile(".*abstract-content"))
    if abstract_elem:
        abstract = get_clean_text(abstract_elem).replace('Abstract. ', '').replace('Abstract ', '')
        res['abstract'] = [{"abstract": abstract}]

    keywords = []
    kw_elem = soup.find(class_='keywords')
    if kw_elem:
        kw = get_clean_text(kw_elem).replace("Keywords:", "").strip()
        for k in kw.split(','):
            keywords.append({'keyword': k.strip()})
    if keywords:
        res["keywords"] = keywords

    return res

def parse_references(soup):
    res = {}
    references = []
    for ref_elem in soup.find_all(class_="ref"):
        ref = {}
        link_elem = ref_elem.find('a')
        if link_elem and 'href' in link_elem.attrs:
            link = link_elem.attrs['href']
            ref['link'] = link
            if 'doi' in link:
                doi = get_doi(link)
                ref['doi'] = doi
        _ = [k.extract() for k in ref_elem.find_all("a")]
        ref['reference'] = get_clean_text(ref_elem)
        if ref:
            references.append(ref)
    if references:
        res["references"] = references
    return res
