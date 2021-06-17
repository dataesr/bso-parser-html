import re, bs4
from project.server.main.parsers.strings import get_clean_text, get_doi


# doi 10.3389
def parse_frontiers(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    res.update(parse_references(soup))
    return res

def parse_authors(soup):
    res = {}

    affiliations_dict = {}
    notes_elem = soup.find('ul', class_='notes')
    if notes_elem:
        for e in notes_elem.find_all('li'):
            sup_elem = e.find('sup')
            if sup_elem:
                aff_id = get_clean_text(sup_elem)
            else:
                aff_id = 0
            _ = [e.extract() for e in e.find_all("sup")]
            affiliations_dict[aff_id] = {"name": get_clean_text(e)}

    affiliations = list(affiliations_dict.values())

    authors=[]
    for elem in soup.find_all(class_="authors"):
        for a in elem.find_all('a'):
            author = {}
            current_affiliations = []
            full_name = get_clean_text(a)
            author['full_name'] = full_name
            sup_elem = a.findNext('sup')
            if sup_elem:
                sup = get_clean_text(sup_elem)
                for aff_id in sup:
                    if aff_id in affiliations_dict:
                        current_affiliations.append(affiliations_dict[aff_id])
            if current_affiliations:
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

def parse_references(soup):

    res = {}
    for e in soup.find_all('h2'):
        if get_clean_text(e)=="Funding":
            break
    next_p = e.findNext('p')
    if next_p:
        funding = get_clean_text(next_p)
        res['grants'] = [{'grant':funding}]
        res['has_grant'] = True

    references = []
    for ref_elem in soup.find_all(class_="References"):
        ref = {}

        for a_elem in ref_elem.find_all('a'):
            if 'doi.org' in a_elem.attrs.get('href', ''):
                ref['link'] = a_elem.attrs['href']
                ref['doi'] = get_doi(a_elem.attrs['href'])

        _ = [e.extract() for e in ref_elem.find_all("a")]

        current_ref=get_clean_text(ref_elem)

        if current_ref:
            ref['reference'] = current_ref

        if ref:
            references.append(ref)
    if references:
        res['references'] = references
    return res



