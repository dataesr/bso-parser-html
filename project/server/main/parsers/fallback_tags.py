import re, bs4, string
from project.server.main.parsers.strings import get_clean_text

def parse_fallback_tags(soup, doi):

    res = {'doi': doi}
    affiliations = []
    affiliation_regex = re.compile("affili|institution")
    potential_elts = []
    potential_elts += soup.find_all(id= affiliation_regex) 
    potential_elts += soup.find_all(class_= affiliation_regex)

    potential_aff = []

    for p in potential_elts:
        current_name = get_clean_text(p)
        potential_aff.append(current_name)

    #for e in soup.find_all("sup"):
    #    if len(get_clean_text(e)) == 1:
    #        potential_aff.append(get_clean_text(e.next.next))

    for current_name in potential_aff:
        for k in ["Affiliation", "Author Information"]:
            current_name = current_name.replace(k, "").strip()
        if current_name.startswith(';'):
            continue
        if len(current_name.split(' ')) < 2:
            continue
        if len(current_name) > 2:
            current_aff = {'name': current_name}
            if current_aff not in affiliations:
                affiliations.append(current_aff)
    if affiliations:
        res['affiliations'] = affiliations

    return res
