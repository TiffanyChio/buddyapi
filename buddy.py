from app import app, db
from app.models import User, Trip, Contact, SignificantLocation

@app.shell_context_processor
def make_shell_context():
  return {'db': db, 'User': User, 'Trip': Trip, 'Contact': Contact, 'SignificantLocation': SignificantLocation}
