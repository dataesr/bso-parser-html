import re, bs4
from project.server.main.parsers.strings import get_clean_text, get_doi, get_orcid


# doi 10.1371
def parse_plos(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    res.update(parse_references(soup))
    return res

def parse_authors(soup):
    res = {}
    authors = []
    affiliations = []

    for elt in soup.find_all("li", {"data-js-tooltip":'tooltip_trigger'}):
        author={}
        name_elt = elt.find(class_="author-name")
        if name_elt:
            author['full_name'] = get_clean_text(name_elt).replace(',', '').strip()
        role_elt = elt.find(class_="roles")
        if role_elt:
            roles=[r.strip() for r in get_clean_text(role_elt).replace('Roles', '').split(',')]
            if roles:
                author['roles'] = roles

        a_elem = elt.find("a", href=re.compile('orcid'))
        if a_elem:
            author['orcid'] = get_orcid(a_elem['href'])

        a_elem = elt.find("a", href=re.compile('mailto'))
        if a_elem:
            author['corresponding'] = True
            author['email'] = a_elem['href'].replace('mailto:', '')

        current_affiliations = []
        for aff in elt.find_all(id=re.compile('Affiliation')):
            current_affiliation = {'name': get_clean_text(aff)}
            current_affiliations.append(current_affiliation)
            if current_affiliation not in affiliations:
                affiliations.append(current_affiliation)

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

    for ref_elem in soup.find_all(id=re.compile("ref")):
        ref = {}
        for a_elem in ref_elem.find_all('a'):
            if 'doi.org' in a_elem.attrs.get('href', ''):
                ref['link'] = a_elem.attrs['href']
                ref['doi'] = get_doi(a_elem.attrs['href'])
            elif '/document/' in a_elem.attrs.get('href', '')[0:10]:
                ref['link'] = "https://ieeexplore.ieee.org"+a_elem.attrs['href']
        _ = [k.extract() for k in ref_elem.find_all("a")]
        current_ref = get_clean_text(ref_elem)
        if current_ref:
            ref['reference'] = current_ref
        if ref:
            references.append(ref)
    if references:
        res["references"] = references

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
        res['abstract'] = abstracts

    images = []
    for e in soup.find_all('img', src=re.compile('figure')):
        if 'Fig' in e.get('alt'):
            images.append({'url': 'https://journals.plos.org'+e['src'], 'alt':e.get('alt')})
    if images:
        res['images'] = images

    keywords = []
    for k in soup.find_all('a', href = re.compile('filterSubject')):
        keywords.append({'keyword': get_clean_text(k)})
    if keywords:
        res['keywords'] = keywords


    elt_info = soup.find(class_='articleinfo')
    if elt_info:
        for p in elt_info.find_all('p'):
            p_strong = p.find('strong')
            if p_strong:
                data_type = get_clean_text(p_strong).replace(':', '').strip().lower().replace(' ', '_')
                if data_type in ['received', 'published']:
                    data_type += "_date"
                _  = [e.extract() for e in p.find_all("strong")]
                res[data_type] = get_clean_text(p)

    ack = soup.find(title="Acknowledgments")
    if ack and ack.parent:
        ack_str = get_clean_text(ack.parent).replace('Acknowledgments', '').strip()
        res['acknowledgments'] = [{'acknowledgment': ack_str}]

    return res
