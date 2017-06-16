import os
from app import create_app, db
from app.models import User, Meeting, scan
from threading import Thread
from datetime import datetime
from flask_script import Manager, Shell
from flask import current_app

app = create_app()
manager = Manager(app)

def make_shell_context():
    return dict(app=app, db=db, User=User, Meeting=Meeting)

manager.add_command("shell", Shell(make_context=make_shell_context))

@app.before_first_request
def run_scan():
	c_app = current_app._get_current_object()
	scan_task = Thread(target=scan, args=[c_app])
	scan_task.start()

if __name__ == '__main__':
	manager.run()