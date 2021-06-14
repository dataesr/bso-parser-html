import re, bs4
from project.server.main.parsers.strings import get_clean_text, cleanhtml

def parse_fallback_dublincore(soup, doi):
    res = {"doi": doi}
    # res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    return res

def parse_abstract(soup):
    res = {}

    abstracts = []
    for abstr_elem in soup.find_all('meta', {"name":"DC.Description"}):
        abstract=None
        if 'content' in abstr_elem.attrs:
            abstract = {"abstract": cleanhtml(abstr_elem['content'])}
        if abstract and 'lang' in abstr_elem.attrs:
            abstract['lang'] = abstr_elem['lang']
        if abstract:
            abstracts.append(abstract)
    if abstracts:
        res["abstract"] = abstracts

    lang_elem = soup.find('meta', {"name":"DC.language"})
    if lang_elem and 'content' in lang_elem.attrs:
        lang = lang_elem['content']
        res["lang"] = lang.lower()
    
    title_elem = soup.find('meta', {"name":"DC.title"})
    if title_elem and 'content' in title_elem.attrs:
        res["title"] = title_elem['content']
    
    elem = soup.find('meta', {"name":"DC.publisher"})
    if elem and 'content' in elem.attrs:
        res["publisher"] = elem['content']

    keywords = []
    for elem in soup.find_all('meta', {"name":re.compile("DC.subject")}):
        if 'content' in elem.attrs:
            for k in re.split(";|,", elem['content']):
                current_k = {'keyword': k.strip()}
                if current_k not in keywords:
                    keywords.append(current_k)
    if keywords:
        res["keywords"] = keywords

    elem = soup.find('meta', {"name": "DC.date"})
    if elem and 'content' in elem.attrs:
        res['publication_date'] = elem['content']
    
    return res
