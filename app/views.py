import ast
import os
import pytz
from flask import render_template, flash, make_response, redirect, url_for, request, jsonify, Response
import datetime
from app.config import Config
from app.models import Tutor,User
from flask_login import login_user,login_required,current_user,logout_user
from flask_user import roles_required, UserManager
import logging
import traceback
import json
from apscheduler.schedulers.background import BackgroundScheduler
from service import SendMessagesToClients

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)

from app import server,db
from app.dbUtil import AppDBUtil
from flask_login import LoginManager
login_manager = LoginManager()
login_manager.init_app(server)
#login_manager.login_view = 'login'

from wtforms import StringField
from wtforms.fields.html5 import TelField
from wtforms.validators import DataRequired

# Customize the Register form:
from flask_user.forms import RegisterForm
class CustomRegisterForm(RegisterForm):
    # Add a country field to the Register form
    first_name = StringField(('First name'), validators=[DataRequired()])
    last_name = StringField(('Last name'), validators=[DataRequired()])
    phone_number = TelField(('Phone number'), validators=[DataRequired()])

# Customize the User profile form:
from flask_user.forms import EditUserProfileForm
class CustomUserProfileForm(EditUserProfileForm):
    # Add a country field to the UserProfile form
    first_name = StringField(('First name'), validators=[DataRequired()])
    last_name = StringField(('Last name'), validators=[DataRequired()])
    phone_number = TelField(('Phone number'), validators=[DataRequired()])

# Customize Flask-User
class CustomUserManager(UserManager):
    def customize(self, app):
        # Configure customized forms
        self.RegisterFormClass = CustomRegisterForm
        self.UserProfileFormClass = CustomUserProfileForm
        # NB: assign:  xyz_form = XyzForm   -- the class!
        #   (and not:  xyz_form = XyzForm() -- the instance!)

user_manager = CustomUserManager(server, db, User)
#user_manager = UserManager(server, db, User)

server.config.from_object(Config)
server.logger.setLevel(logging.DEBUG)

@server.route("/")
@login_required
def root_route():
    is_admin = False
    for role in current_user.roles:
        if role.name == 'admin':
            is_admin = True
    if is_admin:
        return redirect(url_for('admin_services'))
    else:
        return redirect(url_for('associate_services'))


@server.route("/associate_services",methods=['GET'])
@login_required
def associate_services():
    return render_template('associate_services.html')

@server.route("/health",methods=['GET','POST'])
@login_required
def health():
    print("healthy!")
    return render_template('health.html')

@server.route("/submit_hours",methods=['GET','POST'])
@login_required
def submit_hours():
    day = request.form['day']
    hours = request.form['hours']
    memo = request.form['memo']
    submit_hours_worked_message = AppDBUtil.submitHoursWorked(tutor_email=current_user.email, day=day, hours=hours, memo=memo)
    flash(submit_hours_worked_message)
    #return render_template('enter_hours.html')
    return redirect(url_for('associate_services'))


@server.route('/logout', methods=['GET'])
@login_required
def logout():
    user = current_user
    #AppDBUtil.logoutUserInDB(user)
    logout_user()
    return redirect('user/sign-in')

@server.route('/admin_services',methods=['GET','POST'])
@roles_required('admin')
def admin_services():
    return render_template('admin_services.html',transaction_setup_url=os.environ['transaction_setup_url'],lead_info_url=os.environ['lead_info_url'])


