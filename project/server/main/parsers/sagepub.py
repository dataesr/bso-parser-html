import re, bs4
from project.server.main.parsers.strings import get_clean_text, get_orcid, get_doi


# doi 10.1177
def parse_sagepub(soup, doi):
    res = {"doi": doi}
    res.update(parse_authors(soup))
    res.update(parse_abstract(soup))
    res.update(parse_references(soup))
    return res

def parse_authors(soup):
    res = parse_authors1(soup)
    if not res.get('affiliations'):
        return parse_authors2(soup)
    return res

def parse_authors1(soup):
    res = {}

    authors = []
    affiliations = []

    affiliations_dict = {}
    for aff in soup.find_all(class_=re.compile('affiliation')):
        sup = aff.find('sup')
        if sup:
            aff_id = get_clean_text(sup)
        else:
            aff_id = len(affiliations_dict)
        _ = [k.extract() for k in aff.find_all("sup")]
        affiliations_dict[aff_id] = {"name": get_clean_text(aff)}
    affiliations = list(affiliations_dict.values())


    for elt in soup.find_all(class_="contribDegrees"):
        author = {}
        current_affiliations = []
        for aff in elt.find_all("sup"):
            aff_id = get_clean_text(aff)

            if aff_id in affiliations_dict:

                current_aff = affiliations_dict[aff_id]
                current_affiliations.append(current_aff)

        if current_affiliations:
            author['affiliations'] = current_affiliations

        a_elem = elt.find("a", href=re.compile('orcid'))
        if a_elem:
            author['orcid'] = get_orcid(a_elem['href'])

        name_e = elt.find('a', href=re.compile('%2C'))
        if name_e:
            sp = re.sub(".*=","",name_e['href']).replace('+', ' ').split('%2C')
            if len(sp) == 2:
                author['first_name'] = sp[1].strip()
                author['last_name'] = sp[0].strip()

        full_name_e = elt.find(class_="entryAuthor")
        if full_name_e:
            author['full_name'] = get_clean_text(full_name_e)

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
    
    authors = []
    affiliations = []
    for elt in soup.find_all(class_="authorLayer"):
        author = {}
        current_affiliations = []
        for aff in elt.find_all(class_="aff-newLine"):
            if aff.next.next:
                current_aff = {"name": aff.next.next}
                current_affiliations.append(current_aff)
                if current_aff not in affiliations:
                    affiliations.append(current_aff)

        if current_affiliations:
            author['affiliations'] = current_affiliations

        a_elem = elt.find("a", href=re.compile('orcid'))
        if a_elem:
            author['orcid'] = get_orcid(a_elem['href'])

        name_e = elt.find('a', href=re.compile('%2C'))
        if name_e:
            sp = re.sub(".*=","",name_e['href']).replace('+', ' ').split('%2C')
            if len(sp) == 2:
                author['first_name'] = sp[1].strip()
                author['last_name'] = sp[0].strip()

        full_name_e = elt.find(class_="entryAuthor")
        if full_name_e:
            author['full_name'] = get_clean_text(full_name_e)

        if author:
            authors.append(author)


    for ix, a in enumerate(authors):
        a['author_position'] = ix+1

    if affiliations:
        res['affiliations'] = affiliations
    if authors:
        res['authors'] = authors
    return res

def parse_abstract(soup):
    res = {}
    abstracts = []
    for resume_elem in soup.find_all(class_="abstractSection abstractInFull"):
        abstract = {}
        abstract['abstract'] = get_clean_text(resume_elem)
        if abstract:
            abstracts.append(abstract)
    if abstracts:
        res['abstracts'] = abstracts
        

        
    keywords = []
    for k in soup.find_all('a', href = re.compile('keyword')):
        keywords.append({'keyword': get_clean_text(k)})
    if keywords:
        res['keywords'] = keywords
        
    for dates_elem in soup.find_all(class_="published-dates"):
        for br in dates_elem.find_all('br'):
            br.append(';')
        for b in get_clean_text(dates_elem).split(';'):
            #print(b)
            sp = b.split(':')
            #print(sp)
            #print(len(sp))
            if len(sp) == 2:
                date_type = sp[0].lower().replace('article', '').replace('issue', '').strip().replace(' ', '_')
                date_value = sp[1].replace(';', '').strip()
                if date_type and date_value:
                    res[date_type+'_date'] = date_value
        
                
    ack = soup.find(class_="acknowledgement")
    if ack :
        ack_str = get_clean_text(ack).replace('Acknowledgments', '').strip()
        res['acknowledgments'] = [{'acknowledgment': ack_str}]
        
    for e in soup.find_all(class_="NLM_fn"):
        if "Funding" in get_clean_text(e):
            res['fundings'] = [{'funding': get_clean_text(e).replace('Funding',"").strip()}]
   
    return res



def parse_references(soup):
    res = {}
    references = []

    for ref_elem in soup.find_all(id=re.compile("bibr")):
        ref = {}
        for a_elem in ref_elem.find_all('a'):
            if 'doi.org' in a_elem.attrs.get('href', ''):
                ref['link'] = a_elem.attrs['href']
                ref['doi'] = get_doi(a_elem.attrs['href'])
            elif '/document/' in a_elem.attrs.get('href', '')[0:10]:
                ref['link'] = "https://ieeexplore.ieee.org"+a_elem.attrs['href']
        current_ref = get_clean_text(ref_elem)
        if current_ref and len(current_ref)>10:
            ref['reference'] = current_ref
        elif 'data-referenceslink' in ref_elem.attrs:
            ref['reference'] = get_clean_text(ref_elem['data-referenceslink'])
        if ref:
            references.append(ref)
    if references:
        res["references"] = references

    return res
