import re, bs4
from project.server.main.parsers.strings import get_clean_text, get_orcid


# doi 10.1021
def parse_acs(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    return res

def parse_authors(soup):
    res = {}
    affiliations, authors = [], []

    for elem in soup.find_all(class_="loa-info"):
        author = {}
        current_affiliations = []
        name = elem.find(class_="loa-info-name")
        if name:
            full_name = get_clean_text(name)
            author['full_name'] = full_name
        for aff_elem in elem.find_all(class_='loa-info-affiliations-info'):
            current_aff = {'name': get_clean_text(aff_elem)}
            if current_aff not in affiliations:
                affiliations.append(current_aff)
            current_affiliations.append(current_aff)
        if current_affiliations:
            author['affiliations'] = current_affiliations

        corresp_elem = soup.find(class_="conrtib-corresp")
        if corresp_elem:
            author['corresponding'] = True
            corresp = [w for w in get_clean_text(corresp_elem).split(' ') if '@' in w]
            if len(corresp) == 1:
                author['email'] = corresp[0]

        orcid_elem = soup.find(class_="loa-info-orcid")
        if orcid_elem:
            a_elem = orcid_elem.find('a')
            if a_elem and 'href' in a_elem.attrs:
                author['orcid'] = get_orcid(a_elem.attrs['href'])

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
    abstract_elem = soup.find(class_="articleBody_abstractText")
    if abstract_elem:
        res['abstract'] = [{'abstract': get_clean_text(abstract_elem)}]

    images = []
    img_elem = soup.find(class_="article_abstract-img")
    if img_elem:
        for k in img_elem.find_all('img'):
            if 'src' in k.attrs:
                images.append({"url": "https://pubs.acs.org/"+k.attrs['src']})
    if images:
        res["images"] = images


    classifications = []
    for e in soup.find_all('a', href=re.compile(".*ConceptID")):
        classifications.append({"reference": "ConceptACS", "label": get_clean_text(e)})
    if classifications:
        res["classifications"] = classifications

    keywords = []
    for k in soup.find_all(class_="keyword"):
        keywords.append({"keyword": get_clean_text(k)})
    if keywords:
        res['keywords'] = keywords

    return res