@server.route('/assign_unassign_tutor',methods=['GET','POST'])
@roles_required('admin')
def assign_unassign_tutor():
    if request.method == 'GET':
        tutors_data,students_data = [],[]
        tutors = AppDBUtil.getTutors()
        students = AppDBUtil.getStudents()
        for tutor in tutors:
            tutors_data.append(tutor.tutor_first_name + " " + tutor.tutor_last_name+" "+"("+tutor.tutor_email+")")
        for student in students:
            students_data.append(student.student_first_name+" "+student.student_last_name+" "+"("+student.student_email+")")
        return render_template('assign_unassign_tutor.html', tutors_data=tutors_data, students_data=students_data)
    elif request.method == 'POST':
        assign_unassign_tutor_contents = request.form.to_dict()
        print(assign_unassign_tutor_contents)

        if assign_unassign_tutor_contents:
            tutor_email = assign_unassign_tutor_contents['tutor_data'].split('(')[1].split(')')[0]
            student_email = assign_unassign_tutor_contents['student_data'].split('(')[1].split(')')[0]
            assign_unassign_result_message = AppDBUtil.assignUnassign(tutor_email,student_email,assign_unassign_tutor_contents['submit'])
            flash(assign_unassign_result_message)
        return redirect('assign_unassign_tutor')
    
 #TODO literally wrap every url in a try catch ? will that cause too much clutter? pro is you will avoid silent errors where things look good on the front end despite problems ont he back end
@server.route('/add_students_one_time',methods=['GET','POST'])
@login_required
def add_students_one_time():
    if request.method == 'GET':
        tutors_emails = []

        for tutor in AppDBUtil.getTutors():
            if tutor != current_user.email:
                tutors_emails.append(tutor.tutor_email)

        tutors_info = {}
        students_info = {}
        tutor_students_assignments = AppDBUtil.getTutorStudentsAssignment(tutors_emails=tutors_emails)

        for assignment in tutor_students_assignments:
            students_info.update({assignment.student_email: assignment.student_first_name + " " + assignment.student_last_name+" ("+assignment.student_email+")"})
            tutors_info.update({assignment.tutor_email: assignment.tutor_first_name + " " + assignment.tutor_last_name+" ("+assignment.tutor_email+")"})
        return render_template('add_students_one_time.html', tutors_info=json.dumps(tutors_info), students_info=json.dumps(students_info))
    elif request.method == 'POST':
        students_to_search_for = request.form.to_dict()
        logger.debug('Tutors to search for are: {}'.format(str(students_to_search_for['tutors_to_add'])))
        logger.debug('Students to search for are: {}'.format(str(students_to_search_for['students_to_add'])))
        tutors_to_add = students_to_search_for['tutors_to_add'].split('\r\n')
        students_to_add = students_to_search_for['students_to_add'].split('\r\n')
        extra_students = {'tutors_to_add':tutors_to_add,'students_to_add':students_to_add}
        logger.debug('Extra tutors and students are: {}'.format(str(extra_students)))
        return redirect(url_for('students_reports',extra_students=extra_students))

