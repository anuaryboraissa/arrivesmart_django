import firebase_admin
import os
from rest_framework.response import Response
from firebase_admin import credentials, messaging
from .models import SentNotification

SETTINGS_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the JSON file
JSON_FILE_PATH = os.path.join(SETTINGS_DIR, 'python.json')
cred = credentials.Certificate(f"{JSON_FILE_PATH}")
firebase_admin.initialize_app(cred)

def sendPush(title, msg, registration_token, dataObject=None,image=None,post=None,user_ticket=None):
    # See documentation on defining a message payload.
    try:
        message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=msg,
            image=image
        ),
        data=dataObject,
        tokens=registration_token,
        )

    # Send a message to the device corresponding to the provided
    # registration token.
        response = messaging.send_multicast(message)
        map={"sent_status":True,"message":"success"}
        SentNotification.objects.create(post=post,user_ticket=user_ticket,**map)
    except Exception as e:
        map={"sent_status":False,"message":f"{e}"}
        SentNotification.objects.create(post=post,user_ticket=user_ticket,**map)