from app.aws import AWSInstance
import time
import ssl
from twilio.rest import Client as TwilioClient
from pathlib import Path
import os
import requests
import datetime
import re
from app.config import Config
import logging

from PIL import Image, ImageDraw, ImageFont

ssl._create_default_https_context = ssl._create_unverified_context

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


class SendMessagesToClients():
   awsInstance = AWSInstance()

   def __init__(self):
      pass

   @classmethod
   def cleanMessage(cls,message=''):
      def regexReplaceFunction(match=''):
         return match.group(0).upper()

      cleaned_message = re.sub('[\.][\s]+[a-z]', regexReplaceFunction, message)
      cleaned_message = cleaned_message[0].upper()+cleaned_message[1:]
      return cleaned_message

   #not needed now; might be needed in future
   @classmethod
   def sendEmail(cls, to_address='mo@vensti.com', message='perfectscoremo', subject='Payment Instructions/Options', type=''):
      SendMessagesToClients.awsInstance.send_email(to_address=to_address, message=message, subject=subject, type=type)

   @classmethod
   def sendSMS(cls, message_as_text=None, message_as_image=None, to_numbers=[], type=''):
      account_sid = SendMessagesToClients.awsInstance.get_secret("twilio_cred", "TWILIO_ACCOUNT_SID") or os.environ['TWILIO_ACCOUNT_SID']
      auth_token = SendMessagesToClients.awsInstance.get_secret("twilio_cred", "TWILIO_AUTH_TOKEN") or os.environ['TWILIO_AUTH_TOKEN']
      twilioClient = TwilioClient(account_sid, auth_token)

      #twilioClient.messaging.services('MGd37b2dce09791f42239043b6e949f96b').delete()
      conversations =  twilioClient.conversations.conversations.list(limit=100)#
      for record in conversations:
          logger.debug("Deleted record is: "+str(record.sid))
          twilioClient.conversations.conversations(record.sid).delete()

      listToVerifyDeleteComplete = twilioClient.conversations.conversations.list(limit=100)
      logger.debug("listToVerifyDeleteComplete is: " + str(listToVerifyDeleteComplete))
      while listToVerifyDeleteComplete:
         logger.debug("Waiting for 2 seconds to give deletion action time to complete before proceeding.")
         time.sleep(2)
         listToVerifyDeleteComplete = twilioClient.conversations.conversations.list(limit=100)

      conversation = twilioClient.conversations.conversations.create(messaging_service_sid=Config.twilio_messaging_service_sid,friendly_name='AssociateService')
      logger.debug("conversation created: "+str(conversation.sid)+"!")

      twilioClient.conversations.conversations(conversation.sid).participants.create(messaging_binding_projected_address=Config.twilio_sms_number)
      twilioClient.conversations.conversations(conversation.sid).participants.create(messaging_binding_address='+19725847364') #add mo
      twilioClient.conversations.conversations(conversation.sid).participants.create(messaging_binding_address='+19725039573') # add assitant

      for to_number in to_numbers:
         logger.debug("to_number is "+str(to_number))
         twilioClient.conversations.conversations(conversation.sid).participants.create(messaging_binding_address='+1'+to_number)

      CreateMessageAsImage.writeTextAsImage(message_as_image)
      message_as_text_to_send = ''+message_as_text.get('title','')+"\n\n"

      for k, v in message_as_text.items():
         if k != 'title':
            message_as_text_to_send = message_as_text_to_send + "\n\n"+k+": \n\n"+v+"\n\n"

      message_as_text_to_send = message_as_text_to_send + "\n\n" + "Regards," + " \n" + "Mo" + "\n\n"

      media_sid = CreateMessageAsImage.uploadMessageImage(account_sid,auth_token,conversation.chat_service_sid)
      twilioClient.conversations.conversations(conversation.sid).messages.create(media_sid=media_sid,author=Config.twilio_sms_number)
      time.sleep(2) # wait before next send to help ensure order
      twilioClient.conversations.conversations(conversation.sid).messages.create(body=message_as_text_to_send, author=Config.twilio_sms_number)
      logger.debug("texts sent!")

class CreateMessageAsImage():
   @classmethod
   def uploadMessageImage(cls,account_sid=None,auth_token=None,chat_service_sid=None):
      api_url = "https://mcs.us1.twilio.com/v1/Services/"+chat_service_sid+"/Media"

      with open('/app/data/geeks.jpeg', 'rb') as payload:
         headers = {'Content-Type': 'image/jpeg'}
         response = requests.post(api_url, auth=(account_sid, auth_token),data=payload, verify=False, headers=headers)

      # print(response.json())
      # print(response.status_code)
      return response.json()['sid']

   @classmethod
   def writeTextAsImage(cls, textToWrite=None):
      spacing = 35
      img = Image.new('RGB', (400, 200), color='White')
      canvas = ImageDraw.Draw(img)
      font = ImageFont.truetype('/app/data/Noto_Sans/NotoSans-Bold.ttf', size=15)
      report_date = textToWrite.get('report_date','')
      report_day = datetime.datetime.strptime(report_date, "%m/%d/%Y").strftime('%A')
      canvas.text((spacing, spacing), textToWrite.get('title',''), font=font, fill='black')
      #canvas.text((spacing, spacing), "Report for {} ({})".format(report_day,report_date), font=font, fill='black')
      underline_length = len(textToWrite.get('title',''))*8
      canvas.line((spacing, spacing+20, spacing + underline_length, spacing+20),  fill='black')
      counter = 2
      for key,content in textToWrite.items():
         if key != 'report_date' and key != 'send_report' and key != 'title':
            fill = 'red' if content=='No' else 'green' if content=='Yes' else 'yellow' if content=='N/A' else 'black'
            canvas.text((spacing, spacing*counter), key+": "+content, font=font, fill=fill)
            counter+=1

      # canvas.line((spacing, (spacing * counter) + 20, spacing + 450, (spacing * counter) + 20), fill='black')
      # counter += 1
      canvas.text((spacing, (spacing * counter)+15), "Regards,", font=font, fill='black')
      counter += 1
      canvas.text((spacing, (spacing * counter) + 5), "Mo", font=font, fill='black')
      counter += 1

      Path("/app/data").mkdir(parents=True, exist_ok=True)
      img.save("/app/data/geeks.jpeg")