#@server.route('/students_reports',methods=['GET','POST'])
@server.route('/students_reports',defaults={'extra_students': None}, methods=['GET','POST'])
@server.route('/students_reports/<extra_students>', methods=['GET','POST'])
@login_required
def students_reports(extra_students):
    try:
        if request.method == 'GET':
            logger.debug("In GET for students_reports")
            extra_students = ast.literal_eval(extra_students) if extra_students else {}
            tutors_emails = [current_user.email]
            tutors_emails.extend(extra_students.get('tutors_to_add',''))

            students_names_data, students_emails_data, students_ids_data = [], [], []
            tutor_student_assignments = AppDBUtil.getTutorStudentsAssignment(tutors_emails=tutors_emails)

            for assigned_student in tutor_student_assignments:
                student = AppDBUtil.getStudentsByEmails(students_emails=[assigned_student.student_email])[0]
                students_names_data.append(assigned_student.student_first_name + " " + assigned_student.student_last_name)
                students_emails_data.append(assigned_student.student_email)
                students_ids_data.append(student.student_id)

            for retrieved_student in AppDBUtil.getStudentsByEmails(students_emails=extra_students.get('students_to_add',[])):
                print("student id is ", retrieved_student.student_id)
                students_names_data.append(retrieved_student.student_first_name + " " + retrieved_student.student_last_name)
                students_emails_data.append(retrieved_student.student_email)
                students_ids_data.append(retrieved_student.student_id)

            return render_template('students_reports.html',students_names_data=students_names_data,students_ids_data=students_ids_data,students_emails_data=students_emails_data)
        elif request.method == 'POST':
            logger.debug("In POST for students_reports")
            students_reports_contents = request.form.to_dict()
            # auto send reports for trusted tutors
            is_trusted_tutor = False
            for role in current_user.roles:
                if role.name == 'trusted_tutor':
                    is_trusted_tutor = True

            all_students_reports_to_send = {}
            for key, content in students_reports_contents.items():
                if len(key.split('_vensti_')) > 1:
                    student_email = key.split('_vensti_')[0]
                    report_type = key.split('_vensti_')[1]
                    this_student_report_to_send = all_students_reports_to_send.get(student_email, {})
                    this_student_report_to_send.update({report_type: content})
                    all_students_reports_to_send.update({student_email: this_student_report_to_send})

            logger.debug("Reports received from frontend for saving and/or sending are: "+str(all_students_reports_to_send))
            for key, content in all_students_reports_to_send.items():
                if is_trusted_tutor and content.get('send_report','') == 'send':
                    memos, not_memos = {}, {}
                    report_date = datetime.datetime.strftime(datetime.datetime.now(pytz.timezone('US/Central')), "%m/%d/%Y")

                    content['report_date'] = report_date
                    report_day = datetime.datetime.now(pytz.timezone('US/Central')).strftime('%A')
                    memos.update({'title': "Report for {} ({})".format(report_day, report_date)})
                    for k, v in content.items():
                        if k.startswith('memo_1'):
                            memo_key = "Topics Covered"
                            memos.update({memo_key: SendMessagesToClients.cleanMessage(v)})
                        elif k.startswith('memo_2'):
                            memo_key = "Homework Assigned"
                            memos.update({memo_key: SendMessagesToClients.cleanMessage(v)})
                        elif k.startswith('memo_3'):
                            memo_key = "Miscellanous Comments"
                            memos.update({memo_key: SendMessagesToClients.cleanMessage(v)})
                        else:
                            not_memos.update({k: SendMessagesToClients.cleanMessage(v)})

                    student = dict(AppDBUtil.getStudentsByEmails(students_emails=[key])[0])
                    to_numbers = [number for number in [student['parent_1_phone_number'], student['parent_2_phone_number'], student['student_phone_number']] if number != '']
                    SendMessagesToClients.sendSMS(to_numbers=to_numbers, message_as_text=memos, message_as_image=not_memos)
                    flash("Report successfully sent for trusted tutor.")

            # save reports
            save_students_reports_message,next_page,submitted_successfully = AppDBUtil.saveStudentsReports(tutor_email=current_user.email, students_reports_contents=students_reports_contents)

            logger.debug('save_students_reports_message is: '+ str(save_students_reports_message))
            logger.debug('next_page is: ' + str(next_page))
            logger.debug('submitted_successfully is: ' + str(submitted_successfully))

            if next_page == 'hours':
                if submitted_successfully:
                    flash(save_students_reports_message)
                    return render_template('enter_hours.html')
                else:
                    next_page = 'students_reports'
                    save_students_reports_message = 'Weird. Cannot submit hours without submitting reports. Contact Mo.'
                    flash(save_students_reports_message)
                    return redirect(url_for(next_page))
            else:
                flash(save_students_reports_message)
                return redirect(url_for(next_page))
    except Exception as e:
        flash("Error in saving or sending reports. Contact Mo.")
        print(e)
        traceback.print_exc()
        return redirect(url_for('students_reports'))
    finally:
        pass


