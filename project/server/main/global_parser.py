import copy
import json
from bs4 import BeautifulSoup
from project.server.main.doi_parser_mapping import MAPPING
import project.server.main.parsers as parsers
from project.server.main.logger import get_logger
from jsonschema import exceptions, validate
    
schema = json.load(open('/src/project/server/main/schema.json', 'r'))

logger = get_logger()

def is_empty(res):
    if len(res) <= 1:
        return True
    return False

def validate_json_schema(datum: object, schema: dict) -> bool:
    is_valid = True
    try:
        validate(instance=datum, schema=schema)
    except exceptions.ValidationError as error:
        is_valid = False
        logger.debug(error)
    return is_valid

def need_parsing(html):
    if html[0:4] == "%PDF":
        return False

    if len(html) > 2000000 and ('<div' not in html):
        return False

    if html == 'file too large':
        return False
    return True

def parse(doi, html, publisher=None):
    logger.debug(f"PARSER -- parsing {doi}")
    res_base = {
        'doi': doi,
        'url': f'http://doi.org/{doi}',
        'sources': ['html']
    }
    if not need_parsing(html):
        return res

    exec = MAPPING.get(doi[0:7])
    soup = BeautifulSoup(html, 'lxml')
    res = {}
    if exec:
        try:
            logger.debug(f"PARSER -- exec {exec.get('func')}")
            res = exec.get('func')(soup, doi)
        except Exception as e:
            logger.debug(f"PARSER -- FAILED {e}")
            # soup2 = BeautifulSoup(html, 'html.parser')
            # res = exec.get('func')(soup2)
    res = apply_fallbacks(doi, soup, res)
    res = post_treat(doi, soup, res)
    res.update(res_base)
    is_valid = validate_json_schema(datum = res, schema=schema)
    logger.debug(f"is valid {is_valid}")
    return res

def apply_fallbacks(doi, soup, current_res):
    exec = MAPPING.get(doi[0:7], {})
    func_fallbacks = []
    
    if "cbs" in exec:
        func_fallbacks += exec.get("cbs", []) 
    func_fallbacks += [parsers.parse_fallback_highwire, parsers.parse_fallback_dublincore, parsers.parse_fallback_tags]
    
    for func in func_fallbacks:
        res = func(soup, doi)
        for field in res:
            #print(field, flush=True)
            #print(res[field], flush=True)
            #print(current_res.get(field, ''), flush=True)
            if len(current_res.get(field, '')) == 0:
                #print(f'replacing field {field} with fallback for doi {doi}', flush=True)
                current_res[field] = res[field]
    return current_res

def post_treat(doi, soup, current_res):
    authors = current_res.get('authors', [])
    affiliations = current_res.get('affiliations', [])
    if len(authors) == 1 or len(affiliations) == 1:
        for a in authors:
            current_affiliations = a.get('affiliations', [])
            for aff in affiliations:
                if aff not in current_affiliations:
                    current_affiliations.append(aff)
            if current_affiliations:
                a['affiliations'] = current_affiliations
    
    has_grant = current_res.get('has_grant', False)
    current_res['has_grant'] = has_grant

    return current_res

