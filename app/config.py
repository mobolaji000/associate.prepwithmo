import os
from app.aws import AWSInstance
import traceback

basedir = os.path.abspath(os.path.dirname(__file__))
awsInstance = AWSInstance()
class Config(object):
    try:
        if os.environ['DEPLOY_REGION'] == 'local':

            os.environ["url_to_start_reminder"] = "http://127.0.0.1:5001/"
            os.environ["transaction_setup_url"] = "http://127.0.0.1:5002/lead_info"
            os.environ["lead_info_url"] = "http://127.0.0.1:5002/transaction_setup"
            flask_secret_key = os.environ.get('flask_secret_key')
            SECRET_KEY = os.environ.get('flask_secret_key')
            dbUserName = os.environ.get('dbUserNameLocal')
            dbPassword = os.environ.get('dbPasswordLocal')
            SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://'+str(dbUserName)+':'+str(dbPassword)+'@host/mobolajioo'
            SQLALCHEMY_TRACK_MODIFICATIONS = False

            USER_APP_NAME = "PrepWithMo Associates"  # Shown in and email templates and page footers
            USER_ENABLE_EMAIL = True  # Enable email authentication
            USER_ENABLE_USERNAME = False  # Disable username authentication
            USER_EMAIL_SENDER_NAME = USER_APP_NAME
            USER_EMAIL_SENDER_EMAIL = "mo@info.perfectscoremo.com"
            USER_REQUIRE_RETYPE_PASSWORD = True

            # Flask-Mail SMTP server settings
            MAIL_SERVER = 'email-smtp.us-east-2.amazonaws.com'
            MAIL_PORT = 465
            MAIL_USE_SSL = True
            MAIL_USE_TLS = False
            MAIL_USERNAME = os.environ.get('SMTP_Username')
            MAIL_PASSWORD = os.environ.get('SMTP_Password')
            MAIL_DEFAULT_SENDER = '"PrepWithMo Associates" <mo@info.perfectscoremo.com>'

            USER_CORPORATION_NAME = 'PrepWithMo'
            USER_COPYRIGHT_YEAR = 2022

        elif os.environ['DEPLOY_REGION'] == 'dev':

            os.environ["url_to_start_reminder"] = "https://associate-prepwithmo-7kkr5.ondigitalocean.app/health"
            os.environ["transaction_setup_url"] = "https://dev-pay-perfectscoremo-7stpz.ondigitalocean.app/lead_info"
            os.environ["lead_info_url"] = "https://dev-pay-perfectscoremo-7stpz.ondigitalocean.app/transaction_setup"
            flask_secret_key = awsInstance.get_secret("vensti_admin", "flask_secret_key")
            SECRET_KEY = awsInstance.get_secret("vensti_admin", "flask_secret_key")
            dbUserName = awsInstance.get_secret("do_db_cred", "dev_username")
            dbPassword = awsInstance.get_secret("do_db_cred", "dev_password")
            SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://'+str(dbUserName)+':'+str(dbPassword)+'@app-27fee962-3fa3-41cb-aecc-35d29dbd568e-do-user-9096158-0.b.db.ondigitalocean.com:25060/db'
            SQLALCHEMY_TRACK_MODIFICATIONS = False

            USER_APP_NAME = "PrepWithMo Associates"  # Shown in and email templates and page footers
            USER_ENABLE_EMAIL = True  # Enable email authentication
            USER_ENABLE_USERNAME = False  # Disable username authentication
            USER_EMAIL_SENDER_NAME = USER_APP_NAME
            USER_EMAIL_SENDER_EMAIL = "mo@info.perfectscoremo.com"
            USER_REQUIRE_RETYPE_PASSWORD = True

            # Flask-Mail SMTP server settings
            MAIL_SERVER = 'email-smtp.us-east-2.amazonaws.com'
            MAIL_PORT = 465
            MAIL_USE_SSL = True
            MAIL_USE_TLS = False
            MAIL_USERNAME = os.environ.get('SMTP_Username')
            MAIL_PASSWORD = os.environ.get('SMTP_Password')
            MAIL_DEFAULT_SENDER = '"PrepWithMo Associates" <mo@info.perfectscoremo.com>'

            USER_CORPORATION_NAME = 'PrepWithMo'
            USER_COPYRIGHT_YEAR = 2022

        elif os.environ['DEPLOY_REGION'] == 'prod':

            os.environ["url_to_start_reminder"] = "https://associate.prepwithmo.com/health"
            os.environ["transaction_setup_url"] = "https://pay.perfectscoremo.com/lead_info"
            os.environ["lead_info_url"] = "https://pay.perfectscoremo.com/transaction_setup"
            flask_secret_key = awsInstance.get_secret("vensti_admin", "flask_secret_key")
            SECRET_KEY = awsInstance.get_secret("vensti_admin", "flask_secret_key")
            dbUserName = awsInstance.get_secret("do_db_cred", "username")
            dbPassword = awsInstance.get_secret("do_db_cred", "password")
            SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://' + str(dbUserName) + ':' + str(dbPassword) + '@app-36443af6-ab5a-4b47-a64e-564101e951d6-do-user-9096158-0.b.db.ondigitalocean.com:25060/db'
            SQLALCHEMY_TRACK_MODIFICATIONS = False

            USER_APP_NAME = "PrepWithMo Associates"  # Shown in and email templates and page footers
            USER_ENABLE_EMAIL = True  # Enable email authentication
            USER_ENABLE_USERNAME = False  # Disable username authentication
            USER_EMAIL_SENDER_NAME = USER_APP_NAME
            USER_EMAIL_SENDER_EMAIL = "mo@info.perfectscoremo.com"
            USER_REQUIRE_RETYPE_PASSWORD = True

            # Flask-Mail SMTP server settings
            MAIL_SERVER = 'email-smtp.us-east-2.amazonaws.com'
            MAIL_PORT = 465
            MAIL_USE_SSL = True
            MAIL_USE_TLS = False
            MAIL_USERNAME = os.environ.get('SMTP_Username')
            MAIL_PASSWORD = os.environ.get('SMTP_Password')
            MAIL_DEFAULT_SENDER = '"PrepWithMo Associates" <mo@info.perfectscoremo.com>'

            USER_CORPORATION_NAME = 'PrepWithMo'
            USER_COPYRIGHT_YEAR = 2022


    except Exception as e:
        print("error in initialization")
        print(e)
        traceback.print_exc()
        #trigger10

