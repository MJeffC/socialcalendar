from flask_app.config.mysqlconnection import connectToMySQL
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
from flask import flash
from flask_app.models import event

class User:
    db = "socialcalendar"
    def __init__(self,data):
        self.id = data['id']
        self.username = data['username']
        self.email = data['email']
        self.password = data['password']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.savedevents=[]

    @classmethod
    def save(cls,data):
        query = "INSERT INTO users (username,email,password) VALUES(%(username)s,%(email)s,%(password)s)"
        return connectToMySQL(cls.db).query_db(query,data)

    @classmethod
    def get_all(cls):
        query = "SELECT * FROM users;"
        results = connectToMySQL(cls.db).query_db(query)
        users = []
        for row in results:
            users.append( cls(row))
        return users

    @classmethod
    def get_by_email(cls,data):
        query = "SELECT * FROM users WHERE email = %(email)s;"
        results = connectToMySQL(cls.db).query_db(query,data)
        if len(results) < 1:
            return False
        return cls(results[0])


    @classmethod
    def get_by_id(cls,data):
        query = "SELECT * FROM users WHERE id = %(id)s;"
        results = connectToMySQL(cls.db).query_db(query,data)
        return cls(results[0])

    @classmethod
    def get_by_eventid(cls,data):
        query = "SELECT * FROM users LEFT JOIN events ON users.id = events.user_id LEFT JOIN events ON events.id = events.event_id WHERE users.id = %(id)s;"
        results = connectToMySQL(cls.db).query_db(query,data)

        user = cls(results[0])

        for row in results:
            if row['events.id'] == None:
                break
            data = {
                "id": row['events.id'],
                "name": row['name'],
                "location":row['location'],
                "startdate":row['startdate'],
                "category":row['category'],
                "description":row['description'],
                "created_at": row['events.created_at'],
                "updated_at": row['events.updated_at'],
                "user_id":row['events.user_id']
            }
            user.savedevents.append(event.Event(data))
        return user


    @classmethod
    def add_rsvp(cls,data):
        query="INSERT INTO rsvps (user_id,event_id) VALUES (%(user_id)s, %(event_id)s);"
        return connectToMySQL(cls.db).query_db(query,data)

    @staticmethod
    def validate_register(user):
        is_valid = True
        query = "SELECT * FROM users WHERE email = %(email)s;"
        results = connectToMySQL(User.db).query_db(query,user)
        if len(results) >= 1:
            flash("Email already taken.","register")
            is_valid=False
        if not EMAIL_REGEX.match(user['email']):
            flash("Invalid Email!!!","register")
            is_valid=False
        if len(user['username']) < 3:
            flash("Username must be at least 3 characters","register")
            is_valid= False
        if len(user['password']) < 8:
            flash("Password must be at least 8 characters","register")
            is_valid= False
        if user['password'] != user['password_confirmation']:
            flash("Passwords don't match","register")
            is_valid=False
        return is_valid