import time
from project.server.main.global_parser import parse
from project.server.main.utils_swift import get_data_from_ovh, get_filename, exists_in_storage, set_objects
from project.server.main.logger import get_logger

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
                logger.debug("parsing done")
                set_objects([parsed], "parsed", filename)
                return parsed
            else:
                logger.debug("should crawl first")
                return {"status": "missing html"}
