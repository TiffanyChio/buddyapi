from app import app, db, sched
from datetime import datetime, timedelta

def check_in_exp():
  check_in_users = User.query.filter_by(check_in_mode=True)
  if len(check_in_users.all()) == 0:
    return

  now = datetime.now()
  exp_users = check_in_users.filter(User.last_check_in < now - timedelta(hours=24)).all()

  account_sid = os.environ.get('TWILIOSID')
  auth_token = os.environ.get('TWILIOTOKEN')
  tw_num = os.environ.get('TWILIONUM')
  client = Client(account_sid, auth_token)

  for user in exp_users:
    all_contacts = user.contacts.all()

    if len(all_contacts) > 0:
      body_text = user.username + "  has not check into a saved location within the past " + user.check_in_period + " hours. Consider checking in on them?"

      for contact in all_contacts:
        num_to = "+1" + str(contact.phone)
        message = client.messages.create(
          to=num_to,
          from_=tw_num,
          body=body_text)


sched.add_job(check_in_exp,'interval',days=1)
sched.start()
