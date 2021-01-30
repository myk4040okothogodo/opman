from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required,current_user
from . import auth
from ..models import User
from .forms import LoginForm,RegistrationForm,ChangePasswordForm
from datetime import datetime
from .. import db


@auth.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash("invalid username or pasword","negative")
    return render_template('auth/login.html',  form=form, current_time=datetime.utcnow())

@auth.route('/register', methods=['GET','POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email= form.email.data,
                    username= form.username.data,
                    about_me =form.about_me.data,
                    password = form.password.data)
        db.session.add(user)
        flash("You can now login", "positive")
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form,current_time=datetime.utcnow())

@auth.route('/change-password', methods=['GET','POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password =form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash ('Your password has been updated.', 'positive')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid password,','negative')
    return render_template("auth/change_password.html", form=form,current_time=datetime.utcnow())        

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out!.", "negative")
    return redirect(url_for('main.index'))

"""
@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if  request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))
        
@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous :
        return redirect('main.index')
"""    
