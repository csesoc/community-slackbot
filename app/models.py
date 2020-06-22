"""Data models."""
from sqlalchemy import func, ForeignKey

from . import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(16), primary_key=True)
    karma = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=func.now())

    def __repr__(self):
        return '<User {}>'.format(self.id)


class UserProfileDetail(db.Model):
    __tablename__ = "userprofiledetails"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(16), ForeignKey("users.id"))
    detail_key = db.Column(db.String(32))
    value = db.Column(db.String(256))

    def __repr__(self):
        return '<UserProfileDetail {}>'.format(self.id)


