import re, bs4
from project.server.main.parsers.strings import get_clean_text, keep_digits


# doi 10.1051
def parse_aanda(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    return res

def parse_authors(soup):
    res = {}
    affiliations_dict = {}
    affiliations_elem = soup.find(class_="aff")
    aff_id = 0
    if affiliations_elem:
        for e in list(affiliations_elem.children):
            if e.name=='sup':
                aff_id = get_clean_text(e)
            txt = get_clean_text(e)
            if e.name is None and txt:
                affiliations_dict[aff_id] = {'name': txt}

    affiliations = list(affiliations_dict.values())
    if affiliations:
        res["affiliations"] = affiliations
        
    corresp_elem = soup.find(class_="corresp")
    aff_id = 0
    if corresp_elem:
        for e in list(corresp_elem.children):
            if e.name=='sup':
                aff_id = get_clean_text(e)
            txt = get_clean_text(e)
            if '@' in txt:
                affiliations_dict[aff_id] = {'name': txt}
    authors_elem = None
    first_author_elem = soup.find(class_="author")
    if first_author_elem:
        authors_elem = first_author_elem.parent
        
    if authors_elem is None:
        return res
    
    authors = []
    none_authors_has_affiliation = True
    author = None
    for tag in authors_elem.find_all():
        if 'author' in tag.attrs.get('class', []):
            # include the previous author if not empty
            if author:
                authors.append(author)
            author = {"full_name": get_clean_text(tag)}
            current_affiliations = []
        if tag.name == "sup":
            for aff_id in get_clean_text(tag).split(','):
                if aff_id in affiliations_dict:
                    if '@' not in affiliations_dict[aff_id]['name']:
                        current_affiliations.append(affiliations_dict[aff_id])
                    else:
                        author['email'] = affiliations_dict[aff_id]['name'].lower().replace("corresponding author","")
                        author['corresponding'] = True
            if current_affiliations:
                author['affiliations'] = current_affiliations
                none_authors_has_affiliation = False
    # include the last author
    if author and author not in authors:
        authors.append(author)
    
    if none_authors_has_affiliation and affiliations:
        for a in authors:
            a['affiliations'] = affiliations
            
    for ix, a in enumerate(authors):
        a['author_position'] = ix+1
    
    if authors:
        res["authors"] = authors
        
    return res
    
def parse_abstract(soup):
    res = {}
    abstract_elem = soup.find("a", {"name": "abs"})
    if abstract_elem:
        for e in abstract_elem.next_elements:
            if e.name=="p":
                res['abstract'] = {'abstract': get_clean_text(e)}
                get_clean_text(e)
                break
                
    keywords = []
    kword_elem = soup.find(class_="kword")
    if kword_elem:
        _ = [e.extract() for e in kword_elem.find_all(class_="span")]
        kwords = get_clean_text(kword_elem).replace('Key words:','').split('/')
        for k in kwords:
            if k.strip():
                keywords.append({"keyword": k.strip()})
    if keywords:
        res["keywords"] = keywords

    return res
