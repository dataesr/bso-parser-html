import os
import requests
import time

from project.server.main.global_parser import parse
from project.server.main.logger import get_logger
from project.server.main.utils_swift import exists_in_storage, get_data_from_ovh, get_filename, set_objects


AFFILIATION_MATCHER_SERVICE = os.getenv('AFFILIATION_MATCHER_SERVICE')
matcher_endpoint_url = f'{AFFILIATION_MATCHER_SERVICE}/enrich_filter'
FRENCH_ALPHA2 = ['fr', 'gp', 'gf', 'mq', 're', 'yt', 'pm', 'mf', 'bl', 'wf', 'tf', 'nc', 'pf']


logger = get_logger(__name__)


def get_matcher_results(publications: list, countries_to_keep: list) -> list:
    r = requests.post(matcher_endpoint_url, json={'publications': publications, 'countries_to_keep': countries_to_keep,
                                                  'queue': 'matcher_short'})
    task_id = r.json()['data']['task_id']
    logger.debug(f'New task {task_id} for matcher')
    for i in range(0, 10000):
        r_task = requests.get(f'{AFFILIATION_MATCHER_SERVICE}/tasks/{task_id}').json()
        try:
            status = r_task['data']['task_status']
        except:
            logger.error(f'Error in getting task {task_id} status : {r_task}')
            status = 'error'
        if status == 'finished':
            return r_task['data']['task_result']
        elif status in ['started', 'queued']:
            time.sleep(2)
            continue
        else:
            logger.error(f'Error with task {task_id} : status {status}')
            return []


def create_task_parse(arg):
    doi = arg.get('doi')
    filename = arg.get('filename')
    if doi is None and filename is None:
        return {'status': 'missing doi or filename'}
    if doi:
        doi = doi.lower()
        filename = get_filename(doi)
    force = arg.get('force', False) 
    if filename:
        if force is False and exists_in_storage('parsed', filename) is True:
            return {'status': 'already parsed'}
        else:
            download_data_html = get_data_from_ovh(filename=filename, container='landing-page-html')
            if download_data_html:
                parsed = parse(doi=download_data_html.get('doi'), html=download_data_html.get('notice'))
                all_parsed = [parsed]
                publications_with_countries = get_matcher_results(publications=all_parsed,
                                                                  countries_to_keep=FRENCH_ALPHA2)
                all_parsed = publications_with_countries['publications']
                all_parsed_filtered = publications_with_countries['filtered_publications']

                set_objects(all_parsed, 'parsed', filename)
                if all_parsed_filtered:
                    set_objects(all_parsed_filtered, 'parsed_fr', filename)
                return parsed
            else:
                logger.debug('Should crawl first')
                return {'status': 'missing html'}
