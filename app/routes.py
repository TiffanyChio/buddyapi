from app import app, db
from app.models import User, Contact, Trip, SignificantLocation
from app.errors import bad_request
from app.auth import token_auth
from flask import redirect, url_for, jsonify, request, url_for, g, abort
import os
from twilio.rest import Client

@app.route('/users/<int:id>', methods=['GET'])
def view_user(id):
  # instead of returning None when the id does not exist, it aborts the request and returns a 404 error to the client
  return jsonify(User.query.get_or_404(id).to_dictionary())

@app.route('/users', methods=['POST'])
def create_user():
  # JSON provided in request body
  # request.get_json() will return none if no JSON data found
  # {} ensures a consistent format for input
  data = request.get_json(silent=True) or {}
  if 'username' not in data or 'email' not in data or 'password' not in data:
    return bad_request('Please fill out the username, email and password fields.')
  if User.query.filter_by(username=data['username']).first():
    return bad_request('please use a different username')
  if User.query.filter_by(email=data['email']).first():
    return bad_request('please use a different email address')
  user = User()
  user.from_dictionary(data, new_user=True)
  db.session.add(user)
  db.session.commit()
  response = jsonify(user.to_dictionary())
  response.status_code = 201
  return response

@app.route('/users/<int:id>', methods=['PATCH'])
def update_user(id):
  user = User.query.get_or_404(id)
  # body must be {} cannot be blank
  data = request.get_json(silent=True) or {}
  # you can change to your own username again
  # but otherwise if it's in the system, you can't have the same username as another user
  if 'username' in data and data['username'] != user.username and \
      User.query.filter_by(username=data['username']).first():
    return bad_request('Username already in use. Please select a different username.')
  if 'email' in data and data['email'] != user.email and \
      User.query.filter_by(email=data['email']).first():
    return bad_request('Email address already in use. Please use a different email address.')
  user.from_dictionary(data, new_user=False)
  # apparently you can change data wherever else as long as you commit
  db.session.commit()
  return jsonify(user.to_dictionary())

@app.route('/users/<int:id>/togglecheckin', methods=['PATCH'])
def toggle_check_in(id):
  user = User.query.get_or_404(id)
  num_sig_locations = user.significant_locations.count()
  num_contacts = user.contacts.count()
  # cannot turn on check-in mode with no significant locations or emergency contacts
  if (num_sig_locations == 0 or num_contacts == 0) and user.check_in_mode == False:
    return bad_request('Cannot turn on Check In Mode without saved check-in locations.')
  user.check_in_mode = not user.check_in_mode
  db.session.commit()
  return jsonify(user.to_dictionary())

@app.route('/users/<int:id>', methods=['DELETE'])
def delete_user(id):
  user = User.query.get_or_404(id)
  db.session.delete(user)
  db.session.commit()
  response = jsonify({'message': 'Successfully deleted ' + user.username + '\'s account.'})
  return response

@app.route('/users/<int:user_id>/contacts', methods=['GET'])
def index_contacts(user_id):
  user = User.query.get_or_404(user_id)
  # returns [] if there are no records
  return jsonify(user.contacts_to_arr_of_hashes())

@app.route('/contacts/<int:contact_id>', methods=['GET'])
def view_contact(contact_id):
  contact = Contact.query.get_or_404(contact_id)
  return jsonify(contact.to_dictionary())

@app.route('/users/<int:user_id>/contacts', methods=['POST'])
def create_contact(user_id):
  user = User.query.get_or_404(user_id)
  data = request.get_json(silent=True) or {}
  if 'name' not in data or 'phone' not in data or 'email' not in data:
    return bad_request('Please fill out the name, phone number, and email fields.')
  contact = Contact()
  contact.from_dictionary(data, new_contact=True, user_id=user_id)
  db.session.add(contact)
  db.session.commit()
  response = jsonify(contact.to_dictionary())
  response.status_code = 201
  return response

@app.route('/contacts/<int:contact_id>', methods=['PATCH'])
def update_contact(contact_id):
  contact = Contact.query.get_or_404(contact_id)
  data = request.get_json(silent=True) or {}
  contact.from_dictionary(data)
  db.session.commit()
  return jsonify(contact.to_dictionary())

