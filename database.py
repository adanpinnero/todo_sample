# -*- coding: utf-8 -*-
__author__ = 'seb'
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

"""
create sql alchemy models for User Category Item
    look at code from udacity
run setup to populate db with one entry for each
"""

#  common base class for all Models(?) to inherit from
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    categories = relationship("Category", backref="User")
    items = relationship("Item", backref="User")


class Category(Base):
    __tablename__ = "category"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    description = Column(String(450), nullable=False)

    items = relationship("Item", backref="Category")


class Item(Base):
    __tablename__ = "item"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    category_id = Column(Integer, ForeignKey("category.id"))
    title = Column(String(250), nullable=False)
    description = Column(String(450), nullable=False)
    is_done = Column(Boolean, unique=False, default=False)


engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)