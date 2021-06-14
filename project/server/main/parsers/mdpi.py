import re, bs4
from project.server.main.parsers.strings import get_clean_text, get_orcid


# doi 10.3390
def parse_mdpi(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    return res

def parse_authors(soup):
    res = {}

    affiliations_dict = {}

    for e in soup.find_all(class_="affiliation"):
        sup = e.find('sup')
        if sup:
            aff_id = get_clean_text(sup)
        else:
            aff_id = len(affiliations_dict)
        name_elem = e.find(class_="affiliation-name")
        if name_elem:
            affiliations_dict[aff_id] = {"name": get_clean_text(name_elem)}
    affiliations = list(affiliations_dict.values())

    authors = []
    for e in soup.find_all(class_ = "inlineblock"):
        author = {}
        current_affiliations = []
        for sup_e in e.find_all('sup'):
            affs = get_clean_text(sup_e)
            for aff_id in affs.split(','):
                aff_id = aff_id.strip()
                if aff_id in affiliations_dict:
                    current_affiliations.append(affiliations_dict[aff_id])
                elif 0 in affiliations_dict:
                    current_affiliations.append(affiliations_dict[0])
        _  = [k.extract() for k in e.find_all("sup")]
        author['full_name'] = get_clean_text(e).replace(',', '').strip()
        if author['full_name'][-4:] == " and":
            author['full_name'] = author['full_name'][0:len(author['full_name'])-4].strip()

        orcid_elem = e.find('a', href=re.compile('.*orcid'))
        if orcid_elem:
            author['orcid'] = get_orcid(orcid_elem.attrs['href'])

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
    abstr_elem = soup.find(class_=re.compile("art-abstract"))
    if abstr_elem:
        res['abstract'] = [{'abstract': get_clean_text(abstr_elem)}]

    keywords = []
    k_elem = soup.find(itemprop='keywords')
    if k_elem:
        for k in get_clean_text(k_elem).split(';'):
            keywords.append({'keyword': k.strip()})
    if keywords:
        res["keywords"] = keywords

    return res