@app.route('/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
  contact = Contact.query.get_or_404(contact_id)
  db.session.delete(contact)
  db.session.commit()
  response = jsonify({'message': 'Successfully deleted ' + contact.name + '\'s information.'})
  return response

@app.route('/users/<int:user_id>/slocations', methods=['GET'])
def index_slocations(user_id):
  user = User.query.get_or_404(user_id)
  # returns [] if there are no records
  return jsonify(user.slocations_to_arr_of_hashes())

@app.route('/users/<int:user_id>/slocations', methods=['POST'])
def create_slocation(user_id):
  user = User.query.get_or_404(user_id)
  data = request.get_json(silent=True) or {}
  if 'address' not in data or 'latitude' not in data or 'longitude' not in data:
    return bad_request('Valid address needed to save as a check-in location.')
  existing_locations = user.significant_locations.all()
  # Cannot save a significant location if it's already part of the user account
  # Other users can save the exact same information still
  for element in existing_locations:
    # if element.location_name == data['location_name']:
    #   return bad_request('Location name already in use. Please select a different location name.')
    if element.address == data['address'] or (str(element.latitude) == data['latitude'] and str(element.longitude) == data['longitude']):
      return bad_request('Check-in location has already been saved to this account.')
  slocation = SignificantLocation()
  slocation.from_dictionary(data, user_id)
  db.session.add(slocation)
  db.session.commit()
  response = jsonify(slocation.to_dictionary())
  response.status_code = 201
  return response

@app.route('/slocations/<int:location_id>', methods=['DELETE'])
def delete_slocation(location_id):
  slocation = SignificantLocation.query.get_or_404(location_id)
  db.session.delete(slocation)
  db.session.commit()
  response = jsonify({'message': 'Successfully deleted ' + slocation.address +'.'})
  return response

# do not include user id to the URL for privacy
@app.route('/trips/<int:trip_id>', methods=['GET'])
def view_trip(trip_id):
  trip = Trip.query.get_or_404(trip_id)
  return jsonify(trip.to_dictionary())

@app.route('/users/<int:user_id>/trips', methods=['POST'])
def create_trip(user_id):
  user = User.query.get_or_404(user_id)
  data = request.get_json(silent=True) or {}
  if 'destination_address' not in data or 'destination_latitude' not in data or 'destination_longitude' not in data:
    return bad_request('Error. Trip was not created. Please try again.')
  existing_trips = user.trips.all()
  # Cannot create more than one trip at a time.
  for element in existing_trips:
    if element.is_tracking:
      return bad_request('A Trip is already underway. Cannot create another Trip.')
  trip = Trip()
  trip.from_dictionary(data, user_id)
  db.session.add(trip)
  db.session.commit()
  response = jsonify(trip.to_dictionary())
  response.status_code = 201
  return response

# updates current location and status
@app.route('/trips/<int:trip_id>', methods=['PATCH'])
def update_trip(trip_id):
  trip = Trip.query.get_or_404(trip_id)
  if (not trip.status == "ONGOING") and (not trip.status == "PANIC"):
    return bad_request('Cannot update ' + trip.status + ' trips.')
  data = request.get_json(silent=True) or {}
  trip.update_from_dictionary(data)
  db.session.commit()
  return jsonify(trip.to_dictionary())

@app.route('/trips/<int:trip_id>', methods=['DELETE'])
def delete_trip(trip_id):
  trip = Trip.query.get_or_404(trip_id)
  db.session.delete(trip)
  db.session.commit()
  response = jsonify({'message': 'Successfully deleted ' + trip.destination_address +'.'})
  return response

@app.route('/users/<int:user_id>/trips/<int:trip_id>/panic', methods=['POST'])
def send_panic_notif(user_id, trip_id):
  user = User.query.get_or_404(user_id)
  trip = Trip.query.get_or_404(trip_id)
  all_contacts = user.contacts.all()
  # if there are no contacts, send an error message and return
  # else iterate through contacts and send out SMS notification
  if len(all_contacts) == 0:
    return bad_request('There are no contacts set up for this user.')
  else:
    account_sid = os.environ.get('TWILIO SID')
    auth_token = os.environ.get('TWILIO TOKEN')
    client = Client(account_sid, auth_token)
    body_text = user.username + " has pressed the Panic Button on their Buddy App. For current location information, please visit https://buddy-web-ada.herokuapp.com/" + str(trip_id)

    for contact in all_contacts:
      num_to = "+1" + str(contact.phone)
      message = client.messages.create(
        to=num_to,
        from_="+15592574390",
        body=body_text)

  response = jsonify({'message': 'Successfully sent notification to contacts.'})
  return response
