# -*- coding: utf-8 -*-
__author__ = 'seb'

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Restaurant, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

def get_menu_items():
    menuitems = session.query(MenuItem).all()

    for item in menuitems:
        print "Name: " + item.name + " and Price: " + item.price


def get_restaurants():
    """
    :return: html formatted list of restaurants
    """
    html = ""
    restaurants = session.query(Restaurant).all()

    for res in restaurants:
        html += "<h4>" + res.name + "</h4>"
        html += "<a href='localhost:8080/editrestaurant/%s'>edit</a></br>" %\
                res.id
        html += "<a href='localhost:8080/deleterestaurant/%s'>delete</a>" % \
                res.id

    return html

def save_restaurant(name):
    restaurant = Restaurant(name=name)
    session.add(restaurant)
    session.commit()