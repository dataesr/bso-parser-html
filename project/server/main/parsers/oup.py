import re, bs4
from project.server.main.parsers.strings import get_clean_text, get_orcid


# doi 10.1093
def parse_oup(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    return res

def parse_authors(soup):
    res = {}
    authors = []
    affiliations = []

    for elt in soup.find_all(class_="info-card-author"):
        author = {}
        current_affiliations = []
        name_elt = elt.find(class_="info-card-name")
        if name_elt:
            author['full_name'] = get_clean_text(name_elt)

        a_elem = elt.find("a", href=re.compile('search-results'))
        if a_elem:
            sp = re.sub(".*Authors=","",a_elem['href']).split('+')
            if len(sp) == 2:
                author['first_name'] = sp[0]
                author['last_name'] = sp[1]
            if sp:
                author['full_name'] = " ".join(sp)

        a_elem = elt.find("a", href=re.compile('mailto'))
        if a_elem:
            author['corresponding'] = True
            author['email'] = a_elem['href'].replace('mailto:', '')

        a_elem = elt.find("a", href=re.compile('orcid'))
        if a_elem:
            author['orcid'] = get_orcid(a_elem['href'])

        for aff_elt in elt.find_all(class_="aff"):
            aff = {'name': get_clean_text(aff_elt)}
            current_affiliations.append(aff)
            if aff not in affiliations:
                affiliations.append(aff)
        if current_affiliations:
            author['current_affiliations'] = current_affiliations


        if author:
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
    for resume_elem in soup.find_all(class_="abstract"):
        abstract = {}
        abstract['abstract'] = get_clean_text(resume_elem)
        if abstract:
            abstracts.append(abstract)
    if abstracts:
        res['abstracts'] = abstracts

    keywords = []
    for k in soup.find_all('a', href = re.compile('f_SemanticFilterTopics|keyword')):
        keywords.append({'keyword': get_clean_text(k)})
    if keywords:
        res['keywords'] = keywords

    for e in soup.find_all(class_="history-entry"):
        date_type = e.find(class_="wi-state")
        date_value = e.find(class_="wi-date")
        if date_type and date_value:
            date_type = get_clean_text(date_type).replace(':', '').strip().lower()+'_date'.replace(' ','_')
            res[date_type] = get_clean_text(date_value)

    return res


