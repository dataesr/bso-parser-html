import re, bs4
from project.server.main.parsers.strings import get_clean_text, get_doi, get_orcid

#doi 10.1007
def parse_springer(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    res.update(parse_references(soup))
    return res

def parse_authors(soup): 
    res = {}
    affiliations_dict = {}
    authors = []

    for aff in soup.find_all(class_="affiliation"):
        if 'data-test' in aff.attrs:
            aff_id = aff.attrs['data-test']
        else:
            aff_id = len(affiliations_dict)
        #print(get_clean_text(aff))
        aff_elt = aff.find(class_="affiliation__item")
        if aff_elt:
            affiliations_dict[aff_id] = {'name': get_clean_text(aff_elt)}
    affiliations = list(affiliations_dict.values())

    authors_elem = soup.find(class_="authors-affiliations")
    if authors_elem:
        for e in authors_elem.find_all(itemtype = "http://schema.org/Person"):
            #print(e)
            author = {}
            orcid_elt = e.find('a', href=re.compile('orcid'))
            if orcid_elt:
                author['orcid'] = get_orcid(orcid_elt['href'])
            mail_elt = e.find('a', href=re.compile('mailto'))
            if mail_elt:
                author['email'] = mail_elt['href'].replace('mailto:', '')
                author['corresponding'] = True
            name_elt = e.find(itemprop="name")
            if name_elt:
                author['full_name'] = get_clean_text(name_elt)
            current_affiliations = []
            for li in e.find_all('li'):
                if 'data-affiliation' in li.attrs:
                    aff_id = li['data-affiliation']
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
    references = []
    for elem in soup.find_all(class_="CitationContent"):
        #print(elem)
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

def parse_abstract(soup):
    res = {}

    abstracts = []
    for ab_elem in soup.find_all(class_="Abstract"):
        abstract = {'abstract': get_clean_text(ab_elem).replace("Abstract ", "")}
        if 'lang' in ab_elem.attrs:
            lang = ab_elem['lang']
            abstract['lang'] = lang
        abstracts.append(abstract)
    if abstracts:
        res['abstract'] = abstracts

    keywords = []
    for k in soup.find_all(class_="Keyword"):
        keywords.append({'keyword': get_clean_text(k)})
    if keywords:
        res['keywords'] = keywords

    acknowledgements = []
    for ab_elem in soup.find_all(class_="content"):
        if ab_elem.find(class_="Heading") and "Acknowledgements" in get_clean_text(ab_elem.find(class_="Heading")):
            acknowledgement = {'acknowledgment': get_clean_text(ab_elem).replace("Acknowledgements ", "")}
            if 'lang' in ab_elem.attrs:
                lang = ab_elem['lang']
                acknowledgement['lang'] = lang
            acknowledgements.append(acknowledgement)
        if acknowledgements:
            res['acknowledgments'] = acknowledgements

    return res
