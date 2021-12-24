from __future__ import print_function
from googleapiclient.discovery import build
from google.oauth2 import service_account


class GoogleInstance():
    def __init__(self):
        pass

    @classmethod
    def getGoogleCredentials(cls):
        SCOPES = ['https://www.googleapis.com/auth/drive.metadata.readonly']
        SERVICE_ACCOUNT_FILE = '/app/vensti-df64afca06ca.json'

        credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        return credentials

    @classmethod
    def getFilesFromGoogleDrive(cls,creds=None):

        service = build('drive', 'v3', credentials=creds)

        # Call the Drive v3 API
        results = service.files().list(
            pageSize=10, fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])

        if not items:
            print('No files found.')
        else:
            print('Files:')
            for item in items:
                print(u'{0} ({1})'.format(item['name'], item['id']))


