# -*- coding: utf-8 -*-
__author__ = 'seb'

from flask import Flask, render_template, request, redirect, jsonify, url_for, g
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database import Base, User, Project, Task
from functions import *

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.before_request
def get_sidebar():
    g.projects = session.query(Project).all()
    g.latest10 = session.query(Task).order_by(Task.id.desc()).limit(10).all()
    print("f")


@app.route('/')
def home():
    return render_template('home.html')


# ## Project ## #
@app.route('/project/create', methods=['GET', 'POST'])
def create_project():
    if request.method == 'POST':
        # todo read userid from logged in user
        project = Project(name=request.form['project_name'], user_id=1)
        session.add(project)
        session.commit()
        # todo redirect to the newly created project instead of home
        return redirect(url_for('view_project', project_id=project.id))
    else:
        return render_template('createproject.html')


# only the name can be edited
@app.route('/project/edit/<int:project_id>/', methods=['GET', 'POST'])
def edit_project(project_id):
    project = session.query(Project) \
        .filter(Project.id == project_id).one()
    if request.method == 'POST':
        project.name = request.form['project_name']
        session.add(project)
        session.commit()
        return redirect(url_for('view_project', project_id=project.id))
    else:
        return render_template('editproject.html', project=project)


@app.route('/project/delete/<int:project_id>/', methods=['GET', 'POST'])
def delete_project(project_id):
    project = session.query(Project) \
        .filter(Project.id == project_id).one()
    if request.method == 'POST':
        session.delete(project)
        session.commit()
        return redirect(url_for('home'))
        # todo splash "project deleted"
    else:
        return render_template('deleteproject.html', project=project)


@app.route('/project/view/<int:project_id>/')
def view_project(project_id):
    # I'm loading the data for the sidebar so maybe I should use that
    # instead of querying the db twice
    project = session.query(Project).\
        filter(Project.id == project_id).one()
    return render_template('viewproject.html', project=project)


# ## Tasks ## #
@app.route('/task/create/<int:project_id>/', methods=['GET', 'POST'])
def create_task(project_id):
    if request.method == 'POST':
        # todo read userid from logged in user
        # why can't I pass the params dict?
        params = {"user_id": 1, "project_id": project_id,
                  "title": request.form['title'],
                  "description": request.form['description']}
        task = Task(user_id=1,
                    project_id=project_id,
                    title=request.form['title'],
                    description=request.form['description'])
        session.add(task)
        session.commit()
        # todo redirect to the newly created project instead of home
        #return redirect(render_template('viewproject.html',
        #                project_id=project_id))
        return redirect(url_for('view_project', project_id=project_id))
    else:
        return render_template('createtask.html', project_id=project_id)

@app.route('/task/edit/<int:task_id>/', methods=['GET', 'POST'])
def edit_task(task_id):
    task = session.query(Task).filter(Task.id == task_id).one()
    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        session.add(task)
        session.commit()
        # todo add viewtask page and redirect there- make that edit also, JavaS
        return redirect(url_for('view_project',
                                project_id=task.Project.id))
    else:
        return render_template('edittask.html', task=task)


@app.route('/task/delete/<int:task_id>/', methods=['GET', 'POST'])
def delete_task(task_id):
    task = session.query(Task).filter(Task.id == task_id).one()
    if request.method == 'POST':
        session.delete(task)
        session.commit()
        return redirect(url_for('view_project',
                                project_id=task.Project.id))
    else:
        return render_template('deletetask.html', task=task)


# JSON functions

# JSON view Task
@app.route('/task/<int:task_id>/JSON')
def show_task_json(task_id):
    task = session.query(Task).filter_by(id=task_id).one()
    return jsonify(task=task.serialize)


# JSON view Project
@app.route('/project/<int:project_id>/JSON')
def show_project_json(project_id):
    project = session.query(Project).filter_by(id=project_id).one()
    return jsonify(project=project.serialize)


# JSON list Projects
@app.route('/projects/JSON')
def show_all_projects():
    projects = session.query(Project).all()
    return jsonify(projects=[p.serialize for p in projects])

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)


"""
Main page that prints all data. Really?


"""