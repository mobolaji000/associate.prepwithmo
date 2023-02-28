

from app import db, metadata, server
from flask_user import UserMixin, UserManager
from werkzeug.security import generate_password_hash,check_password_hash
from sqlalchemy import Table, event, update, insert


# Define the User data-model.
# NB: Make sure to add flask_user UserMixin !!!
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column('id',db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    email = db.Column('email',db.String(255), nullable=False, unique=True)
    email_confirmed_at = db.Column(db.DateTime())
    password = db.Column(db.String(255), nullable=False, server_default='')

    # User information
    first_name = db.Column('first_name',db.String(100), nullable=False, server_default='')
    last_name = db.Column('last_name',db.String(100), nullable=False, server_default='')
    phone_number = db.Column('phone_number',db.String(22), index=True, nullable=False, default='')

    # Define the relationship to Role via UserRoles
    roles = db.relationship('Role', secondary='user_roles')

    # One-to-one Relationship
    #tutor = db.relationship('Tutor', uselist=False)
    #


class Tutor(db.Model):
    __table_args__ = {'extend_existing': True}

    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'),primary_key=True)
    user = db.relationship('User', uselist=False)

    tutor_email = db.Column(db.String(48),  unique=True)
    tutor_first_name = db.Column(db.String(64), index=True, nullable=False, default='')
    tutor_last_name = db.Column(db.String(64),  index=True, nullable=False, default='')
    tutor_phone_number = db.Column(db.String(22), index=True,nullable=False, default='',)
    is_active = db.Column(db.Boolean(), nullable=False, server_default='1')

    def __repr__(self):
        return '<Tutor {} created>'.format(self.tutor_first_name)

class TutorStudentAssignment(db.Model):
    #tutor_email = db.Column(db.String(48), primary_key=True, index=True, nullable=False, default='')
    tutor_email = db.Column(db.String(48), db.ForeignKey('tutor.tutor_email'), primary_key=True, index=True, nullable=False, default='')
    tutor_first_name = db.Column(db.String(64), index=True, nullable=False, default='')
    tutor_last_name = db.Column(db.String(64), index=True, nullable=False, default='')
    #student_email = db.Column(db.String(48), primary_key=True, index=True, nullable=False, default='')
    student_email = db.Column(db.String(48), db.ForeignKey('student.student_email'), primary_key=True, index=True, nullable=False, default='')
    student_first_name = db.Column(db.String(64), index=True, nullable=False, default='')
    student_last_name = db.Column(db.String(64), index=True, nullable=False, default='')

    def __repr__(self):
        return '<Tutor {} assigned to Student {}>'.format(self.tutor_first_name, self.student_first_name)

class TutorHours(db.Model):
    tutor_email = db.Column(db.String(48), db.ForeignKey('tutor.tutor_email'), primary_key=True, index=True, nullable=False, default='')
    day = db.Column(db.Date,index=True,primary_key=True,nullable=True)
    hours = db.Column(db.Integer, index=True, nullable=True, default=-1)
    memo = db.Column(db.String(1064), index=True,nullable=False, default='')

    def __repr__(self):
        return '<TutorHours created for {},{}>'.format(self.tutor_email, self.day)

class StudentsReports(db.Model):
    tutor_email = db.Column(db.String(48), db.ForeignKey('tutor.tutor_email'), primary_key=True, index=True, nullable=False, default='')
    day = db.Column(db.Date,index=True,primary_key=True,nullable=True)
    student_email = db.Column(db.String(48), db.ForeignKey('student.student_email'), primary_key=True, index=True, nullable=False, default='')
    attendance = db.Column(db.String(4), index=True, nullable=False, default='')
    home_work = db.Column(db.String(4), index=True, nullable=False, default='')
    memo_1 = db.Column(db.String, index=True,nullable=False, default='')
    memo_2 = db.Column(db.String, index=True, nullable=False, default='')
    memo_3 = db.Column(db.String, index=True,nullable=False, default='')

    def __repr__(self):
        return '<TutorHours created for {},{}>'.format(self.tutor_email, self.day)

# Define the Role data-model
class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)

# Define the UserRoles association table
class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer(), primary_key=True)
    user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
    role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

#research that this was done right, including getting metadata
with server.app_context():
    Student = Table('student', metadata, autoload_with=db.engine)

@event.listens_for(User, 'after_insert')
def receive_after_insert(mapper, connection, target):
    with connection.begin() as trans:
        connection.execute(insert(Tutor).values(user_id=target.id,tutor_email=target.email,tutor_first_name=target.first_name,tutor_last_name=target.last_name,tutor_phone_number=target.phone_number,is_active=target.active))

@event.listens_for(User, 'after_update')
def receive_after_update(mapper, connection, target):
    with connection.begin() as trans:
        connection.execute(update(Tutor).where(target.id == Tutor.__table__.c.user_id).values(tutor_email=target.email,tutor_first_name=target.first_name,tutor_last_name=target.last_name,tutor_phone_number=target.phone_number,is_active=target.active))

db.create_all()
try:
    db.session.commit()
except:
    db.session.rollback()
    raise
finally:
    db.session.close()


