from app import db, login
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from flask import url_for
import base64
import os

class User(db.Model, UserMixin):
  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(64), index=True, unique=True)
  email = db.Column(db.String(120), index=True, unique=True)
  password_hash = db.Column(db.String(128))
  token = db.Column(db.String(32), index=True, unique=True)
  token_expiration = db.Column(db.DateTime, index=True)
  last_check_in = db.Column(db.DateTime, index=True)
  check_in_mode = db.Column(db.Boolean, index=True, default=False)
  check_in_period = db.Column(db.Integer, index=True, default=24)
  trips = db.relationship('Trip', backref='user', lazy='dynamic')
  contacts = db.relationship('Contact', backref='user', lazy='dynamic')
  significant_locations = db.relationship('SignificantLocation', backref='user', lazy='dynamic')

  def __repr__(self):
    return '<User {}>'.format(self.username)

  def set_password(self, password):
    self.password_hash = generate_password_hash(password)

  def check_password(self, password):
    return check_password_hash(self.password_hash, password)

  def to_dictionary(self):
    data = {
      'id': self.id,
      'username': self.username,
      'email': self.email,
      'last_check_in': self.last_check_in,
      'check_in_mode': self.check_in_mode,
      'check_in_period': self.check_in_period
    }
    return data

  def from_dictionary(self, data, new_user=False):
    # it is not possible to request a check-in period less than 24
    if 'check_in_period' in data and int(data['check_in_period']) >= 24:
      setattr(self, 'check_in_period', data['check_in_period'])
    if 'last_check_in' in data:
      # conversion from ms to s is due to difference between the
      # order of magnitude between JS and Python timedate
      converted = datetime.fromtimestamp(int(data['last_check_in']) / 1000.0)
      setattr(self, 'last_check_in', converted)
    for field in ['username', 'email']:
      if field in data:
        setattr(self, field, data[field])
    if new_user and 'password' in data:
      self.set_password(data['password'])

  def contacts_to_arr_of_hashes(self):
    contacts = self.contacts.all()
    data = []
    for contact in contacts:
      data.append(contact.to_dictionary())
    return data

  def slocations_to_arr_of_hashes(self):
    slocations = self.significant_locations.all()
    data = []
    for location in slocations:
      data.append(location.to_dictionary())
    return data

class Trip(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  destination_name = db.Column(db.String(64), index=True)
  destination_address = db.Column(db.String(128), index=True)
  destination_latitude = db.Column(db.Float(53))
  destination_longitude = db.Column(db.Float(53))
  current_latitude = db.Column(db.Float(53))
  current_longitude = db.Column(db.Float(53))
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
  is_tracking = db.Column(db.Boolean, index=True, default=True)
  last_update = db.Column(db.DateTime, index=True)
  status = db.Column(db.String(32), index=True)

  def __repr__(self):
    return '<Trip {}>'.format(self.destination_address)

  def to_dictionary(self):
    data = {
      'id': self.id,
      'destination_address': self.destination_address,
      'destination_latitude': self.destination_latitude,
      'destination_longitude': self.destination_longitude,
      'current_latitude': self.current_latitude,
      'current_longitude': self.current_longitude,
      'last_update': self.last_update,
      'status': self.status
    }
    return data

  def from_dictionary(self, data, user_id):
    for field in ['destination_address', 'destination_latitude', 'destination_longitude', 'current_latitude', 'current_longitude']:
      if field in data:
        setattr(self, field, data[field])
    self.user_id = user_id
    self.status = "ONGOING"

  def update_from_dictionary(self, data):
    for field in ['current_latitude', 'current_longitude', 'status']:
      if field in data:
        setattr(self, field, data[field])
    self.last_update = datetime.now()
    # if the status is "CANCEL" or "COMPLETE" then we're no longer tracking
    if not self.status == 'ONGOING':
      self.is_tracking = False

class Contact(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(64), index=True)
  phone_number = db.Column(db.Integer, index=True)
  phone = db.Column(db.BigInteger)
  email = db.Column(db.String(120), index=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

  def __repr__(self):
    return '<Contact {}>'.format(self.name)

  def from_dictionary(self, data, new_contact=False, user_id=None):
    for field in ['name', 'phone', 'email']:
      if field in data:
        setattr(self, field, data[field])
    if new_contact:
      self.user_id = user_id

  def to_dictionary(self):
    data = {
      'id': self.id,
      'name': self.name,
      'phone': self.phone,
      'email': self.email,
      'user_id': self.user_id,
      'associated_user': self.user.username
    }
    return data


# a model is given by its database table name, all lower case, and snake case if many letter
class SignificantLocation(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  location_name = db.Column(db.String(64), index=True)
  address = db.Column(db.String(128), index=True)
  latitude = db.Column(db.Float(53))
  longitude = db.Column(db.Float(53))
  last_check_in = db.Column(db.DateTime, index=True)
  user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

  def __repr__(self):
    return '<SignificantLocation {}>'.format(self.location_address)

  def from_dictionary(self, data, user_id):
    for field in ['address', 'latitude', 'longitude']:
      if field in data:
        setattr(self, field, data[field])
    self.user_id = user_id

  def to_dictionary(self):
    data = {
      'id': self.id,
      'address': self.address,
      'latitude': self.latitude,
      'longitude': self.longitude,
      'last_check_in': self.last_check_in,
      'user_id': self.user_id,
      'associated_user': self.user.username
    }
    return data
