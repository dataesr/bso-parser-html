import re, bs4
from project.server.main.parsers.strings import get_clean_text


# doi 10.3233
def parse_ios(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    res.update(parse_references(soup))
    return res

def parse_authors(soup):
    res = {}

    affiliations_dict = {}

    aff_found = False
    for elt in soup.find_all(class_='metadata-entry'):
        if ("affiliation" in elt.get_text().lower()):
            aff_found = True
            break
    if aff_found:
        for aff in get_clean_text(elt).replace("Affiliations: ","").split("|"):
            name = re.sub("\[(.*)\]", "", aff).strip()
            aff_id = aff.replace(name, "").replace('[','').replace(']', '').strip()
            if not aff_id:
                aff_id = len(affiliations_dict)
            affiliations_dict[aff_id] = {'name': name}

    affiliations = list(affiliations_dict.values())

    authors = []
    authors_found = False
    for elt in soup.find_all(class_='metadata-entry'):
        if ("author" in elt.get_text().lower()):
            authors_found = True
            break
    if authors_found:
        for a_elem in elt.find_all('a', href=re.compile('http')):
            author = {}
            full_name = get_clean_text(a_elem)
            author['full_name'] = full_name
            sp = full_name.split(',')
            if len(sp) == 2:
                author['first_name'] = sp[1].strip()
                author['last_name'] = sp[0].strip()
            current_affiliations = []
            for s in a_elem.findAllNext('a'):
                if "id" in s.attrs or '#' not in s.attrs['href']:
                    break
                aff_id = get_clean_text(s)
                if aff_id in affiliations_dict:
                    current_affiliations.append(affiliations_dict[aff_id])
            if len(affiliations) == 1:
                current_affiliations = affiliations
            if current_affiliations:
                author['affiliations'] = current_affiliations
            authors.append(author)

        if len(authors) == 1 and authors[0].get('affiliations') is None:
            authors[0]['affiliations'] = affiliations

    for ix, a in enumerate(authors):
        a['author_position'] = ix+1

    if affiliations:
        res['affiliations'] = affiliations
    if authors:
        res['authors'] = authors
    return res

def parse_references(soup):
    res = {}
    references = [{'reference': get_clean_text(e)} for e in soup.find_all('tr', id=re.compile('ref.*'))]
    if references:
        res['references'] = references
    return res

def parse_abstract(soup):
    res = {}
    keywords = []
    abstr_found = False
    for elt in soup.find_all(class_='metadata-entry'):
        if ("keyword" in elt.get_text().lower()):
            abstr_found = True
            break
    if abstr_found:
        sp = get_clean_text(elt).split(':')
        if len(sp)==2:
            keywords = [{'keyword': e.strip()} for e in sp[1].split(',')]

    if keywords:
        res['keywords'] = keywords

    abstr_elem = soup.find(class_="front")
    if abstr_elem:
        res['abstract'] = [{'abstract': get_clean_text(abstr_elem)}]

    return res


