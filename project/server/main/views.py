import dateutil.parser
import redis

from flask import Blueprint, current_app, jsonify, render_template, request
from rq import Connection, Queue

from project.server.main.logger import get_logger
from project.server.main.tasks import create_task_parse
from project.server.main.utils_swift import conn

main_blueprint = Blueprint('main', __name__,)
logger = get_logger(__name__)
REDIS_QUEUE = 'parser'


@main_blueprint.route('/', methods=['GET'])
def home():
    return render_template('main/home.html')


@main_blueprint.route('/parse', methods=['POST'])
def run_task_parse():
    args = request.get_json(force=True)
    logger.debug(args)
    with Connection(redis.from_url(current_app.config['REDIS_URL'])):
        q = Queue(REDIS_QUEUE, default_timeout=21600)
        task = q.enqueue(create_task_parse, args)
    response_object = {
        'status': 'success',
        'data': {
            'task_id': task.get_id()
        }
    }
    return jsonify(response_object), 202


@main_blueprint.route('/parse_all', methods=['POST'])
def run_task_parse_all():
    args = request.get_json(force=True)
    logger.debug(args)
    with Connection(redis.from_url(current_app.config['REDIS_URL'])):
        q = Queue(REDIS_QUEUE, default_timeout=216000)
        task = q.enqueue(create_task_parse_all, args)
    response_object = {
        'status': 'success',
        'data': {
            'task_id': task.get_id()
        }
    }
    return jsonify(response_object), 202


def create_task_parse_all(args):
    modified_date_start = args.get('modified_date_start', '0')
    modified_date_end = args.get('modified_date_start', '9999')
    force = args.get('force', True)
    keep_going = True
    marker = None
    ix = 0
    nb_tasks = 0
    while keep_going:
        ix += 1
        data = []
        x = conn.get_container('landing-page-html', marker=marker)
        for e in x[1]:
            last_modified = dateutil.parser.parse(e['last_modified']).isoformat()
            if modified_date_start <= last_modified < modified_date_end:
                data.append(e['name'])
        keep_going = len(x[1]) == 10000
        marker = x[1][-1]['name']
        for filename in data:
            with Connection(redis.from_url(current_app.config['REDIS_URL'])):
                q = Queue(REDIS_QUEUE, default_timeout=21600)
                q.enqueue(create_task_parse, {'filename': filename, 'force': force})
            nb_tasks += 1
    response_object = {'nb_tasks': nb_tasks}
    return response_object


@main_blueprint.route('/tasks/<task_id>', methods=['GET'])
def get_status(task_id):
    with Connection(redis.from_url(current_app.config['REDIS_URL'])):
        q = Queue(REDIS_QUEUE)
        task = q.fetch_job(task_id)
    if task:
        response_object = {
            'status': 'success',
            'data': {
                'task_id': task.get_id(),
                'task_status': task.get_status(),
                'task_result': task.result,
            },
        }
    else:
        response_object = {'status': 'error'}
    return jsonify(response_object)
