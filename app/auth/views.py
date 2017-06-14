from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, \
    current_user
from . import auth
from .. import db
from ..models import User, Meeting
from .forms import LoginForm, RegisterForm, ResetPasswordForm, verifyPasswordForm

@auth.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is not None and user.verify_password(form.password.data):
			login_user(user, form.remember_me.data)
			return redirect(url_for('main.index'))
		flash('Invalid username or password.')
	return render_template('login.html', form=form) 

@auth.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm()
	if form.validate_on_submit():
		user = User(username=form.username.data,
					password=form.password.data,
					email=form.email.data,
					phone=form.phone.data)
		db.session.add(user)
		db.session.commit()
		flash('Register successfully!Please log in!')
		return redirect(url_for('auth.login'))
	return render_template('register.html', form=form)


@auth.route('/resetPassword', methods=['GET', 'POST'])
def resetPassword():
	form = ResetPasswordForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user is not None and user.phone == form.phone.data and user.email == form.email.data:
			user.password = form.password.data
			flash('Your password has been reset!')
			return redirect(url_for('auth.login'))

@auth.route('/logout')
@login_required
def logout():
	logout_user()
	flash('You have been logged out.')
	return redirect(url_for('main.index'))


@auth.route('/deleteAccount', methods=['GET', 'POST'])
@login_required
def delete_account():
	form = verifyPasswordForm()
	if form.validate_on_submit():
		if not current_user.verify_password(form.password.data):
			flash('Your password is wrong! Fail to delete your account!')
			return redirect(url_for('main.index'))
		meetings = Meeting.query.all()
		for meeting in meetings:
			if meeting.sponsor == current_user.username:
				db.session.delete(meeting)
			meeting.deleteParticipator(current_user)
			if meeting.empty():
				db.session.delete(meeting)
		db.session.delete(current_user)
		db.session.commit()
		flash('You delete your account successfully!')
		return redirect(url_for('main.index'))
	return render_template('deleteAccount.html', form=form)