from . import db # our SQLAlchemy db object

from flask_login import UserMixin
from sqlalchemy.sql import func

"""
User model for storing user information
"""
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)

    # given by user during sign-up
    email = db.Column(db.String(150), unique = True)
    password = db.Column(db.String(150)) 
    first_name = db.Column(db.String(150))   
    sex = db.Column(db.String(10))
    weight = db.Column(db.Integer)
    height = db.Column(db.Integer) 
    age = db.Column(db.Integer)
    goal = db.Column(db.String(10))
    activity_factor = db.Column(db.Float)
    allergies = db.Column(db.String(200))
    dietary_preferences = db.Column(db.String(200))

    # calculate during sign-up, 
    recommended_intake = db.Column(db.Integer)
    recommended_protein = db.Column(db.Integer)
    recommended_fats = db.Column(db.Integer)
    recommended_carbs = db.Column(db.Integer)

    items = db.relationship("Item", backref = "user")
    profile_image = db.Column(db.String(150), nullable=True)
    
"""
Items that users can add to their day of eating. reset items at midnight
"""
class Item(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))
    cals = db.Column(db.Integer)
    fats = db.Column(db.Integer)
    protein = db.Column(db.Integer)
    carbs = db.Column(db.Integer)

    date = db.Column(db.DateTime(timezone=True), default = func.now())

    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))

"""
Recipes model for storing recipes information
"""

class Recipes(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(50))
    cooktime = db.Column(db.String(50))
    calories = db.Column(db.String(50))
    description = db.Column(db.String(250))
