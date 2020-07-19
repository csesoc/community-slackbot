"""Data models."""
import enum

from sqlalchemy import func, ForeignKey
from app import db

MAX_STRING_LENGTH = 65535


class UserRoles:
    NORMAL = 0
    MOD = 1
    ADMIN = 2
    ROLES = [NORMAL, MOD, ADMIN]
    TITLES = [
        "Normal",
        "Moderator",
        "Admin"
    ]


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(16), primary_key=True)
    karma = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=func.now())

    def __repr__(self):
        return '<User {}>'.format(self.id)


class UserRole(db.Model):
    __tablename__ = "user_role"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(16), ForeignKey("users.id"))
    role_id = db.Column(db.Integer(), ForeignKey("roles.id"))

    def __repr__(self):
        return '<UserRole {}>'.format(self.id)


class Roles(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255))
    perm_level = db.Column(db.Integer)

    def __repr__(self):
        return '<Role {}>'.format(self.id)


class Courses(db.Model):
    __tablename__ = "courses"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course = db.Column(db.String(255))
    msg = db.Column(db.Text())

    def __repr__(self):
        return '<Courses {}>'.format(self.id)


class AnonMsgs(db.Model):
    __tablename__ = "anon_msgs"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    msg = db.Column(db.Text())
    # user_id = db.Column(db.String(16), ForeignKey("users.id"))
    user_id = db.Column(db.String(16))
    target_id = db.Column(db.String(16))

    def __repr__(self):
        return '<AnonMsgs {}>'.format(self.id)


class UserProfileDetail(db.Model):
    __tablename__ = "user_profile_details"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(16), ForeignKey("users.id"))
    detail_key = db.Column(db.String(32))
    value = db.Column(db.String(256))

    def __repr__(self):
        return '<UserProfileDetail {}>'.format(self.id)


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    review = db.Column(db.Text())
    user_id = db.Column(db.String(16), ForeignKey("users.id"))
    lecturer = db.Column(db.String(255))
    term = db.Column(db.String(255))
    is_approved = db.Column(db.Boolean())

    def __repr__(self):
        return '<Review {}>'.format(self.id)


class Report(db.Model):
    __tablename__ = "reports"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    msg_id = db.Column(db.Integer, ForeignKey("anon_msgs.id"))
    report = db.Column(db.Text())

    def __repr__(self):
        return '<AnonMsgs {}>'.format(self.id)