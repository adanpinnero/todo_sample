# -*- coding: utf-8 -*-
__author__ = 'seb'
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Shelter(Base):
    __tablename__ = 'shelter'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)





class Puppy(Base):
    __tablename__ = 'puppy'



