import re, bs4
from project.server.main.parsers.strings import get_clean_text, get_doi, get_orcid

# doi 10.1038
def parse_nature(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    res.update(parse_references(soup))
    return res

def parse_abstract(soup):
    res = {}

    abstracts = []
    for ab_elem in soup.find_all("section", {"data-title":"Abstract"}) + soup.find_all(id=re.compile('Abs.*-content')):
        abstract = {'abstract': get_clean_text(ab_elem).replace("Abstract ", "")}
        if 'lang' in ab_elem.attrs:
            lang = ab_elem['lang']
            abstract['lang'] = lang
        abstracts.append(abstract)
    if abstracts:
        res['abstract'] = abstracts

    acknowledgements = []
    for ab_elem in soup.find_all("section", {"data-title":"Acknowledgements"}):
        acknowledgement = {'acknowledgment': get_clean_text(ab_elem).replace("Acknowledgements ", "")}
        if 'lang' in ab_elem.attrs:
            lang = ab_elem['lang']
            acknowledgement['lang'] = lang
        acknowledgements.append(acknowledgement)
    if acknowledgements:
        res['acknowledgments'] = acknowledgements

    return res

def parse_references(soup):
    res = {}
    references = []
    for elem in soup.find_all(id=re.compile("ref-C")):
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

def parse_authors(soup):
    res = {}
    authors = []
    affiliations = []
    list_authors = soup.find('ul', class_=re.compile('(.*author-list.*)|(.*list-author.*)'))
    if list_authors:
        for elt in list_authors.find_all(itemprop="author"):
            #print(elt)
            author = {}
            current_affiliations = []
            name_elt = elt.find('span', itemprop="name")
            if name_elt:
                author['full_name'] = get_clean_text(name_elt)
            for aff_elt in elt.find_all(itemprop="affiliation"):
                current_affiliation = {}
                aff_name = ''
                aff_elt_name = aff_elt.find(itemprop="name")
                if aff_elt_name and 'content' in aff_elt_name.attrs:
                    aff_name = aff_elt_name.attrs['content']
                aff_elt_addr = aff_elt.find(itemprop="address")
                if aff_elt_addr and 'content' in aff_elt_addr.attrs:
                    if aff_name in aff_elt_addr.attrs['content']:
                        aff_name = ''
                    addr_elts = aff_elt_addr.attrs['content'].split(',')
                    external_ids = []
                    grids = []
                    for add in addr_elts:
                        if 'grid.' in add:
                            external_ids.append({'id_type': 'grid', 'id_value': add.strip()})
                            grids.append(add.strip())
                        elif re.search("([0-9A-Z]{4}(.)?){4}", add):
                            external_ids.append({'id_type': 'isni', 'id_value': add.strip()})
                        else:
                            aff_name+=" "+add.strip()
                            aff_name = aff_name.strip()
                    if external_ids:
                        current_affiliation['external_ids'] = external_ids
                    if grids:
                        current_affiliation['grid'] = grids
                if aff_name:
                    current_affiliation['name'] = aff_name
                if current_affiliation:
                    current_affiliations.append(current_affiliation)
                    if current_affiliation not in affiliations:
                        affiliations.append(current_affiliation)

            if current_affiliations:
                author['affiliations'] = current_affiliations

            orcid_elt = elt.find('a', href=re.compile('orcid'))
            if orcid_elt:
                author['orcid'] = get_orcid(orcid_elt['href'])

            if elt.find('use', {"xlink:href":re.compile('email')}):
                author['corresponding'] = True

            if author:
                authors.append(author)
    for ix, a in enumerate(authors):
        a['author_position'] = ix+1

    for k in soup.find_all(class_="c-article-identifiers__item", href=re.compile("term=")):
        sp = (re.sub(".*term=","",k['href'])).split('+')
        if len(sp) == 2:
            for a in authors:
                if sp[0] in a.get('full_name', '') and sp[1] in a.get('full_name', ''):
                    a['first_name'] = sp[0]
                    a['last_name'] = sp[1]

    if affiliations:
        res['affiliations'] = affiliations
    if authors:
        res['authors'] = authors
    return res
