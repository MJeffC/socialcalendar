from flask import render_template, request, redirect, session, flash
from flask_app import app
from flask_app.models.event import Event
from flask_app.models.user import User
from datetime import datetime

@app.route('/create')
def new_event():
    if 'user_id' not in session:
        return redirect('/logout')
    data = {
        "id": session['user_id']
    }
    return render_template('newevent.html', user= User.get_by_id(data))

@app.route('/myevents')
def view_events():
    if 'user_id' not in session:
        return redirect('/logout')
    user_data = {
        "id": session['user_id']
    }
    data = {
        "id": id
    }
    return render_template('myevents.html', user= User.get_by_id(user_data), events= Event.get_events_with_user(), now=datetime.now())


@app.route('/event/create', methods=['POST'])
def create_event():
    if 'user_id' not in session:
        return redirect('/logout')
    if not Event.validate_event(request.form):
        return redirect('/create')
    data = {
        "name": request.form["name"],
        "location": request.form['location'],
        "description": request.form["description"],
        "startdate": request.form["startdate"],
        "category": request.form["category"],
        "user_id": session["user_id"]
    }
    Event.save(data)
    return redirect('/dashboard')

@app.route('/edit/<int:id>')
def edit_event(id):
    if 'user_id' not in session:
        return redirect('/logout')
    data = {
        "id": id
    }
    user_data = {
        'id':session['user_id']
    }
    return render_template('edit.html', event=Event.get_one(data), user=User.get_by_id(user_data))

@app.route('/destroy/event/<int:id>')
def destroy_event(id):
    if 'user_id' not in session:
        return redirect('/logout')
    data = {
        "id": id
    }
    Event.destroy(data)
    return redirect('/dashboard')

@app.route('/view/<int:id>')
def show_event(id):
    if 'user_id' not in session:
        return redirect('/logout')
    data = {
        "id": id
    }
    user = User.get_by_id(data)
    event = Event.get_one_with_creator(data)
    rsvp = Event.grab_rsvp(data)
    # print(rsvp)
    return render_template('showevent.html',event = event, user=user, rsvp=rsvp)

@app.route('/event/update/<int:id>', methods=['POST'])
def update_event(id):
    if 'user_id' not in session:
        return redirect('/logout')
    if not Event.validate_event(request.form):
        return redirect(f'/event/edit/{id}') #cannot pass in int:id outside of app.route links
    data = {
        "name": request.form["name"],
        "startdate": request.form['startdate'],
        "location": request.form['location'],
        "description": request.form["description"],
        "id": request.form["id"]
        }

    Event.update(data)
    return redirect ('/dashboard')

@app.route('/join/rsvp', methods=['POST'])
def join_rsvp():
    data = {
        'user_id':session['user_id'],
        'event_id': request.form['event_id']
    }
    User.add_rsvp(data)
    return redirect(f"/view/{request.form['event_id']}")

@app.route('/remove/rsvp', methods=['POST'])
def remove_rsvp():
    data = {
        'user_id':session['user_id'],
        'event_id': request.form['event_id']
    }
    User.deletersvp(data)
    return redirect(f"/view/{request.form['event_id']}")
