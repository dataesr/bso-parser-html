import decimal
import json
import os

from flask import Flask
from flask_bootstrap import Bootstrap
from flask.json import JSONEncoder
from datetime import datetime

bootstrap = Bootstrap()


def create_app():
    app = Flask(
        __name__,
        template_folder='../client/templates',
        static_folder='../client/static'
    )
    app_settings = os.getenv("APP_SETTINGS")
    app.config.from_object(app_settings)
    app.json_encoder = CustomJSONEncoder
    bootstrap.init_app(app)
    from project.server.main.views import main_blueprint
    app.register_blueprint(main_blueprint)
    app.shell_context_processor({'app': app})
    return app


class CustomJSONEncoder(JSONEncoder):
    """Redefine default JSON encoder."""
    def default(self, obj):
        """Default."""
        try:
            if isinstance(obj, datetime):
                datetime_format = "%Y-%m-%dT%H:%M:%S"
                return obj.strftime(datetime_format)
            elif isinstance(obj, decimal.Decimal):
                return str(obj)
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)


def from_mongo(cursor):
    """Return a Python."""
    return json.loads(json.dumps(cursor))
