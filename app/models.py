import datetime
from time import sleep
from flask import current_app, request
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager
from .email import send_email


participate = db.Table('participate',
                      db.Column('meetingTitle', db.String(30), db.ForeignKey('meetings.title')),
                      db.Column('participatorName', db.String(30), db.ForeignKey('users.username'))
)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, index = True)
    email = db.Column(db.String(60), index=True)
    password_hash = db.Column(db.String(128))
    phone = db.Column(db.String(12))
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Meeting(db.Model):
    __tablename__ = 'meetings'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(30), unique=True, index = True)
    sponsor = db.Column(db.String(30), index=True)
    startDate = db.Column(db.DateTime())
    endDate = db.Column(db.DateTime())
    participator = db.relationship('User', secondary=participate,
        primaryjoin = (participate.c.meetingTitle == title),
        secondaryjoin = (participate.c.participatorName == User.username),
        backref=db.backref('meeting', lazy='dynamic'), lazy='dynamic')

    def addParticipator(self, user):
        if not self.is_participator(user):
            meetings = Meeting.query.filter_by(sponsor=user.username or is_participator(user))
            for meeting in meetings:
                if not(self.startDate >= meeting.endDate or self.endDate <= meeting.startDate):
                    return False
            self.participator.append(user)
            db.session.add(self)
            db.session.commit()
            return True


    def deleteParticipator(self, user):
        if self.is_participator(user):
            self.participator.remove(user)
            return self

    def empty(self):
        if self.participator.count() == 0:
            return True

    def is_participator(self, user):
        return self.participator.filter(participate.c.participatorName == user.username).count() > 0

    def sendEmailToAll(self):
        temp = User.query.filter_by(username=self.sponsor).first()
        send_email(temp.email, 'Meeting Reminder', 'email/reminder', user=temp, meeting=self)
        for i in self.participator:
            send_email(i.email, 'Meeting Reminder', 'email/reminder', user=i, meeting=self)
 
def scan(app):
    with app.app_context():
        while True:
            meetings = Meeting.query.all()
            for m in meetings:
                temp = m.startDate - datetime.datetime.now();
                print (m.startDate)
                print (datetime.datetime.now())
                print (temp <= datetime.timedelta(0,1800) and temp > datetime.timedelta(0,1780))
                if temp <= datetime.timedelta(0,1800) and temp > datetime.timedelta(0,1780):
                    m.sendEmailToAll()
            sleep(20)
