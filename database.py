# -*- coding: utf-8 -*-
__author__ = 'seb'
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


#  common base class for all Models(?) to inherit from
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    project = relationship("Project", backref="User")
    tasks = relationship("Task", backref="User")


class Project(Base):
    __tablename__ = "project"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    name = Column(String(450), nullable=False)

    tasks = relationship("Task", backref="Project")

    # property is used for JSON API
    @property
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
        }


class Task(Base):
    __tablename__ = "task"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    project_id = Column(Integer, ForeignKey("project.id"))
    title = Column(String(250), nullable=False)
    description = Column(String(450), nullable=True)
    is_done = Column(Boolean, unique=False, default=False)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'project_id': self.project_id,
            'title': self.title,
            'description': self.description,
            'is_done': self.is_done
        }


engine = create_engine('sqlite:///catalog.db')

Base.metadata.create_all(engine)