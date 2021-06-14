import re, bs4
from project.server.main.parsers.strings import get_clean_text, get_orcid, get_doi


# doi 10.1063
def parse_aip(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    res.update(parse_references(soup))
    return res

def parse_authors(soup):
    res = {}

    authors, affiliations, affiliations_dict =[], [], {}
    for elt in soup.find_all(class_='author-affiliation'):
        sup_elem = elt.find('sup')
        aff_id = "0"
        if sup_elem:
            _ = [e.extract() for e in elt.find_all("sup")]
            aff_id = get_clean_text(sup_elem)
        affiliations_dict[aff_id] = {"name": get_clean_text(elt)}
    affiliations = list(affiliations_dict.values())

    for author_elem in soup.find_all(class_='contrib-author'):
        author = {}

        name_elem = author_elem.find('a', href=re.compile('/author'))
        if name_elem:
            author['full_name'] = get_clean_text(name_elem)

        orcid_elem = author_elem.find('a', href=re.compile('.*orcid.org'))
        if orcid_elem:
            author['orcid'] = get_orcid(orcid_elem.attrs['href'])

        corresp_elem = author_elem.find('a', href=re.compile('mailto'))  
        if corresp_elem:
            author['corresponding'] = True
            author['email'] = corresp_elem.attrs['href'].replace('mailto:','')

        current_affiliations = []
        author_sup = author_elem.find('sup')
        if author_sup:
            for aff_elem in get_clean_text(author_sup).split(','):
                current_id = aff_elem.strip()

                if current_id in affiliations_dict:
                    current_affiliations.append(affiliations_dict[current_id])

        if "0" in affiliations_dict:
            current_affiliations.append(affiliations_dict["0"])

        if current_affiliations:
            author['affiliations'] = current_affiliations

        if author:
            authors.append(author)

    for ix, a in enumerate(authors):
        a['author_position'] = ix+1
    
    if authors:
        res["authors"] = authors
        
    if affiliations:
        res["affiliations"] = affiliations
        
    return res
                            
def parse_abstract(soup):
    res = {}
    abstract_elem = soup.find(class_="hlFld-Abstract")
    if abstract_elem:
        res['abstract'] = {'abstract': get_clean_text(abstract_elem).replace('ABSTRACT ', '')}

    ack_elem = soup.find(class_="ack")
    if ack_elem:
        res["acknowledgments"] = [{'acknowledgment': get_clean_text(ack_elem).replace('ACKNOWLEDGMENTS ', '')}]

    classifications = []
    for e in soup.find_all(class_="topicLink"):
        classifications.append({"reference": "topicAIP", "label": get_clean_text(e)})
    if classifications:
        res["classifications"] = classifications

    return res

def parse_references(soup):
    res = {}
    references = []
    for elem in soup.find_all(class_="ref-text"):
        ref = {}
        for a_elem in elem.find_all('a'):
            if 'doi' in a_elem.attrs['href']:
                ref['link'] = a_elem.attrs['href']
                if 'doi.org/' in ref['link']:
                    ref['doi'] = get_doi(ref['link'])
                break
        _ = [e.extract() for e in elem.find_all('a')]
        ref['reference'] = get_clean_text(elem)
        if ref:
            references.append(ref)
    if references:
        res["references"] = references
    return res
