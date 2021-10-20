from flask import render_template, flash, make_response, redirect, url_for, request, jsonify, Response
from werkzeug.urls import url_parse
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.config import Config
from app.service import ValidateLogin
from app.service import User
from flask_login import login_user,login_required,current_user,logout_user
import logging
import traceback

from app import server
from app.aws import AWSInstance
from app.dbUtil import AppDBUtil
from flask_login import LoginManager
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = 'admin_login'

server.config.from_object(Config)
server.logger.setLevel(logging.DEBUG)
db = SQLAlchemy(server)
migrate = Migrate(server, db)
awsInstance = AWSInstance()




@server.route("/")
def hello():
    # server.logger.debug('Processing default request')
    return ("You have landed on the wrong page")


@server.route("/usercode.html")
def usercode():
    name = 'Mo'
    return render_template('usercode.html', name=name)


@server.route("/health")
def health():
    print("healthy!")
    return render_template('health.html')


@server.route('/validate_login', methods=['POST'])
def validate_login():
    username = request.form.to_dict()['username']
    password = request.form.to_dict()['password']
    validateLogin = ValidateLogin(username, password)
    if validateLogin.validateUserName() and validateLogin.validatePassword():
        flash('login successful')
        user = User(password)
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('transaction_setup')
        return redirect(next_page)
    else:
        flash('login failed')
        return redirect('/admin-login')


@server.route('/admin-login', methods=['GET', 'POST'])
def admin_login():
    return render_template('admin.html')



@server.before_first_request
def start_background_jobs_before_first_request():
    def background_job():
        try:
            print(" background job started")

        except Exception as e:
            print("Error in background job")
            print(e)
            traceback.print_exc()

    scheduler.add_job(background_job, 'cron', day_of_week='sat', hour='19', minute='45')
    scheduler.start()




