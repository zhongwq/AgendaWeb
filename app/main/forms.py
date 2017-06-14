from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField, DateTimeField, IntegerField, BooleanField, SelectField,\
    SubmitField
from wtforms.validators import Required, Length, Email, Regexp
from wtforms import ValidationError
from ..models import Meeting, User


class MeetingFrom(FlaskForm):
	title = StringField('Title', validators=[Required(), Length(1,30)])
	startDate = DateTimeField('startDate(format:1992-02-23 22:38)', format='%Y-%m-%d %H:%M')
	endDate = DateTimeField('endDate(format:1992-02-23 23:38)', format='%Y-%m-%d %H:%M')
	participator = SelectMultipleField('participator', validators=[
		Required()], coerce=int)
	submit = SubmitField('Create')

	def __init__(self, user, *args, **kwargs):
		super(MeetingFrom,self).__init__(*args, **kwargs)
		temp = set()
		for s_user in User.query.all():
			if (s_user.username != user.username):
				temp.add(s_user);
		self.participator.choices = [(user.id, user.username) for user in temp]
		self.user = user
	
	def validate_title(self, field):
		if Meeting.query.filter_by(title=field.data).first():
			raise ValidationError('The title already in use!')

class EditProfileFrom(FlaskForm):
	email = StringField('Email', validators=[Required(), Length(1, 60),
											Email()])
	phone = IntegerField('Phone', validators=[Required()])
	submit = SubmitField('Finish')

class SearchMeetingForm(FlaskForm):
	startDate = DateTimeField('startDate(format:1992-02-23 22:38)', format='%Y-%m-%d %H:%M')
	endDate = DateTimeField('endDate(format:1992-02-23 23:38)', format='%Y-%m-%d %H:%M')
	submit = SubmitField('Search')

class EditMeetingProfileFrom(FlaskForm):
	participator = SelectMultipleField('participator', validators=[
		Required()], coerce=int)
	submit = SubmitField('Finish')

	def __init__(self, user, *args, **kwargs):
		super(EditMeetingProfileFrom,self).__init__(*args, **kwargs)
		temp = set()
		for s_user in User.query.all():
			if (s_user.username != user.username):
				temp.add(s_user);
		self.participator.choices = [(user.id, user.username) for user in temp]
		self.user = user