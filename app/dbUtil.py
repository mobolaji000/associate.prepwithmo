from app import db
from datetime import datetime
import math
import uuid
from dateutil.parser import parse
import logging
import traceback

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


class AppDBUtil():
    def __init__(self):
        pass

    @classmethod
    def executeDBQuery(cls):
        try:
            db.session.commit()
        except Exception as e:
            # if any kind of exception occurs, rollback transaction
            db.session.rollback()
            traceback.print_exc()
        finally:
            db.session.close()




