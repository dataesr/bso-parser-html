import re, bs4
from project.server.main.parsers.strings import get_clean_text, get_orcid


# doi 10.1136
def parse_bmj(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    res.update(parse_references(soup))
    return res

def parse_authors(soup):
    res = {}

    authors, affiliations = [], []

    affiliations_dict = {}
    for ix, aff_elem in enumerate(soup.find_all(class_="aff")):
        sup_elem = aff_elem.find('sup')
        if sup_elem:
            aff_id_s = get_clean_text(sup_elem).split(',')
        else:
            aff_id_s = [str(ix+1)]
        _  = [e.extract() for e in aff_elem.find_all("sup")]
        for aff_id in aff_id_s:
            affiliations_dict[aff_id] = {'name': get_clean_text(aff_elem)}
    affiliations = list(affiliations_dict.values())

    authors = []
    for aut_elem in soup.find_all(id=re.compile("contrib*")):
        author = {}
        a_elem = aut_elem.find('a')
        if a_elem and 'href' in a_elem.attrs and 'orcid' in a_elem.attrs['href']:
            author['orcid'] = get_orcid(a_elem.attrs['href'])

        name_elem = aut_elem.find(class_="name")
        if name_elem:
            author['full_name'] = get_clean_text(name_elem)
        current_affiliations = []
        for sup_elem in aut_elem.find_all("a"):
            aff_id = get_clean_text(sup_elem)
            if not aff_id:
                aff_id = sup_elem.attrs['href'][-1]


            if aff_id in affiliations_dict:
                current_affiliations.append(affiliations_dict[aff_id])

        if current_affiliations:
            author['affiliations'] = current_affiliations
        if author and author not in authors:
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
    for ref_elem in soup.find_all(class_="ref-cit"):
        ref = {}
        current_ref=""

        cite_elem1 = ref_elem.find(class_ = "cit-auth-list")
        if cite_elem1:
            current_ref += get_clean_text(cite_elem1)

        cite_elem2 = ref_elem.find("cite")
        if cite_elem2:
            current_ref += get_clean_text(cite_elem2)

        if current_ref:
            ref['reference'] = current_ref

        if "data-doi" in ref_elem.attrs:
            ref['doi'] = ref_elem.attrs['data-doi'].lower()
        if ref:
            references.append(ref)
    if references:
        res['references'] = references
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

    return res
