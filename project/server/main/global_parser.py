import json

from bs4 import BeautifulSoup
from jsonschema import exceptions, validate
from project.server.main.parsers.strings import get_orcid

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

def parse(doi: str, html: str, json: dict, return_input):
    logger.debug(f'PARSER -- parsing {doi}')
    res = {}
    res_base = {
        'doi': doi,
        'url': f'http://doi.org/{doi}',
    }
    if json:
        res_base['sources'] = ['json']
        if return_input:
            res_base['input'] = json
        author_field_correspondance = {'affiliation': 'affiliations', 'given': 'first_name', 'family': 'last_name', 'ORCID': 'orcid'}
        authors = json.get('authors', [])
        if authors:
            for ix, author in enumerate(authors):
                for field in author_field_correspondance:
                    if field in author:
                        new_field = author_field_correspondance[field]
                        author[new_field] = author[field]
                        del author[field]
                author['author_position'] = ix + 1
                if 'sequence' in author:
                    del author['sequence']
                full_name = ''
                if author.get('first_name'):
                    full_name += author.get('first_name').strip()
                if author.get('last_name'):
                    full_name += " " + author.get('last_name').strip()
                if full_name:
                    author['full_name'] = full_name.strip()
                if author.get('orcid'):
                    author['orcid'] = get_orcid(author['orcid'])
                if 'authenticated-orcid' in author:
                    del author['authenticated-orcid']
        res_base.update(json)
    else:
        res_base['sources'] = ['html']

    if html:
        if return_input:
            res_base['input'] = html
        if not need_parsing(html=html):
            return res_base
        _exec = MAPPING.get(doi[0:7])
        soup = BeautifulSoup(html, 'lxml')
        if _exec:
            try:
                logger.debug(f"PARSER -- exec {_exec.get('func')}")
                res = _exec.get('func')(soup, doi)
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
    _exec = MAPPING.get(doi[0:7], {})
    func_fallbacks = []
    if 'cbs' in _exec:
        func_fallbacks += _exec.get('cbs', [])
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
    for aut in authors:
        if 'affiliation' in aut and 'affiliations' not in aut:
            if isinstance(aut['affiliation'], dict):
                aut['affiliations'] = [aut['affiliation']]
            elif isinstance(aut['affiliation'], list):
                aut['affiliations'] = aut['affiliation']
            del aut['affiliation']
    if len(authors) == 1 or len(affiliations) == 1:
        for a in authors:
            current_affiliations = a.get('affiliations', [])
            for aff in affiliations:
                if aff not in current_affiliations:
                    current_affiliations.append(aff)
            if current_affiliations:
                a['affiliations'] = current_affiliations
    for aut in authors:
        if 'affiliations' in aut and isinstance(aut['affiliations'], list):
            for aff in aut['affiliations']:
                if aff not in affiliations:
                    affiliations.append(aff)
    current_res['affiliations'] = affiliations
    has_grant = current_res.get('has_grant', False)
    current_res['has_grant'] = has_grant

    for r in current_res.get('references', []):
        if 'doi' in r and (not r['doi']):
            del r['doi']
    return current_res