# @server.route('/twilio', methods=['GET','POST'])
# @login_required
# def twilio():
#     account_sid = SendMessagesToClients.awsInstance.get_secret("twilio_cred", "TWILIO_ACCOUNT_SID") or os.environ['TWILIO_ACCOUNT_SID']
#     auth_token = SendMessagesToClients.awsInstance.get_secret("twilio_cred", "TWILIO_AUTH_TOKEN") or os.environ['TWILIO_AUTH_TOKEN']
#     twilioClient = TwilioClient(account_sid, auth_token)
#
#     # twilioClient.messaging.services('MGd37b2dce09791f42239043b6e949f96b').delete()
#     conversations = twilioClient.conversations.conversations.list(limit=100)  #
#     for record in conversations:
#         print(record.sid)
#         twilioClient.conversations.conversations(record.sid).delete()
#
#     listToVerifyDeleteComplete = twilioClient.conversations.conversations.list(limit=100)
#     print("listToVerifyDeleteComplete is: ", listToVerifyDeleteComplete)
#     while listToVerifyDeleteComplete:
#         print("Waiting for 2 seconds to give deletion action time to complete before proceeding.")
#         time.sleep(2)
#         listToVerifyDeleteComplete = twilioClient.conversations.conversations.list(limit=100)
#
#     conversation = twilioClient.conversations.conversations.create(messaging_service_sid='MG0faa1995ce52477a642163564295650c', friendly_name='DailyReport')
#     print("conversation created!")
#     print(conversation.sid)
#
#     twilioClient.conversations.conversations(conversation.sid).participants.create(messaging_binding_projected_address='+19564771274')
#     twilioClient.conversations.conversations(conversation.sid).participants.create(messaging_binding_address='+19725847364')
#
#     for to_number in to_numbers:
#         print("to_number is ", to_number)
#         twilioClient.conversations.conversations(conversation.sid).participants.create(messaging_binding_address='+1' + to_number)
#
#     CreateMessageAsImage.writeTextAsImage(message_as_image)
#     message_as_text_to_send = '' + message_as_text.get('title', '') + "\n\n"
#
#     for k, v in message_as_text.items():
#         if k != 'title':
#             message_as_text_to_send = message_as_text_to_send + "\n\n" + k + ": \n\n" + v + "\n\n"
#
#     message_as_text_to_send = message_as_text_to_send + "\n\n" + "Regards," + " \n" + "Mo" + "\n\n"
#
#     media_sid = CreateMessageAsImage.uploadMessageImage(account_sid, auth_token, conversation.chat_service_sid)
#     twilioClient.conversations.conversations(conversation.sid).messages.create(media_sid=media_sid, author='+19564771274')
#     time.sleep(2)  # wait before next send to help ensure order
#     twilioClient.conversations.conversations(conversation.sid).messages.create(body=message_as_text_to_send, author='+19564771274')
#     print("texts sent!")


@server.route('/view_hours', methods=['GET','POST'])
@login_required
def view_hours():
    hours_worked_by_day = ''
    tutors = {}
    is_admin = False
    for role in current_user.roles:
        if role.name == 'admin':
            is_admin = True
    if is_admin:
        for tutor in AppDBUtil.getTutors():
            tutors.update({tutor.tutor_email:tutor.tutor_first_name+" "+tutor.tutor_last_name})
    if request.method == 'POST':
        view_hours_contents = request.form.to_dict()
        tutor_email = view_hours_contents.get('tutor',current_user.email)
        hours_worked_by_day = AppDBUtil.getHoursWorked(tutor_email=tutor_email,month=view_hours_contents['month'],year=view_hours_contents['year'])
    #print(hours_worked_by_day)
    #print(tutors)
    return render_template('view_hours.html', hours_worked_by_day=hours_worked_by_day,tutors=tutors)

