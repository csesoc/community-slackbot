"""Data models."""
from sqlalchemy import func, ForeignKey

from . import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    karma = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=func.now())

    def __repr__(self):
        return '<User {}>'.format(self.id)


class UserProfileDetail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey("users.id"))
    detail_key = db.Column(db.String(255))
    value = db.Column(db.String(255))

    def __repr__(self):
        return '<UserProfileDetail {}>'.format(self.id)


# class Courses(db.Model):
#     user_id = db.Column(db.Integer, ForeignKey("users.id"))