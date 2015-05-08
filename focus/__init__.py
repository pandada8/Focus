from flask import Flask, jsonify, render_template
from flask.ext.login import LoginManager
from werkzeug.routing import AnyConverter
from pymongo import MongoClient
import os
from .errors import APIError


app = Flask(__name__)
app.config.from_pyfile('config.py')

if "config" in os.environ and os.environ['config']:
    app.config.from_envvar("config")

loginmanager = LoginManager()

loginmanager.init_app(app)

mongodb = MongoClient(app.config['MONGO_URI'])[app.config['MONGO_DB']]


@app.errorhandler(APIError)
def print_the_error(error):
    response = jsonify(error.to_dict())
    # return normal 200 code so we needn't deal the problem in the frontend
    return response


@app.errorhandler(404)
def Page_not_find(error):
    return render_template('404.html')


def find_self_projects(project_type):
    return [i for i in mongodb.meta.find() if i.project_type == project_type]


def get_view_for_proj(project_id):
    t = mongodb.meta.find_one({'hmac': project_id})['project_type']
    try:
        return getattr(views, t)
    except AttributeError:
        return None


class ProjectType(AnyConverter):

    def __init__(self, url_map, *items):
        items = [i['hmac'] for i in mongodb.meta.find({"project_type": items[0]})]
        super(ProjectType, self).__init__(url_map, *items)

app.url_map.converters['proj'] = ProjectType


def update_map():
    for i in app.url_map.iter_rules():
        if "<proj(" in i.rule:
            i.compile()
            print("update the route for {}".format(i.rule))


from . import views
from . import admin
from . import projects
