import gzip
import hashlib
import os
import pandas as pd
import swiftclient

from io import BytesIO, TextIOWrapper

from project.server.main.logger import get_logger

logger = get_logger(__name__)

user = f'{os.getenv("OS_TENANT_NAME")}:{os.getenv("OS_USERNAME")}'
key = os.getenv("OS_PASSWORD")
project_id = os.getenv("OS_TENANT_ID")
project_name = os.getenv("OS_PROJECT_NAME")

conn = swiftclient.Connection(
    authurl='https://auth.cloud.ovh.net/v3',
    user=user,
    key=key,
    os_options={
            'user_domain_name': 'Default',
            'project_domain_name': 'Default',
            'project_id': project_id,
            'project_name': project_name,
            'region_name': 'GRA'},
    auth_version='3'
)


def exists_in_storage(container, filename):
    try:
        conn.head_object(container, filename)
        return True
    except:
        return False


def get_hash(x):
    return hashlib.md5(x.encode('utf-8')).hexdigest()


def get_filename(doi):
    init = doi.split('/')[0]
    notice_id = f'doi{doi}'
    id_hash = get_hash(notice_id)
    filename = f'{init}/{id_hash}.json.gz'
    return filename


def get_data_from_ovh(doi=None, filename=None, container='landing-page-html'):
    if doi:
        filename = get_filename(doi)
    if exists_in_storage(container, filename) is False:
        logger.debug("ERROR : missing file")
        return {}
    if filename is None:
        logger.debug("ERROR : missing file")
        return {}
    df_notice = pd.read_json(BytesIO(conn.get_object(container, filename)[1]), compression='gzip')
    return df_notice.to_dict(orient='records')[0]


def get_objects(container, path):
    try:
        df = pd.read_json(BytesIO(conn.get_object(container, path)[1]), compression='gzip')
    except:
        df = pd.DataFrame([])
    return df.to_dict('records')


def set_objects(all_objects, container, path):
    logger.debug(f'Setting object {container} {path}')
    if isinstance(all_objects, list):
        all_notices_content = pd.DataFrame(all_objects)
    else:
        all_notices_content = all_objects
    gz_buffer = BytesIO()
    with gzip.GzipFile(mode='w', fileobj=gz_buffer) as gz_file:
        all_notices_content.to_json(TextIOWrapper(gz_file, 'utf8'), orient='records')
    conn.put_object(container, path, contents=gz_buffer.getvalue())
    logger.debug('Done')
    return


def delete_folder(cont_name, folder):
    cont = conn.get_container(cont_name)
    for n in [e['name'] for e in cont[1] if folder in e['name']]:
        print(n)
        conn.delete_object(cont_name, n)
