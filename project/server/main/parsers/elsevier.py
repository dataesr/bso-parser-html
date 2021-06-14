import json
import re, bs4
from project.server.main.parsers.strings import get_clean_text

#doi 10.1016
def parse_elsevier(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    return res

def get_value(x):
    res = []
    if '_' in x:
        return x['_']
    if '$$' in x:
        for e in x['$$']:
            res.append(get_value(e))
    return " ".join(res)

def get_js(soup):
    js=None
    for s in soup.find_all('script'):
        if ('type' in s.attrs) and (s.attrs['type']=='application/json'):
            try:
                js = json.loads(get_clean_text(s))
            except:
                print("ERROR in loading json ")
            break
    return js

def parse_authors(soup):
    res = {}

    js = get_js(soup)
    if js is None:
        return res


    affiliations_dict = {}
    for aff_id in js.get('authors', {}).get('affiliations', []):
        current_affiliation = {}
        elt = js.get('authors', {}).get('affiliations', {}).get(aff_id, {}).get('$$', [])
        for e in elt:
            if e.get("#name") == "textfn":
                current_affiliation['name'] = get_value(e)
            if e.get("#name") in ["affiliation"]:
                for sub_e in e.get('$$', []):
                    for f in ['city', 'country', 'postal-code', "address-line"]:
                        if sub_e.get("#name") == f:
                            if f not in current_affiliation:
                                current_affiliation[f] = ""
                            current_affiliation[f] = (current_affiliation[f]+" "+get_value(sub_e)).strip()
        if current_affiliation:
            affiliations_dict[aff_id] = current_affiliation

    for footnote in js.get('authors', {}).get('footnotes', []):
        aff_id = footnote.get("$", {}).get('id')
        for k in footnote.get('$$', []):
            if k.get("#name") in ['note-para']:
                affiliations_dict[aff_id] = {'footnote': get_value(k)}

    authors=[]
    for aut in js.get('authors', {}).get('content', []):
        for elt in aut.get('$$', []):
            author={}
            current_affiliations = []
            if 'orcid' in elt.get('$', {}):
                author['orcid'] = elt['$']['orcid']
            for sub_e in elt.get('$$', []):
                if sub_e.get("#name") == "given-name" and get_value(sub_e):
                    author["first_name"] = get_value(sub_e)

                if sub_e.get("#name") == "surname" and get_value(sub_e):
                    author["last_name"] = get_value(sub_e)

                if sub_e.get("#name") == "cross-ref" and sub_e.get("$", {}).get('refid'):
                    aff_id = sub_e.get("$", {}).get('refid')
                    if aff_id in affiliations_dict:
                        current_affiliations.append(affiliations_dict[aff_id])

                    if aff_id[0:3] == "cor":
                        author['corresponding'] = True

                if sub_e.get("#name") == "e-address" and get_value(sub_e):
                    if sub_e.get('$', {}).get('type'):
                        author[sub_e.get('$', {}).get('type')] = get_value(sub_e)


            if current_affiliations:
                author['affiliations'] = current_affiliations
            if author:
                authors.append(author)


    affiliations = list(affiliations_dict.values())

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

    abstract_elem = soup.find(class_="abstract")
    if abstract_elem:
        res['abstract'] = [{"abstract": get_clean_text(abstract_elem).replace("Abstract ","")}]

    keywords = []
    for k in soup.find_all(class_="keyword"):
        keywords.append({"keyword": get_clean_text(k)})
    if keywords:
        res["keywords"] = keywords

    images = []
    figures_elem = soup.find(id='toc-figures')
    if figures_elem:
        for fig in figures_elem.find_all('img'):
            if 'src' in fig.attrs:
                images.append({"url": fig.attrs['src']})
    if images:
        res["images"] = images

    return res



