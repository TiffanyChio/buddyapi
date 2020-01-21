from app import app, db
from flask import jsonify, request
from werkzeug.http import HTTP_STATUS_CODES

def error_response(status_code, message=None):
  payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
  if message:
    payload['message'] = message
  response = jsonify(payload)
  response.status_code = status_code
  return response

def bad_request(message):
  return error_response(400, message)

@app.errorhandler(404)
def not_found_error(error):
  return error_response(404)

@app.errorhandler(500)
def internal_error(error):
  return error_response(500)

@app.errorhandler(403)
def forbidden_error(error):
  return error_response(403)