@server.route("/view_memos",methods=['GET','POST'])
@login_required
def view_memos():
    try:
        tutors_emails = []
        is_trusted_tutor = False
        for role in current_user.roles:
            if role.name == 'trusted_tutor':
                is_trusted_tutor = True

        is_admin = False
        for role in current_user.roles:
            if role.name == 'admin':
                is_admin = True

        if is_trusted_tutor:
            for tutor in AppDBUtil.getTutors():
                tutors_emails.append(tutor.tutor_email)
        else:
            tutors_emails.append(current_user.email)

        tutors_info = {}
        students_info = {}
        students_reports = ''
        tutor_students_assignments = AppDBUtil.getTutorStudentsAssignment(tutors_emails=tutors_emails)

        for assignment in tutor_students_assignments:
            students_info.update({assignment.student_email:assignment.student_first_name+" "+assignment.student_last_name})
            tutors_info.update({assignment.tutor_email:assignment.tutor_first_name+" "+assignment.tutor_last_name})

        if request.method == 'POST':
            view_memos_contents = request.form.to_dict()
            if  view_memos_contents['submit'] == "View":
                students_reports = {}
                if view_memos_contents['search_by_tutor_or_student'] == 'search_by_tutor':
                    existing_submission_by_tutor = AppDBUtil.getStudentsReports(tutor_email=view_memos_contents['tutor_or_student_list'],start_date=view_memos_contents['start_date'],end_date=view_memos_contents['end_date'])
                elif view_memos_contents['search_by_tutor_or_student'] == 'search_by_student':
                    existing_submission_by_tutor = AppDBUtil.getStudentsReports(student_email=view_memos_contents['tutor_or_student_list'],start_date=view_memos_contents['start_date'],end_date=view_memos_contents['end_date'])

                for report in existing_submission_by_tutor:
                    report_by_day = students_reports.get(report.day.strftime('%m/%d/%Y'), {})
                    student = dict(AppDBUtil.getStudentsByEmails(students_emails=[report.student_email])[0])
                    print(student)
                    report_by_day.update({report.student_email: [student['student_first_name']+" "+student['student_last_name'],report.attendance, report.home_work, report.memo_1, report.memo_2, report.memo_3]})
                    students_reports.update({report.day.strftime('%m/%d/%Y'):report_by_day})

            elif  view_memos_contents['submit'] == "Send":
                all_students_reports_to_send = {}
                for key,content in view_memos_contents.items():
                    if len(key.split('_vensti_')) > 1:
                        student_email = key.split('_vensti_')[0]
                        report_type = key.split('_vensti_')[1]
                        this_student_report_to_send = all_students_reports_to_send.get(student_email,{})
                        this_student_report_to_send.update({report_type:content})
                        all_students_reports_to_send.update({student_email:this_student_report_to_send})

                print(all_students_reports_to_send)
                for key,content in all_students_reports_to_send.items():
                    if content.get('send_report','') == 'send':
                        memos,not_memos = {},{}
                        report_date = content.get('report_date','')
                        report_day = datetime.datetime.strptime(report_date, "%m/%d/%Y").strftime('%A')
                        memos.update({'title':"Report for {} ({})".format(report_day, report_date)})
                        for k,v in content.items():
                            if k.startswith('memo_1'):
                                memo_key = "Topics Covered"
                                memos.update({memo_key:SendMessagesToClients.cleanMessage(v)})
                            elif k.startswith('memo_2'):
                                memo_key = "Homework Assigned"
                                memos.update({memo_key:SendMessagesToClients.cleanMessage(v)})
                            elif k.startswith('memo_3'):
                                memo_key = "Miscellanous Comments"
                                memos.update({memo_key:SendMessagesToClients.cleanMessage(v)})
                            else:
                                not_memos.update({k:SendMessagesToClients.cleanMessage(v)})
                        student = dict(AppDBUtil.getStudentsByEmails(students_emails=[key])[0])
                        to_numbers = [number for number in [student['parent_1_phone_number'],student['parent_2_phone_number'],student['student_phone_number']] if number != '']
                        SendMessagesToClients.sendSMS(to_numbers=to_numbers,message_as_text=memos,message_as_image=not_memos)
                        flash("Report successfully sent from admin page.")

            print(view_memos_contents)
            print(students_info)
            print(tutors_info)

    except Exception as e:
        flash("Error in viewing or sending reports. Contact Mo.")
        print(e)
        traceback.print_exc()
    finally:
        return render_template('view_memos.html', tutors_info=json.dumps(tutors_info), students_info=json.dumps(students_info), students_reports=students_reports, is_admin=is_admin)


@server.route('/send_message',methods=['GET','POST'])
#@roles_required('admin')
def send_message():
    return render_template('send_message.html')


@login_manager.user_loader
def load_user(user_id):
    #return User.query.get(email)
    user = User.query.filter_by(id=user_id).first()
    if user:
        return user
    return None

#trigger
@server.before_first_request
def start_background_jobs_before_first_request():
    def background_job():
        try:
            print(" background job started")
        except Exception as e:
            print("Error in background job")
            print(e)
            traceback.print_exc()

    scheduler = BackgroundScheduler(timezone='US/Central')
    scheduler.add_job(background_job, 'cron', day_of_week='sat', hour='19', minute='45')
    scheduler.start()




