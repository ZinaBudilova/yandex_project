import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import enum


basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class DataType(enum.Enum):
    FILE = "FILE"
    FOLDER = "FOLDER"


class Items(db.Model):
    __tablename__ = "items"
    id = db.Column(db.String(36), primary_key=True, nullable=False)
    type = db.Column(db.Enum(DataType), nullable=False)
    size = db.Column(db.Integer)
    url = db.Column(db.String(255))
    updateDate = db.Column(db.String(26), nullable=False)
    parentId = db.Column(db.String(36))

    def __init__(self, id, type, size, url, updateDate, parentId):
        self.id = id
        self.type = type
        self.size = size
        self.url = url
        self.updateDate = updateDate
        self.parentId = parentId


class Children(db.Model):
    __tablename__ = "children"
    parentId = db.Column(db.String(36), nullable=False)
    childId = db.Column(db.String(36), nullable=False, primary_key=True)

    def __init__(self, parentId, childId):
        self.parentId = parentId
        self.childId = childId


class History(db.Model):
    __tablename__ = "history"
    id = db.Column(db.String(36), nullable=False)
    type = db.Column(db.Enum(DataType), nullable=False)
    size = db.Column(db.Integer)
    url = db.Column(db.String(255))
    updateDate = db.Column(db.String(26), nullable=False)
    parentId = db.Column(db.String(36))
    key = db.Column(db.String(63), primary_key=True, nullable=False)

    def __init__(self, id, type, size, url, updateDate, parentId):
        self.id = id
        self.type = type
        self.size = size
        self.url = url
        self.updateDate = updateDate
        self.parentId = parentId
        self.key = id + " " + updateDate


db.create_all()
