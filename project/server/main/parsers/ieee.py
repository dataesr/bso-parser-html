import re, bs4, json
from project.server.main.parsers.strings import get_clean_text, get_doi

#10.1109
def parse_ieee(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    res.update(parse_references(soup))
    return res

def get_js(soup):
    data = None
    for s in soup.find_all('script'):
        if "bal.document.metadata" in s.get_text():
            infos = re.sub(".*bal.document.metadata=", "", s.text.replace("\n", " ")).strip().replace("};","}")
            try:
                data = json.loads(infos)
            except:
                continue
            break

    return data

def parse_authors(soup):
    res = {}
    authors = []
    affiliations = []

    data = get_js(soup)
    if data is None:
        return {}

    for a in data.get('authors', []):
        author = {}
        current_affiliations = []
        if "firstName" in a:
            author['first_name'] = a['firstName']
        if "lastName" in a:
            author['last_name'] = a['lastName']
        if "affiliation" in a:
            aff_to_loop = []
            if isinstance(a["affiliation"], str):
                aff_to_loop = [a["affiliation"]]
            elif isinstance(a["affiliation"], list):
                aff_to_loop = a["affiliation"]
            for aff in aff_to_loop:
                current_aff = {"name": get_clean_text(aff)}
                current_affiliations.append(current_aff)
                if current_aff not in affiliations:
                    affiliations.append(current_aff)
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

def parse_abstract(soup):
    res = {}
    data = get_js(soup)
    if data is None:
        return res
    if data.get('abstract'):
        res['abstract'] = [{'abstract': data.get('abstract')}]

    keywords, classifications = [], []
    for k in data.get('keywords', []):
        if 'author' in k.get('type', '').lower():
            for e in k.get('kwd', []):
                keywords.append({"keyword": e})
        else:
            for e in k.get('kwd', []):
                classifications.append({"reference": k.get("type", "ieee"), "label":e})
    if keywords:
        res["keywords"] = keywords

    for k in data.get('pubTopics', []):
        if "name" in k:
            classifications.append({"reference": "ieee", "label":k.get('name')})
    if classifications:
        res["classifications"] = classifications

    if 'confLoc' in data and  data["confLoc"]:
        res["conference_location"] = data["confLoc"]

    if 'conferenceDate' in data and data["conferenceDate"]:
        res["conference_date"] = data["conferenceDate"]

    if 'articleId' in data and data['articleId']:
        res['external_ids'] = [{"ieee": data['articleId']}]

    if 'onlineDate' in data and data['onlineDate']:
        res['online_date'] = data['onlineDate']

    return res

def parse_references(soup):
    res = {}
    references = []

    for ref_elem in soup.find_all(class_="reference-container"):
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
