from app import app, db
from flask import jsonify, g
from app.auth import basic_auth

# The login_required decorator will force verification function to run first
@app.route('/signin', methods=['POST'])
@basic_auth.login_required
def signin():
  return jsonify({'BUDDY_ID': g.current_user.id})

