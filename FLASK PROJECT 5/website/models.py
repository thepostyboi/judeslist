from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    username = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    admin = db.Column(db.Boolean(),default=False)
    banned = db.Column(db.Boolean(),default=False)
    ProfilePicture = db.relationship("ProfilePicture")
    Listing = db.relationship("Listing")
    Comments = db.relationship("Comments")
    Likes = db.relationship("Likes")

class Ratings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rater_user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    rated_user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    rater_user = relationship("User", foreign_keys=[rater_user_id])
    rated_user = relationship("User", foreign_keys=[rated_user_id])
    rating = db.Column(db.Integer)


class Reports(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id = db.Column(db.Integer, primary_key=True)
    reporter_user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    reported_user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    reporter_user = relationship("User", foreign_keys=[reporter_user_id])
    reported = relationship("User", foreign_keys=[reported_user_id])
    report = db.Column(db.String(300))


class ProfilePicture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    postcode = db.Column(db.String(10))
    description = db.Column(db.String(300))
    region = db.Column(db.String(50))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    file = db.Column(db.Text, nullable=False)
    minetype = db.Column(db.Text, nullable=False)
    removed = db.Column(db.Boolean(),default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    Comments = db.relationship("Comments")
    Likes = db.relationship("Likes")

class Likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    Listing_id = db.Column(db.Integer, db.ForeignKey("listing.id"))

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(100))
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    Listing_id = db.Column(db.Integer, db.ForeignKey("listing.id"))
