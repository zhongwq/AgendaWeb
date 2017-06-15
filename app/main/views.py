from flask import render_template, redirect, url_for, abort, flash
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileFrom, MeetingFrom, SearchMeetingForm, EditMeetingProfileFrom
from .. import db
from ..models import User, Meeting

@main.route('/')
def index():
	return render_template('index.html')

@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileFrom()
	if form.validate_on_submit():
		current_user.email = form.email.data
		current_user.phone = form.phone.data
		db.session.add(current_user)
		flash('Your profile has been updated.')
		return redirect(url_for('main.index'))
	form.email.data = current_user.email
	form.phone.data = current_user.phone
	return render_template('edit_profile.html', form=form)

@main.route('/show-users')
@login_required
def showUsers():
	users = User.query.all()
	return render_template('users.html', users=users)

@main.route('/createMeeting', methods=['GET', 'POST'])
@login_required
def createMeeting():
	form = MeetingFrom(user=current_user)
	if form.validate_on_submit():
		if form.startDate.data >= form.endDate.data:
			flash('The startDate should be earlier than the endDate! Fail to create the meeting!')
			return redirect(url_for('main.showAllMeetings'))
		sponsor_meetings = Meeting.query.filter_by(sponsor=current_user.username)
		for m in sponsor_meetings:
			if not (m.startDate >= form.endDate.data or m.endDate <= form.startDate.data):
				flash('The Meeting is conflict with your other meetings! Fail to create!')
				return redirect(url_for('main.showAllMeetings'))
		newMeeting = Meeting(title=form.title.data, startDate=form.startDate.data,
							endDate=form.endDate.data, sponsor=current_user.username)
		db.session.add(newMeeting)
		db.session.commit()
		for i in form.participator.data:
			u = User.query.filter_by(id=i).first()
			if not newMeeting.addParticipator(u):
				db.session.delete(newMeeting)
				db.session.commit()
				flash('Some participator is not availible!Fail to create new meeting!')
				return redirect(url_for('main.showAllMeetings'))
		flash('Create meeting successfully!')
		return redirect(url_for('main.showAllMeetings'))
	return render_template('create_meeting.html', form=form)



@main.route('/allMeeting')
@login_required
def showAllMeetings():
	allMeetings = Meeting.query.all()
	meetings = Meeting.query.filter_by(sponsor=current_user.username)
	s = set()
	for m in allMeetings:
		if m.is_participator(current_user):
			s.add(m)
	return render_template('meetings.html', title='All Meeting List',meetings=meetings, meetings_1=s)





@main.route('/sponsorMeeting')
@login_required
def showSponsorMeeting():
	meetings = Meeting.query.filter_by(sponsor=current_user.username)
	return render_template('meetings.html',meetings=meetings, title='Sponsor Meeting List')



@main.route('/participateMeeting')
@login_required
def showParticipateMeeting():
	allMeetings = Meeting.query.all()
	s = set()
	for m in allMeetings:
		if m.is_participator(current_user):
			s.add(m)
	return render_template('meetings.html',meetings=s, title='Participate Meeting List')


@main.route('/searchMeeting', methods=['GET','POST'])
@login_required
def searchMeeting():
	form = SearchMeetingForm()
	if form.validate_on_submit():
		if form.startDate.data >= form.endDate.data:
			flash('The startDate should be earlier than the endDate! Fail to search meetings')
			return redirect(url_for('main.searchMeeting'))
		sDate = form.startDate.data
		eDate = form.endDate.data
		meetings = Meeting.query.all()
		result = set()
		for i in meetings:
			if (i.is_participator(current_user) or i.sponsor == current_user.username) and not (eDate < i.startDate or sDate > i.endDate):
				result.add(i)
		return render_template('meetings.html',meetings=result, title='Result')
	return render_template('search_meeting.html',form=form)


@main.route('/meeting/<title>')
@login_required
def MeetingDetail(title):
	meeting = Meeting.query.filter_by(title=title).first()
	if meeting is None:
		abort(404)
	participators = set()
	for user in User.query.all():
		if meeting.is_participator(user):
			participators.add(user)
	return render_template('meeting_detail.html',meeting=meeting,participators=participators)


@main.route('/quitmeeting/<title>')
@login_required
def quitMeeting(title):
	meeting = Meeting.query.filter_by(title=title).first()
	if meeting is None:
		flash('Invalid Meeting!')
		return redirect(url_for('main.showAllMeetings'))
	if not meeting.is_participator(current_user):
		flash('You are not participating in the meeting!')
	meeting.deleteParticipator(current_user)
	if meeting.empty():
		db.session.delete(meeting)
		db.session.commit()
	flash('You are now quit the meeting named %s!' % meeting.title)
	return redirect(url_for('main.showAllMeetings'))

@main.route('/deleteMeeting/<title>')
@login_required
def deleteMeeting(title):
	meeting = Meeting.query.filter_by(title=title).first()
	if meeting is None:
		abort(404)
	if meeting.sponsor != current_user.username:
		flash('Your are not the sponsor of the meeting, you can not delete the meeting!')
		redirect('main.MeetingDetail',title=title)
	db.session.delete(meeting)
	db.session.commit()
	flash('You delete the meeting successfully!')
	return redirect(url_for('main.showAllMeetings'))


@main.route('/editMeeting/<title>', methods=['GET', 'POST'])
@login_required
def editMeeting(title):
	meeting = Meeting.query.filter_by(title=title).first()
	if meeting is None:
		abort(404)
	if meeting.sponsor != current_user.username:
		flash('Your are not the sponsor of the meeting, you can not add participator or delete participator!')
		return redirect(url_for('main.MeetingDetail',title=title))
	allUsers = User.query.all()
	u_tmp = set()
	p_tmp = set()
	for u in allUsers:
		if meeting.is_participator(u):
			p_tmp.add(u.id)
			u_tmp.add(u)
	form = EditMeetingProfileFrom(current_user)
	if form.validate_on_submit():
		for u in u_tmp:
			meeting.deleteParticipator(u)
		for uid in form.participator.data:
			u = User.query.filter_by(id=uid).first()
			meeting.addParticipator(u)
		return redirect(url_for('main.MeetingDetail',title=title))
	form.participator.data = p_tmp
	return render_template('edit_meeting.html', form=form, meeting=meeting)
