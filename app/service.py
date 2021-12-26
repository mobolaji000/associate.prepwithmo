from app.aws import AWSInstance
from app.google import GoogleInstance
import ssl
from twilio.rest import Client as TwilioClient
from pathlib import Path
import os
import requests

from PIL import Image, ImageDraw, ImageFont

ssl._create_default_https_context = ssl._create_unverified_context


class SendMessagesToClients():
   awsInstance = AWSInstance()

   def __init__(self):
      pass

   @classmethod
   def sendEmail(cls, to_address='mo@vensti.com', message='perfectscoremo', subject='Payment Instructions/Options', type=''):
      SendMessagesToClients.awsInstance.send_email(to_address=to_address, message=message, subject=subject, type=type)

   @classmethod
   def sendSMS(cls, message_as_text=None, message_as_image=None, to_numbers=[], type=''):
      account_sid = SendMessagesToClients.awsInstance.get_secret("twilio_cred", "TWILIO_ACCOUNT_SID") or os.environ['TWILIO_ACCOUNT_SID']
      auth_token = SendMessagesToClients.awsInstance.get_secret("twilio_cred", "TWILIO_AUTH_TOKEN") or os.environ['TWILIO_AUTH_TOKEN']
      twilioClient = TwilioClient(account_sid, auth_token)

      #twilioClient.messaging.services('MGd37b2dce09791f42239043b6e949f96b').delete()
      conversations =  twilioClient.conversations.conversations.list(limit=50)
      for record in conversations:
          print(record.sid)
          twilioClient.conversations.conversations(record.sid).delete()

      conversation = twilioClient.conversations.conversations.create(messaging_service_sid='MG0faa1995ce52477a642163564295650c',friendly_name='DailyReport')
      print("conversation created!")
      print(conversation.sid)


      twilioClient.conversations.conversations(conversation.sid).participants.create(messaging_binding_projected_address='+19564771274')
      twilioClient.conversations.conversations(conversation.sid).participants.create(messaging_binding_address='+19725847364')

      for to_number in to_numbers:
        twilioClient.conversations.conversations(conversation.sid).participants.create(messaging_binding_address='+1'+to_number)

      CreateMessageAsImage.writeTextAsImage(message_as_image)
      for k, v in message_as_text.items():
         message_as_text_to_send = "\n"+k+": \n"+v

      media_sid = CreateMessageAsImage.uploadMessageImage(account_sid,auth_token,conversation.chat_service_sid)
      twilioClient.conversations.conversations(conversation.sid).messages.create(body=message_as_text_to_send,media_sid=media_sid,author='+19564771274')
      print("text sent!")

class CreateMessageAsImage():
   @classmethod
   def uploadMessageImage(cls,account_sid=None,auth_token=None,chat_service_sid=None):
      api_url = "https://mcs.us1.twilio.com/v1/Services/"+chat_service_sid+"/Media"

      with open('/app/data/geeks.jpeg', 'rb') as payload:
         headers = {'Content-Type': 'image/jpeg'}
         response = requests.post(api_url, auth=(account_sid, auth_token),data=payload, verify=False, headers=headers)

      print(response.json())
      print(response.status_code)
      return response.json()['sid']

   @classmethod
   def writeTextAsImage(cls, textToWrite=None):
      spacing = 25
      img = Image.new('RGB', (200, 100), color='White')
      canvas = ImageDraw.Draw(img)
      font = ImageFont.truetype('/app/data/Noto_Sans/NotoSans-Bold.ttf', size=15)
      canvas.text((spacing, spacing), "Report for today ({})".format(textToWrite.get('report_date','')), font=font, fill='black')
      canvas.line((spacing, spacing+2, spacing + 50, spacing+2),  fill='black')
      counter = 2
      for key,content in textToWrite.items():
         if key != 'report_date':
            fill = 'red' if content=='No' else 'green' if content=='Yes' else 'yellow' if content=='N/A' else 'black'
            canvas.text((spacing, spacing*counter), key+": "+content, font=font, fill=fill)
            counter+=1
      Path("/app/data").mkdir(parents=True, exist_ok=True)
      img.save("/app/data/geeks.jpeg")
