from bs4 import BeautifulSoup
import re
from project.server.main.parsers.strings import get_clean_text, get_doi

# doi 10.4000

def parse_openedition(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    res.update(parse_references(soup))
    return res

def parse_authors(soup):
    res = {}
    authors, affiliations = [], []

    author_elts = soup.find("div", {"id":"authors"})
    if author_elts is None:
        author_elts = soup.find("div", {"id":"book-more-content-aboutauthor"})
    if author_elts is None:
        return res

    author_names = author_elts.find_all('h3')
    if len(author_names) == 0 :
        author_names = author_elts.find_all(class_='name')

    author_description_0 = author_elts.find_all(class_ = 'description')
    author_description = []
    for elt in author_description_0:
        if elt.find(class_="docnumber") is None:
            author_description.append(elt)


    if(len(author_names) != len(author_description) and len(author_names) > 1):
        associate_authors_affiliations = False
    else:
        associate_authors_affiliations = True

    for i, author_elt in enumerate(author_names):
        author={}

        last_name_elt = author_elt.find(class_= 'familyName')
        if last_name_elt:
            last_name = get_clean_text(last_name_elt)
            first_name = get_clean_text(author_elt).replace(last_name,'').strip()
            author['last_name'] = last_name
            author['first_name'] = first_name
            author['full_name'] = f"{first_name} {last_name}"
        else:
            author['full_name'] = get_clean_text(author_elt)

        if i<len(author_description):
            descriptions = re.split('–| ', get_clean_text(author_description[i]))
            structure_name, email = "", ""
            for e in descriptions:
                if '[at]' in e or '@' in e:
                    email  = e.replace('[at]', '@').strip()
                    if associate_authors_affiliations:
                        author['email'] = email
                        author['corresponding'] = True
                else:
                    structure_name += e.strip()+' '
            structure_name = structure_name.strip()
            affil = {'name':structure_name}
            if associate_authors_affiliations:
                author['affiliations'] = [affil]
            if affil not in affiliations:
                affiliations.append(affil)
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
    abstracts = []
    for abstract_elem in soup.find_all(id=re.compile("abstract\-*")):
        if 'lang' not in abstract_elem.attrs:
            continue
        lang = abstract_elem.attrs['lang']
        abstract = get_clean_text(abstract_elem)
        abstracts.append({'lang': lang, 'abstract': abstract})
    if abstracts:
        res['abstract'] = abstracts

    keywords= []
    for elem in soup.find_all(class_="index"):
        kw_elem = elem.find_all("a")
        for k in kw_elem:
            keywords.append({'keyword': get_clean_text(k)})
    if keywords:
        res["keywords"] = keywords

    return res


def parse_references(soup):
    res = {}
    references = []
    for ref_elem in soup.find_all(class_="bibliographie"):
        ref = {}
        link_elem = ref_elem.find('a')
        if link_elem and 'href' in link_elem.attrs:
            link = link_elem.attrs['href']
            ref['link'] = link
            if 'doi' in link:
                doi = get_doi(link)
                ref['doi'] = doi
        _ = [k.extract() for k in ref_elem.find_all("a")]
        ref['reference'] = get_clean_text(ref_elem)
        if ref:
            references.append(ref)
    if references:
        res["references"] = references
    return res
