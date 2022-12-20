
from rq import get_current_job
from app import db, create_app, mail
from .models import Device, Task
from flask_mail import Message


def launch_task(app, name, description, *args, **kwargs):
    rq_job = app.task_queue.enqueue('app.task.' + name, *args, **kwargs)

    task = Task(id=rq_job.get_id(), name=name, description=description,)
    db.session.add(task)
    return task


def set_task_finished():
    task = Task.query.filter_by(id=get_current_job().get_id())
    task.complete = True
    db.session.commit()


def get_ip_geo_loc(client_ip):
    print(client_ip)
    try:
        
        app = create_app()
        with app.app_context():
            print("243343434344")

            ip_query = Device.query.filter_by(ip=client_ip).first()

            ip_query.country = "hund" 

            db.session.commit()
    except Exception as e:
        print(e)


def send_email(subject, sender, recipients, text_body, html_body, attachments=None):
    
    app = create_app()

    with app.app_context():

        msg = Message(subject, sender=sender, recipients=recipients)
        msg.body = text_body
        msg.html = html_body
        if attachments:
            for attachment in attachments:
                msg.attach(*attachment)
            
        mail.send(msg)

