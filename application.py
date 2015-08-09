# -*- coding: utf-8 -*-
__author__ = 'seb'

from flask import Flask, render_template, request, redirect, jsonify, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base, User, Category, Item

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()





if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)