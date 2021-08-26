import re, bs4
from project.server.main.parsers.strings import get_clean_text, get_orcid, cleanhtml

def parse_fallback_highwire(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    return res

def parse_abstract(soup):
    res = {}

    abstracts = []
    for abstr_elem in soup.find_all('meta', {"name":"citation_abstract"}):
        abstract=None
        if 'content' in abstr_elem.attrs:
            abstract = {"abstract": cleanhtml(abstr_elem['content'])}
        if abstract and 'lang' in abstr_elem.attrs:
            abstract['lang'] = abstr_elem['lang']
        if abstract:
            abstracts.append(abstract)
    if abstracts:
        res["abstract"] = abstracts

    lang_elem = soup.find('meta', {"name":"citation_language"})
    if lang_elem and 'content' in lang_elem.attrs:
        lang = lang_elem['content']
        res["lang"] = lang.lower()
    
    title_elem = soup.find('meta', {"name":"citation_title"})
    if title_elem and 'content' in title_elem.attrs:
        res["title"] = title_elem['content']
    
    elem = soup.find('meta', {"name":"citation_journal_title"})
    if elem and 'content' in elem.attrs:
        res["journal_title"] = elem['content']
    
    elem = soup.find('meta', {"name":"citation_publisher"})
    if elem and 'content' in elem.attrs:
        res["publisher"] = elem['content']

    references = []
    for e in soup.find_all('meta', {"name":"citation_reference"}):
        if 'content' in e.attrs and e['content']:
            references.append( {"reference": e['content']} )
    if references:
        res['references'] = references
    
    keywords = []
    for elem in soup.find_all('meta', {"name":re.compile("citation_keywords|keywords")}):
        if 'content' in elem.attrs:
            for k in re.split(";|,", elem['content']):
                if k.strip():
                    current_k = {'keyword': k.strip()}
                    if current_k not in keywords:
                        keywords.append(current_k)
    if keywords:
        res["keywords"] = keywords

    elem = soup.find('meta', {"name": "citation_online_date"})
    if elem and 'content' in elem.attrs and len(str(elem['content'])) >= 8:
        res['online_date'] = str(elem['content'])

    elem = soup.find('meta', {"name": "citation_publication_date"})
    if elem and 'content' in elem.attrs and len(str(elem['content'])) >= 8:
        res['publication_date'] = str(elem['content'])
    
    elem = soup.find('meta', {"name": "citation_conference_title"})
    if elem and 'content' in elem.attrs:
        res['conference_title'] = elem['content']
        
    return res

def parse_authors(soup):
    res = {}
    authors, affiliations = [], []
    author, current_affiliations = None, []
    for meta in soup.find_all('meta'):
        if meta.attrs.get('name') == "citation_author":
            if author and current_affiliations:
                author['affiliations'] = current_affiliations
            if author:
                authors.append(author)
            author = {"full_name": meta.attrs.get('content')}
            current_affiliations = []
        if meta.attrs.get('name', '').startswith("citation_author_"):
            author_enrichment = meta.attrs['name'].replace("citation_author_", "")
            if author_enrichment == "institution":
                current_affiliation = {"name": meta.attrs.get('content')}
                current_affiliations.append(current_affiliation)
                if current_affiliation not in affiliations:
                    affiliations.append(current_affiliation)
            elif author_enrichment == "email":
                author[author_enrichment] = meta.attrs.get('content')
                author['corresponding'] = True
            elif author_enrichment == "orcid":
                author[author_enrichment] = get_orcid(meta.attrs.get('content'))
            elif meta and meta.attrs:
                author[author_enrichment] = meta.attrs.get('content')

    if author and current_affiliations:
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
