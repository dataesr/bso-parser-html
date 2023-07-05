import re, bs4
import json
from project.server.main.parsers.strings import get_clean_text, get_orcid, get_doi


# doi 10.1155
def parse_hindawi(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    res.update(parse_references(soup))
    return res

def parse_authors1(soup):
    res = {}
    
    affiliations_dict = {}
    authors, affiliations = [], []
    data = None
    js_elem = soup.find('script', {'id':'__NEXT_DATA__'})
    if js_elem:
        try:
            data = json.loads(js_elem.text)
        except:
            pass
    if data is None:
        return res

    article_data = data.get('props',{}).get('pageProps', {}).get('article', {})

    for e in article_data.get('affiliations', []):
        affil = {'name': e.get('text','')}
        affiliations_dict[e.get('id', 0)] = affil

    affiliations = list(affiliations_dict.values())

    for e in article_data.get('authors', []):
        author = {}
        if 'name' in e:
            author['full_name'] = e['name']
        if e.get('email'):
            author['email'] = e['email']
            author['corresponding'] = True
        if e.get('orcid'):
            author['orcid'] =  get_orcid(e.get('orcid'))

        current_affiliations = []
        for aff_id in e.get('sup', []):
            if aff_id in affiliations_dict:
                current_affiliations.append(affiliations_dict[aff_id])
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

def parse_authors2(soup):
    res = {}
    affiliations_dict = {}
    affiliations, authors = [], []
    authors_elem = soup.find(class_ = 'article_authors')
    if authors_elem:
        affil_elem = authors_elem.find('div')
        if affil_elem:
            for aff_elem in affil_elem.find_all('p'):
                sup_elem = aff_elem.find("sup")
                if sup_elem:
                    aff_id = get_clean_text(sup_elem)
                else:
                    aff_id = 0
                if aff_elem.find('span'):
                    affiliations_dict[aff_id] = {'name': get_clean_text(aff_elem.find('span'))}

        affiliations = list(affiliations_dict.values())

        for e in authors_elem.children:
            if (e.attrs.get('class',[])):
                continue

            author = {}
            current_affiliations = []
            sup_elem = e.find('sup')
            if sup_elem:
                for aff_id in get_clean_text(sup_elem).split(','):
                    aff_id = aff_id.strip()
                    if aff_id in affiliations_dict:
                        current_affiliations.append(affiliations_dict[aff_id])
            if current_affiliations:
                author['affiliations'] = current_affiliations

            a_elem = e.find('a', href=re.compile(".*orcid"))
            if a_elem and 'orcid' in a_elem.attrs['href']:
                author['orcid'] = get_orcid(a_elem.attrs['href'])

            _  = [e.extract() for e in e.find_all("sup")]
            author['full_name'] = (get_clean_text(e).replace(',', '').replace('and', '').strip())
            authors.append(author)

    for ix, a in enumerate(authors):
        a['author_position'] = ix+1

    if affiliations:
        res['affiliations'] = affiliations
    if authors:
        res['authors'] = authors

    return res

def parse_authors(soup):
    res = parse_authors1(soup)
    if res:
        return res
    return parse_authors2(soup)

def parse_abstract(soup):
    res = {}
    e = soup.find(id="abstract")
    if e:
        abstr = e.findNext('p')
        if abstr:
            res['abstract'] = [{'abstract': get_clean_text(abstr)}]

    e = soup.find(id="acknowledgments")
    if e:
        abstr = e.findNext('p')
        if abstr:
            res['acknowledgments'] = [{'acknowledgment': get_clean_text(abstr)}]

    tl_elem = soup.find(class_=re.compile(".*TimeLineWrapper"))
    if tl_elem:
        for e in tl_elem.find_all('div'):
            spans = e.find_all('span')
            if len(spans) == 2:
                date_type = get_clean_text(spans[0]).lower()
                date_value = get_clean_text(spans[1])
                res[date_type+'_date'] = date_value

    return res

def parse_references(soup):
    res = {}
    references = []
    e = soup.find(id='references')
    if e:
        refs = e.findNext('ol')
        if refs:
            for ref_elem in refs.find_all("li"):
                ref = {}
                for a_elem in ref_elem.find_all('a'):
                    if 'doi.org' in a_elem.attrs.get('href', ''):
                        ref['link'] = a_elem.attrs['href']
                        ref['doi'] = get_doi(a_elem.attrs['href'])

                _ = [k.extract() for k in ref_elem.find_all("a")]

                current_ref = get_clean_text(ref_elem)

                if current_ref:
                    ref['reference'] = current_ref

                if ref:
                    references.append(ref)
    if references:
        res['references'] = references
    return res
