import json

from bs4 import BeautifulSoup
from jsonschema import exceptions, validate

from project.server.main.doi_parser_mapping import MAPPING
from project.server.main.logger import get_logger
import project.server.main.parsers as parsers

logger = get_logger(__name__)
schema = json.load(open('/src/project/server/main/schema.json', 'r'))


def is_empty(res) -> bool:
    return len(res) <= 1


def validate_json_schema(datum: object, _schema: dict) -> bool:
    is_valid = True
    try:
        validate(instance=datum, schema=_schema)
    except exceptions.ValidationError as error:
        is_valid = False
        logger.debug(error)
    return is_valid


def need_parsing(html: str) -> bool:
    if html[0:4] == '%PDF' or html == 'file too large' or (len(html) > 2000000 and '<div' not in html):
        return False
    else:
        return True


def parse(doi: str, html: str):
    logger.debug(f'PARSER -- parsing {doi}')
    res_base = {
        'doi': doi,
        'url': f'http://doi.org/{doi}',
        'sources': ['html']
    }
    if not need_parsing(html=html):
        return res_base
    exec = MAPPING.get(doi[0:7])
    soup = BeautifulSoup(html, 'lxml')
    res = {}
    if exec:
        try:
            logger.debug(f"PARSER -- exec {exec.get('func')}")
            res = exec.get('func')(soup, doi)
        except Exception as e:
            logger.debug(f'PARSER -- FAILED {e}')
    res = apply_fallbacks(doi=doi, soup=soup, current_res=res)
    res = post_treat(current_res=res)
    res.update(res_base)
    is_valid = validate_json_schema(datum=res, _schema=schema)
    if not is_valid:
        logger.error(f'Invalid schema for {doi}')
    return res


def apply_fallbacks(doi, soup, current_res):
    exec = MAPPING.get(doi[0:7], {})
    func_fallbacks = []
    if 'cbs' in exec:
        func_fallbacks += exec.get('cbs', [])
    func_fallbacks += [parsers.parse_fallback_highwire, parsers.parse_fallback_dublincore, parsers.parse_fallback_tags]
    for func in func_fallbacks:
        res = func(soup, doi)
        for field in res:
            if len(current_res.get(field, '')) == 0:
                current_res[field] = res[field]
    return current_res


def post_treat(current_res):
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

    for r in current_res.get('references', []):
        if 'doi' in r and (not r['doi']):
            del r['doi']
    return current_res
