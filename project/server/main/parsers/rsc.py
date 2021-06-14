import re, bs4
from project.server.main.parsers.strings import get_clean_text, get_orcid


# doi 10.1039
def parse_rsc(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    return res

def parse_abstract(soup):
    res = {}

    for e in soup.find_all('h2'):
        if 'acknowledgements' in get_clean_text(e).lower():
            p = e.findNext('p')
            if p:
                res['acknowledgments'] = [{'acknowledgment': get_clean_text(p)}]

    for e in soup.find_all(class_="c fixpadt--l"):
        data_type = e.find(class_ = "c__10")
        data_value = e.find(class_ = "c__14")
        if data_type and data_value:
            data_type_str = get_clean_text(data_type).lower().replace(' ', '_')
            for f in ['submitted', 'accepted', 'published']:
                if f in data_type_str:
                    data_type_str = data_type_str+'_date'.strip()
                    break
            res[data_type_str] = get_clean_text(data_value)


    return res




def parse_authors(soup):
    res = {}
    authors = []

    affiliations_dict = {}
    for aff in soup.find_all(class_=re.compile('article__author-affiliation')):
        sup_elem = aff.find('span')
        if sup_elem:
            aff_id = get_clean_text(sup_elem)
            if len(aff.find_all("span"))>1:
                _  = [e.extract() for e in aff.find_all("span")[0:1]]
        else:
            aff_id = len(affiliations_dict)

        affiliations_dict[aff_id] = {'name': get_clean_text(aff)}

    affiliations = list(affiliations_dict.values())

    for elt in soup.find_all(class_ = 'article__author-link'):
        author = {}
        current_affiliations = []
        for sup in elt.find_all('sup'):
            for aff_id in get_clean_text(sup):
                if aff_id in affiliations_dict:
                    #if '@' in affiliations_dict[aff_id].get('name', ''):
                    #    author['corresponding'] = True

                    current_affiliations.append(affiliations_dict[aff_id])


        o_elem = elt.find("a", href=re.compile('orcid'))
        if o_elem:
            author['orcid'] = get_orcid(o_elem['href'])

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

