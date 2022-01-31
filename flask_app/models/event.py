from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from datetime import datetime
from time import time
from flask_app.models import user
import math


class Event:
    db = "socialcalendar"
    def __init__(self,data):
        self.id = data['id']
        self.name=data['name']
        self.location = data['location']
        self.description = data['description']
        self.startdate = data['startdate']
        self.category = data['category']
        self.user_id=data['user_id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.users_who_rsvpd=[]
        self.creator= None

    def time_span(self):
        now = datetime.now()
        delta = now - self.created_at
        print(delta.days)
        print(delta.total_seconds())
        if delta.days > 0:
            return f"{delta.days} days ago"
        elif (math.floor(delta.total_seconds() / 60)) >= 60:
            return f"{math.floor(math.floor(delta.total_seconds() / 60)/60)} hours ago"
        elif delta.total_seconds() >= 60:
            return f"{math.floor(delta.total_seconds() / 60)} minutes ago"
        else:
            return f"{math.floor(delta.total_seconds())} seconds ago"
            
    @classmethod
    def save(cls,data):
        query = "INSERT INTO events (name,location,description,category,startdate,user_id) VALUES (%(name)s,%(location)s,%(description)s,%(category)s,%(startdate)s,%(user_id)s)"
        return connectToMySQL(cls.db).query_db(query, data)


    @classmethod
    def update(cls, data):
        query = "UPDATE events SET name=%(name)s,location=%(location)s, description=%(description)s, startdate=%(startdate)s, category=%(category)s,updated_at=NOW() WHERE id = %(id)s;"
        return connectToMySQL(cls.db).query_db(query,data)


    @classmethod
    def get_one(cls,data):
        query = "SELECT * FROM events WHERE id = %(id)s;"
        results = connectToMySQL(cls.db).query_db(query,data)
        return cls(results[0])

    @classmethod
    def destroy(cls,data):
        query = "DELETE FROM events WHERE id = %(id)s;"
        return connectToMySQL(cls.db).query_db(query,data)

    @classmethod
    def deletersvp(cls,data):
        query= "DELETE FROM rsvps WHERE event_id=%(id)s AND user_id=%(user_id)s;"
        return connectToMySQL(cls.db).query_db(query,data)


    @classmethod
    def get_events_with_user(cls):
        query="SELECT * FROM events LEFT JOIN users ON events.user_id=users.id;"
        results=connectToMySQL(cls.db).query_db(query)
        all_events=[]
        for one_event in results:
            event_data={
                "id":one_event['id'],
                "location":one_event['location'],
                "description":one_event['description'],
                "name":one_event['name'],
                "startdate":one_event['startdate'],
                "category": one_event['category'],
                "user_id":one_event['user_id'],
                "created_at":one_event['created_at'],
                "updated_at":one_event['updated_at']
            }
            single_event=cls(event_data)
            user_data={
                "id":one_event['users.id'],
                "username":one_event['username'],
                "email":one_event['email'],
                "password":one_event['password'],
                "created_at":one_event['users.created_at'],
                "updated_at":one_event['users.updated_at']
            }

            single_user=user.User(user_data)
            single_event.creator=single_user
            all_events.append(single_event)
        return all_events


    @classmethod
    def get_one_with_user(cls,data):
        query="SELECT * FROM events LEFT JOIN users ON events.user_id=users.id WHERE events.id=%(id)s"
        results = connectToMySQL(cls.db).query_db(query,data)
        all_events=[]
        for one_user in results:
            eventdata={
                "id":one_user['id'],
                "name":one_user['name'],
                "location":one_user['location'],
                "description":one_user['description'],
                "startdate":one_user['startdate'],
                "category": one_user['category'],
                "user_id":one_user['user_id'],
                "created_at":one_user['created_at'],
                "updated_at":one_user['updated_at']
            }
            events=cls(eventdata)
            
            userdata={
                "id":one_user['users.id'],
                "username":one_user['username'],
                "email":one_user['email'],
                "password":one_user['password'],
                "created_at":one_user['users.created_at'],
                "updated_at":one_user['users.updated_at']
            }
            user_obj=user.User(userdata)
            rsvp_obj=user.User(userdata)
            events.creator=user_obj
            events.users_who_rsvpd=rsvp_obj
            all_events.append(events)
        return all_events

    @classmethod
    def get_by_id(cls,data):
        query = "SELECT * FROM events LEFT JOIN rsvps ON events.id = rsvps.event_id LEFT JOIN users ON users.id = rsvps.user_id WHERE events.id = %(id)s;"
        results = connectToMySQL(cls.db).query_db(query,data)

        event = cls(results[0])

        for row in results:
            if row['users.id'] == None:
                break
            data = {
                "id": row['users.id'],
                "username": row['username'],
                "email":row['email'],
                "password":row['password'],
                "created_at": row['users.created_at'],
                "updated_at": row['users.updated_at']
            }
            event.users_who_rsvpd.append(user.User(data))
        return event

    @classmethod
    def add_rsvp(cls,data):
        query="INSERT INTO rsvps (user_id,event_id) VALUES (%(user_id)s, %(event_id)s);"
        return connectToMySQL(cls.db).query_db(query,data)
    
    @classmethod
    def grab_rsvp(cls, data):
        query = "SELECT COUNT(*) COUNT FROM rsvps WHERE event_id = %(id)s;"
        return connectToMySQL(cls.db).query_db(query, data)

    @classmethod
    def get_one_with_creator(cls,data):
        query = "SELECT * FROM events JOIN users ON events.user_id = users.id WHERE events.id = %(id)s;"
        results = connectToMySQL(cls.db).query_db(query,data)
        event =  cls(results[0])
        user_data = {
                'id': results[0]['users.id'],
                'username': results[0]['username'],
                'email': results[0]['email'],
                'password': results[0]['password'],
                'created_at': results[0]['created_at'],
                'updated_at': results[0]['updated_at']                 
        }
        creator = user.User(user_data)
        event.creator = creator
        return event


    @staticmethod
    def validate_event(event):
        is_valid = True
        if len(event['name']) < 2:
            is_valid = False
            flash('Event name must be entered!', "event")
        if len(event['location']) < 5:
            is_valid = False
            flash('location must be entered!', "event")
        if len(event['description']) < 10:
            is_valid = False
            flash('description must be entered!', "painting")
        return is_valid
