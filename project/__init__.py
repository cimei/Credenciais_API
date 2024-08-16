# __init__.py dentro da pasta project

import os
import locale
from flask import Flask,render_template,url_for,redirect

from shutil import rmtree

TOP_LEVEL_DIR = os.path.abspath(os.curdir)


app = Flask (__name__, static_url_path=None, instance_relative_config=True, static_folder='/app/project/static')

app.config.from_pyfile('flask.cfg')

app.static_url_path=app.config.get('STATIC_PATH')

locale.setlocale( locale.LC_ALL, '' )

package_dir = os.path.dirname(os.path.abspath(__file__))
static = os.path.join(package_dir, "static")
app.static_folder=static

## blueprints - registros

from project.core.views import core
from project.error_pages.handlers import error_pages

from project.envio.views import envio


app.register_blueprint(core)
app.register_blueprint(error_pages)

app.register_blueprint(envio,url_prefix='/envio')

