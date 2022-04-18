from app import db
import datetime
import calendar
from app.models import TutorHours, TutorStudentAssignment, Tutor, Student, StudentsReports
import logging
import traceback
import pytz
from sqlalchemy.dialects.postgresql import insert

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


class AppDBUtil():
    def __init__(self):
        pass

    # @classmethod
    # def loginUserInDB(cls, tutor=None, enter_password=None):
    #     if enter_password:
    #         tutor.tutor_password_hash = generate_password_hash(enter_password)
    #     tutor.is_tutor_authenticated = True
    #     db.session.add(tutor)
    #     cls.executeDBQuery()
    #     return tutor

    # @classmethod
    # def logoutUserInDB(cls, tutor=None):
    #     tutor.is_tutor_authenticated = False
    #     db.session.add(tutor)
    #     cls.executeDBQuery()

    @classmethod
    def submitHoursWorked(cls, tutor_email = None, day=None, hours=None, memo=None):
        try:
            hours_worked = db.session.query(TutorHours).filter((TutorHours.tutor_email == tutor_email) & (TutorHours.day == day)).first()

            if hours_worked:
                submit_hours_worked_message = "Hours not saved. You already entered hours for today."
            else:
                hours_worked = TutorHours(tutor_email=tutor_email, day=day, hours=hours, memo=memo)
                db.session.add(hours_worked)
                cls.executeDBQuery()
                submit_hours_worked_message = "Hours added successfully. "
        except Exception as e:
            print(e)
            print(traceback.print_exc())
            submit_hours_worked_message = "Error in entering hours. Contact Mo."
        finally:
            return submit_hours_worked_message

        # hours_worked = HoursWorked(tutor_email=tutor_email,date=hours_worked_contents.get('date',''),hours=hours_worked_contents.get('hours',''),
        #                            memo=hours_worked_contents.get('memo',''),submitted=False)
        # db.session.add(hours_worked)
        # cls.executeDBQuery()

    @classmethod
    def getHoursWorked(cls, tutor_email=None, month=None, year=None):
        start_of_month = datetime.datetime(int(year),int(month),1)
        end_of_month = datetime.datetime(int(year), int(month), calendar.monthrange(int(year), int(month))[1])
        hours_worked = TutorHours.query.filter((TutorHours.tutor_email == tutor_email) & (TutorHours.day.between(start_of_month, end_of_month))).all()

        hours_worked_by_day = {}
        for record in hours_worked:
            hours_worked_by_day.update({record.day.strftime('%m/%d/%Y'): [record.hours, record.memo]})

        return hours_worked_by_day

    @classmethod
    def getTutors(cls):
        tutors = Tutor.query.filter(Tutor.is_active == True).all()
        return tutors

    @classmethod
    def getStudents(cls):
        students = db.session.query(Student).filter(Student.c.is_active == True).all()
        return students

    @classmethod
    def getStudentsByEmails(cls, students_emails=[]):
        students = db.session.query(Student).filter((Student.c.student_email.in_(students_emails)), Student.c.is_active == True).all()
        return students

    @classmethod
    def getTutorStudentsAssignment(cls, tutors_emails=[]):
        tutor_student_assignments = TutorStudentAssignment.query.filter((TutorStudentAssignment.tutor_email.in_(tutors_emails))).all()
        return tutor_student_assignments


    @classmethod
    def assignUnassign(cls,selected_tutor_email,selected_student_email,selected_action):
        try:
            if selected_action == 'Assign':
                tutor_student_assignments = TutorStudentAssignment.query.filter((TutorStudentAssignment.tutor_email == selected_tutor_email) & (TutorStudentAssignment.student_email == selected_student_email)).all()
                #print(tutor_student_assignments)
                if tutor_student_assignments:
                    assign_unassign_result_message = 'Tutor previously assigned to student.'
                else:
                    print(selected_student_email)
                    student =   db.session.query(Student).filter(Student.c.student_email == selected_student_email).first()
                    tutor = Tutor.query.filter(Tutor.tutor_email == selected_tutor_email).first()
                    # print(tutor.tutor_first_name)
                    tutor_student_assignments = TutorStudentAssignment(tutor_first_name=tutor.tutor_first_name, tutor_last_name=tutor.tutor_last_name, tutor_email=selected_tutor_email, student_email=selected_student_email,
                                                            student_first_name=student.student_first_name, student_last_name=student.student_last_name)
                    db.session.add(tutor_student_assignments)
                    cls.executeDBQuery()
                    assign_unassign_result_message = 'Tutor assigned successfully.'
            elif selected_action == 'Unassign':
                tutor_student_assignments = TutorStudentAssignment.query.filter((TutorStudentAssignment.tutor_email == selected_tutor_email) & (TutorStudentAssignment.student_email == selected_student_email)).first()
                if tutor_student_assignments:
                    db.session.delete(tutor_student_assignments)
                    cls.executeDBQuery()
                    assign_unassign_result_message = 'Tutor unassigned successfully.'
                else:
                    assign_unassign_result_message = 'Tutor not currently assigned to student.'

        except Exception as e:
            print(e)
            print(traceback.print_exc())
            assign_unassign_result_message = 'Error assigning or unassigning tutor to student.'
        finally:
            return assign_unassign_result_message

    @classmethod
    def saveStudentsReports(cls, tutor_email, students_reports_contents):
        try:
            save_students_reports_message = 'Students reports successfully saved.'
            next_page = 'hours'
            submitted_successfully = False
            existing_submission_by_tutor = StudentsReports.query.filter((StudentsReports.tutor_email == tutor_email) & (StudentsReports.day == datetime.datetime.now(pytz.timezone('US/Central')).date())).first()

            if not students_reports_contents:
                save_students_reports_message = 'No report saved. No student has been assigned to you.'
                next_page = 'associate_services'
                return save_students_reports_message, next_page,submitted_successfully

            if existing_submission_by_tutor:
                save_students_reports_message = 'Report not saved. You already made your report submission for today.'
                next_page = 'associate_services'
                return save_students_reports_message,next_page,submitted_successfully

            for key,content in students_reports_contents.items():
                if key != 'submit':
                    student_email = key.split('_vensti_')[0]
                    report_type = key.split('_vensti_')[1]
                    if report_type == 'attendance':
                        statement = insert(StudentsReports).values(tutor_email=tutor_email, student_email=student_email,attendance=content,day=datetime.datetime.now(pytz.timezone('US/Central')).date())
                        statement = statement.on_conflict_do_update(
                            index_elements=['tutor_email','student_email','day'],
                            set_=dict(attendance=content)
                        )

                        db.session.execute(statement)
                        cls.executeDBQuery()

                    if report_type == 'home_work':

                        statement = insert(StudentsReports).values(tutor_email=tutor_email, student_email=student_email,home_work=content,day=datetime.datetime.now(pytz.timezone('US/Central')).date())
                        statement = statement.on_conflict_do_update(
                            index_elements=['tutor_email','student_email','day'],
                            set_=dict(home_work=content)
                        )

                        db.session.execute(statement)
                        cls.executeDBQuery()

                    if report_type == 'memo_1':

                        statement = insert(StudentsReports).values(tutor_email=tutor_email, student_email=student_email,memo_1=content,day=datetime.datetime.now(pytz.timezone('US/Central')).date())
                        statement = statement.on_conflict_do_update(
                            index_elements=['tutor_email','student_email','day'],
                            set_=dict(memo_1=content)
                        )

                        db.session.execute(statement)
                        cls.executeDBQuery()

                    if report_type == 'memo_2':

                        statement = insert(StudentsReports).values(tutor_email=tutor_email, student_email=student_email,memo_2=content,day=datetime.datetime.now(pytz.timezone('US/Central')).date())
                        statement = statement.on_conflict_do_update(
                            index_elements=['tutor_email','student_email','day'],
                            set_=dict(memo_2=content)
                        )

                        db.session.execute(statement)
                        cls.executeDBQuery()

                    if report_type == 'memo_3':

                        statement = insert(StudentsReports).values(tutor_email=tutor_email, student_email=student_email,memo_3=content,day=datetime.datetime.now(pytz.timezone('US/Central')).date())
                        statement = statement.on_conflict_do_update(
                            index_elements=['tutor_email','student_email','day'],
                            set_=dict(memo_3=content)
                        )

                        db.session.execute(statement)
                        cls.executeDBQuery()
            submitted_successfully = True

        except Exception as e:
            print(e)
            print(traceback.print_exc())
            save_students_reports_message = 'Error saving students reports. Contact Mo.'
            next_page = 'students_reports'
        finally:
            return save_students_reports_message,next_page,submitted_successfully

    @classmethod
    def getStudentsReports(cls, student_email=None, tutor_email=None, start_date=None, end_date=None):
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")

        if student_email:
            #existing_submission_by_tutor = StudentsReports.query.filter((StudentsReports.student_email == student_email) & (StudentsReports.day.between(start_date, end_date))).join(Student).filter(Student.is_active == True).all()
            existing_submission_by_tutor = StudentsReports.query.filter((StudentsReports.student_email == student_email) & (StudentsReports.day.between(start_date, end_date))).all()
        elif tutor_email:
            #existing_submission_by_tutor = StudentsReports.query.filter((StudentsReports.tutor_email == tutor_email) & (StudentsReports.day.between(start_date, end_date))).join(Tutor).filter(Tutor.is_active == True).all()
            existing_submission_by_tutor = StudentsReports.query.filter((StudentsReports.tutor_email == tutor_email) & (StudentsReports.day.between(start_date, end_date))).all()

        return existing_submission_by_tutor

    @classmethod
    def autoSendReportsForTrustedTutors(cls,tutor_email='', students_reports_contents={}):
        pass

    @classmethod
    def executeDBQuery(cls):
        try:
            db.session.commit()
        except Exception as e:
            # if any kind of exception occurs, rollback transaction
            db.session.rollback()
            traceback.print_exc()
            raise e
        finally:
            db.session.close()




