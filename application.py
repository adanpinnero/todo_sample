# -*- coding: utf-8 -*-
__author__ = 'seb'

from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, User, Project, Task

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
def home():
    projects = session.query(Project).all()

    return render_template('home.html', projects=projects)


@app.route('/project/create')
def create_project():
    return render_template('createproject.html')


@app.route('/project/edit/<int:project_id>/')
def edit_project(project_id):
    return render_template('editproject.html')


@app.route('/project/delete/<int:project_id>/')
def delete_project(project_id):
    return render_template('deleteproject.html')


@app.route('/task/create')
def create_task():
    return render_template('createtask.html')


@app.route('/task/edit/<int:task_id>/')
def edit_task(task_id):
    return render_template('edittask.html')


@app.route('/task/delete/<int:task_id>/')
def delete_task(task_id):
    return render_template('deletetask.html')



if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)


"""
Main page that prints all data. Really?


"""