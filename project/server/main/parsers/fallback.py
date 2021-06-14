from bs4 import *
import re, bs4
from project.server.main.parsing.country_detect import detect_country
from project.server.main.parsing.strings import get_clean_text, keep_digits


# doi 10.1515
def fallback1(soup):

    countries = []

    authors, affiliations =[], []

    potential_elts = []

    for kw in ['affiliation', 'affiliations', 'aff-overlay', 'author-tooltip-affiliation','morearticleinfo', 'author-info',\
            'author-tooltip-affiliation', 'author-affiliation', 'authorAffiliation', 'contentContribs', 'expandable-author', \
            'PublicationsDetailBold', 'aff', 'org', 'content-header__institution', 'article-author-affilitation']:
        for elt in soup.find_all(class_=kw):
            potential_elts.append(elt)

    for elt in soup.find_all('span', {'id':re.compile('affilia.*')}):
        potential_elts.append(elt)
    
    for elt in soup.find_all('div', {'id':re.compile('cAffi')}):
        potential_elts.append(elt)

    for elt in soup.find_all('div', {'id':re.compile('.*auteur.*')}):
        potential_elts.append(elt)
    
    for elt in soup.find_all('meta', {'name':re.compile('.*institution.*')}):
        potential_elts.append(elt)
    
    for elt in potential_elts:
        structure_name = get_clean_text(elt).strip()
        try:
            if len(structure_name) < 2 and 'content' in elt.attrs:
                structure_name = elt.attrs['content']
        except:
            pass
        if len(structure_name) > 0:
            current_countries = detect_country(structure_name)
            affiliations.append({'structure_name': structure_name, 'countries': current_countries})
            countries += current_countries
    countries = list(set(countries))

    return {'authors_from_html':authors, 'affiliations_complete': affiliations,  'countries':countries}

        
def fallback2(soup):
    countries = []
    affiliations = []
    authors = []

    for e in soup.find_all(itemtype="http://schema.org/Organization"):
        for c in e.children:
            structure_name = get_clean_text(c)
            try:
                if len(structure_name)<2 and attrs in c and  'content' in c.attrs:
                    structure_name = c.attrs['content']
            except:
                pass

            if len(structure_name)>2 and 'springer' not in structure_name.lower():
                current_countries = detect_country(structure_name)
                countries += current_countries
                affil = {'structure_name': structure_name, 'countries': current_countries}
                if affil not in affiliations:
                    affiliations.append(affil)

    for e in soup.find_all('meta', {'name': 'citation_author_institution'}):
        structure_name = e['content']
        current_countries = detect_country(structure_name)
        countries += current_countries
        affil = {'structure_name': structure_name, 'countries': current_countries}
        if affil not in affiliations:
            affiliations.append(affil)

    try:
        abstract = soup.find('meta', {'name': 'citation_abstract'})['content']
    except:
        pass

    try:
        keywords = [k.strip() for k in soup.find('meta', {'name': 'citation_keywords'})['content'].split(';')]
    except:
        pass

    countries = list(set(countries))
    return {'authors_from_html':authors, 'affiliations_complete': affiliations,  'countries':countries, 'abstract': abstract, 'keywords': keywords}
