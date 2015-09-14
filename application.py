# -*- coding: utf-8 -*-
__author__ = 'seb'

from flask import Flask, render_template, request, redirect, jsonify, url_for, g
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database import Base, User, Project, Task
from flask import session as login_session
import random, string

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response, flash
import requests

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# fetch the data for the sidebar before every request
@app.before_request
def get_sidebar():
    g.projects = session.query(Project).all()
    g.latest10 = session.query(Task).order_by(Task.id.desc()).limit(10).all()
    print("f")


@app.route('/')
def home():
    return render_template('home.html')


# Project Methods #
@app.route('/project/create', methods=['GET', 'POST'])
def create_project():
    # are we logged in?
    if 'username' not in login_session:
        return redirect('/login')

    # check for POST data
    if request.method == 'POST':
        # create new Project and send it to db
        project = Project(name=request.form['project_name'],
                          user_id=login_session['userid'])
        session.add(project)
        session.commit()
        return redirect(url_for('view_project', project_id=project.id))
    else:
        return render_template('createproject.html')


# only the project name can be edited
@app.route('/project/edit/<int:project_id>/', methods=['GET', 'POST'])
def edit_project(project_id):
    if 'username' not in login_session:
        return redirect('/login')

    # fetch Project by id
    project = session.query(Project) \
        .filter(Project.id == project_id).one()

    # bail if this isn't your project
    if not project.user_id == login_session['userid']:
        flash('These are not the droids you are looking for - redirecting home')
        return render_template('home.html')

    # if data was sumbitted - use it - otherwise show the edit page
    if request.method == 'POST':
        project.name = request.form['project_name']
        session.add(project)
        session.commit()
        return redirect(url_for('view_project', project_id=project.id))
    else:
        return render_template('editproject.html', project=project)


@app.route('/project/delete/<int:project_id>/', methods=['GET', 'POST'])
def delete_project(project_id):
    if 'username' not in login_session:
        return redirect('/login')

    project = session.query(Project) \
        .filter(Project.id == project_id).one()

    # bail if this isn't your project
    if not project.user_id == login_session['userid']:
        flash('Your logged in user does not match the project '
              'you tried to interact with - going home')
        return render_template('home.html')

    if request.method == 'POST':
        session.delete(project)
        session.commit()
        flash('Project has been deleted')
        return redirect(url_for('home'))
    else:
        return render_template('deleteproject.html', project=project)


@app.route('/project/view/<int:project_id>/')
def view_project(project_id):
    project = session.query(Project).\
        filter(Project.id == project_id).one()
    return render_template('viewproject.html', project=project)


# Task Methods #
@app.route('/task/create/<int:project_id>/', methods=['GET', 'POST'])
def create_task(project_id):
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        # why can't I pass the params dict?
        params = {"user_id": 1, "project_id": project_id,
                  "title": request.form['title'],
                  "description": request.form['description']}
        task = Task(user_id=login_session['userid'],
                    project_id=project_id,
                    title=request.form['title'],
                    description=request.form['description'])
        session.add(task)
        session.commit()
        return redirect(url_for('view_project', project_id=project_id))
    else:
        return render_template('createtask.html', project_id=project_id)


@app.route('/task/edit/<int:task_id>/', methods=['GET', 'POST'])
def edit_task(task_id):
    if 'username' not in login_session:
        return redirect('/login')

    task = session.query(Task).filter(Task.id == task_id).one()

    if not task.user_id == login_session['userid']:
        flash('Not your task, mate')
        return render_template('home.html')

    if request.method == 'POST':
        task.title = request.form['title']
        task.description = request.form['description']
        session.add(task)
        session.commit()
        return redirect(url_for('view_project',
                                project_id=task.Project.id))
    else:
        return render_template('edittask.html', task=task)


@app.route('/task/delete/<int:task_id>/', methods=['GET', 'POST'])
def delete_task(task_id):
    if 'username' not in login_session:
        return redirect('/login')

    task = session.query(Task).filter(Task.id == task_id).one()

    if not task.user_id == login_session['userid']:
        flash('Not your task, mate')
        return render_template('home.html')

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


@app.route('/login')
def show_login():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


# copied from UDACITY
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    login_session['userid'] = get_userid(data['email'], data['name'])

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def get_userid(email, name):
    """
    check if user with that email exists and either return id or create it
    """
    user = session.query(User).filter_by(email=email).first()

    if user:
        return user.id
    else:
        user = User(email=email, name=name)
        session.add(user)
        session.commit()
        return user.id


if __name__ == '__main__':
    app.secret_key = "such secret, much wow"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)


