import re, bs4
from project.server.main.parsers.strings import get_clean_text

# authors / affiliations handled with fallback_highwire

# doi 10.1088
def parse_iop(soup, doi):
    res = {"doi": doi}
    res.update(parse_abstract(soup))
    return res

def parse_abstract(soup):
    res = {}
    abstr_elem = soup.find(class_=re.compile('abstract'))
    if abstr_elem:
        res['abstract'] = [{'abstract': get_clean_text(abstr_elem)}]

    for e in soup.find_all(itemprop=re.compile("date.*")):
        date_type = e.attrs['itemprop'].lower().replace('date', '')+'_date'
        date_value = get_clean_text(e)
        res[date_type] = date_value
    return res
