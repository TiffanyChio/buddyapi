from flask import g
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app.models import User
from app.errors import error_response

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

@basic_auth.verify_password
def verify_password(email, password):
  user = User.query.filter_by(email=email).first()
  if user is None:
    return False
  # save the authenticated user in g.current_user so that it can be from the API view functions
  # g is a global variable in flask that is valid till we finished processing a request
  g.current_user = user
  if user.check_password(password):
    return user.id
  else:
    return error_response(401)

@basic_auth.error_handler
def basic_auth_error():
  return error_response(401)
