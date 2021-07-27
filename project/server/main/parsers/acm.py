import re

from project.server.main.parsers.strings import get_clean_text


def parse_acm(soup, doi):
    res = {'doi': doi}
    res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    res.update(parse_references(soup))
    return res


def parse_authors(soup):
    res = {}
    affiliations, authors = [], []
    pill_elem = soup.find(class_='pill-all-authors')
    if pill_elem:
        for aut_elem in pill_elem.find_all(class_='author-info'):
            author = {}
            aut_link = aut_elem.find('a', href=re.compile('/author/*'))
            if aut_link and 'href' in aut_link.attrs:
                last_name, first_name = aut_link.attrs['href'].replace('/author/', '').split(',')
                author['last_name'] = get_clean_text(last_name)
                author['first_name'] = get_clean_text(first_name)
                author['full_name'] = f"{author['first_name']} {author['last_name']}"
            p_elem = aut_elem.find('p')
            if p_elem:
                current_aff = {'name': get_clean_text(p_elem)}
                if current_aff not in affiliations:
                    affiliations.append(current_aff)
                author['affiliations'] = [current_aff]
            if author:
                authors.append(author)
    for ix, a in enumerate(authors):
        a['author_position'] = ix+1
    if authors:
        res['authors'] = authors
    if affiliations:
        res['affiliations'] = affiliations
    return res
                            

def parse_abstract(soup):
    res = {}
    abstract_elem = soup.find(class_='abstractInFull')
    if abstract_elem:
        res['abstract'] = {'abstract': get_clean_text(abstract_elem)}
    keywords = []
    chart = soup.find(class_='organizational-chart')
    if chart:
        for e in chart.find_all('h6') + chart.find_all('a'):
            k = get_clean_text(e).strip()
            if k:
                keywords.append({'keyword': k.strip()})
    if keywords:
        res['keywords'] = keywords
    return res


def parse_references(soup):
    res = {}
    references = []
    for ref_elem in soup.find_all(class_='references__item'):
        ref = {}
        ref_note = ref_elem.find(class_='references__note')
        for e in ref_note.find_all('a'):
            if 'href' in e.attrs and 'doi' in e.attrs['href'] and 'google.' not in e.attrs['href']:
                ref['link'] = e.attrs['href']
                if ref['link'][0:5] == '/doi/':
                    ref['doi'] = ref['link'].replace('/doi/', '').lower()
        _ = [w.extract() for w in ref_note.find_all(class_='references__suffix')]
        if ref_note:
            ref['reference'] = get_clean_text(ref_note)
        if ref:
            references.append(ref)
    if references:
        res['references'] = references
    return res
