"""Data models."""
from app import db


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(16), primary_key=True)
    karma = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    def __repr__(self):
        return '<User {}>'.format(self.id)


class UserProfileDetail(db.Model):
    __tablename__ = "userprofiledetails"

    __mapper_args__ = {
        'confirm_deleted_rows': False
    }

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(16), db.ForeignKey("users.id"))
    detail_key = db.Column(db.String(32))
    value = db.Column(db.String(256))

    def __repr__(self):
        return '<UserProfileDetail {}>'.format(self.id)

class Roles(db.Model):
    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(16), db.ForeignKey("users.id"))
    title = db.Column(db.String(255))
    perm_level = db.Column(db.Integer)

    def __repr__(self):
        return '<Roles {}>'.format(self.id)



# class Courses(db.Model):
#     user_id = db.Column(db.Integer, ForeignKey("users.id"))