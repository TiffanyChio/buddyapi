# Buddy - Back-End API

Buddy is a personal safety iOS app with three main features:
1. Users can invite friends to follow along on their trips using a web browser. Friends do not need to download the app! A URL link is sent out via a text message.
2. At the press of a button, the trip webpage will be updated with a danger status. Additionally emergency contacts saved to the app will get a text alert, notifying them that the user does not feel safe. 
3. The Check-In feature sends a text alert to emergency contacts if the user has not returned to a saved location (home, work, or school) within a designated time period. 

This repository contains the code for the back-end API built in Flask.

## Prerequisites
You will need access to the Twilio API. Sign up [here](https://www.twilio.com/sms). 

## Installation
Clone this repository and cd into the repository. Create a virtual environment and install all project dependencies with:

```sh
pip install -r requirements.txt
```

Deploy this project to the platform of your choice. Be sure to set up the deployment's environment variables to include:
1. your Twilio SID saved as ```TWILIOSID```
2. your Twilio Auth Token saved as ```TWILIOTOKEN```
3. your Twilio account's SMS number saved as ```TWILIONUM```
4. a key to encrypt user passwords stored in the database saved under ```LOGINKEY```

