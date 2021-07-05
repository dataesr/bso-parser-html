import time
import requests
import os
from project.server.main.global_parser import parse
from project.server.main.utils_swift import get_data_from_ovh, get_filename, exists_in_storage, set_objects
from project.server.main.logger import get_logger


AFFILIATION_MATCHER_SERVICE = os.getenv('AFFILIATION_MATCHER_SERVICE')
matcher_endpoint_url = f'{AFFILIATION_MATCHER_SERVICE}/enrich_filter'
FRENCH_ALPHA2 = ["fr", "gp", "gf", "mq", "re", "yt", "pm", "mf", "bl", "wf", "tf", "nc", "pf"]


logger = get_logger()

def create_task_parse(arg):
    doi = arg.get('doi')
    filename = arg.get('filename')
    if doi is None and filename is None:
        return {"status": "missing doi or filename"}
    if doi:
        doi = doi.lower()
        filename = get_filename(doi)
    force = arg.get('force', False) 
    if filename:
        if (force is False) and (exists_in_storage("parsed", filename) is True):
            return {"status": "already parsed"}
        else:
            download_data_html = get_data_from_ovh(filename = filename, container = "landing-page-html")
            if download_data_html:
                parsed = parse(download_data_html.get('doi'), download_data_html.get('notice'))
                all_parsed = [parsed]
    
                publications_with_countries = requests.post(matcher_endpoint_url, json={'publications': all_parsed, 'countries_to_keep': FRENCH_ALPHA2}).json()
                all_parsed = publications_with_countries['publications']
                all_parsed_filtered = publications_with_countries['filtered_publications']

                set_objects(all_parsed, "parsed", filename)
                if all_parsed_filtered:
                    set_objects(all_parsed_filtered, "parsed", "fr/"+filename)
                return parsed
            else:
                logger.debug("should crawl first")
                return {"status": "missing html"}
