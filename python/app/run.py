#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random
import logging
import os
import sqlite3
from libs.progress import Progress
from datetime import datetime
from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from prometheus_flask_exporter import PrometheusMetrics

current_dir = os.path.dirname(os.path.abspath(__file__))
database_file = "sqlite:///{}".format(os.path.join(current_dir, "hellos.db"))
database_config = os.getenv('MYSQL_URI', database_file)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = database_config
print("Using DB: ", database_config)

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

random_number = random.randint(1048576,16777215)
hex_number = str(hex(random_number))[2:]

labels = {"app_version": os.getenv('APP_VERSION', '1.0.0'), 
          "app_name" : "acend-awesome-python"}
metrics = PrometheusMetrics(app, static_labels=labels)

db = SQLAlchemy(app)

class Hello(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    frontend = db.Column(db.String(80), nullable=False)
    created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return "<Name: {}>".format(self.title)

db.create_all()

@app.route("/")
def index():
    return render_template('index.jinja', hex_number=hex_number)

@app.route("/hellos", methods=['GET'])
def get_hellos():
    try:
        result = []
        for hello in Hello.query.all():
            result.append({'id': hello.id, 'name': hello.name, 'frontend': hello.frontend, 'created': hello.created})
        return jsonify(result)
    except Exception as e:
        print("Failed fetch hellos")
        print(e)

@app.route("/hellos/<string:name>", methods=['POST'])
def add_hello(name):
    try:
        if name and request.method == 'POST':
            hello = Hello(name=name, frontend=os.getenv('HOSTNAME', 'not-set'))
            db.session.add(hello)
            db.session.commit()
            resp = jsonify('Hello added successfully!')
            resp.status_code = 200
            return resp
        else:
            return not_found()
    except Exception as e:
        print("Failed to add a hello")
        print(e)
        return e

@app.route("/pod/")
def pod():
    return os.getenv('HOSTNAME', 'not-set')

@app.route("/health")
def health():
    return "ok"

@app.route("/progress")
def progress():
    progress = Progress()
    progress.checkProgress(Hello)
    return render_template("progress.jinja", lab=progress.lab)

if __name__ == "__main__":
    app.run(host='0.0.0.0', threaded=True)
