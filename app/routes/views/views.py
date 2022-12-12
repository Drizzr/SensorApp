from secrets import token_hex
from flask import render_template, request, flash, redirect, url_for
from flask_login import current_user, login_required
from app.models import  Room, Sensor
from app import db
from app.utils.forms import  RegisterSensorForm, RegisterRoomForm
from flask import Blueprint
from app.utils.analytics import tracking


views = Blueprint('views', __name__)


@views.before_request
def request_callback():
    tracking(view=True)


@views.route('/', methods=["GET"])
def landing():
    # returns the landing page
    return render_template("view-templates/landing.html", user=current_user)


@views.route('/home', methods=["GET"])
@login_required
def home():
    # returns the individual user homepage
    return render_template("view-templates/home.html", user=current_user)


@views.route('/register-room', methods=["GET", "POST"])
@login_required
def registerRoom():
    form = RegisterRoomForm(request.form)
    if form.validate_on_submit():
        name = form.name.data
        description = form.description.data

        new_room = Room(name=name,
                        description=description,
                        user_id=current_user.id,
                        public_id=token_hex(8)
                        )

        db.session.add(new_room)
        db.session.commit()
        flash(u"New room created: " + new_room.name, category='success')
        return redirect(url_for("views.home"))
    return render_template("view-templates/registerRoom.html", user=current_user, form=form)


@views.route('/room/<room_id>/', methods=["GET"])
@login_required
def roomView(room_id):
    room = Room.query.filter_by(public_id=room_id, user_id=current_user.id).first_or_404()
    return render_template("view-templates/roomView.html", user=current_user, room=room)


@views.route('/room/<room_id>/register-sensor', methods=["GET", "POST"])
@login_required
def registerSensor(room_id):
    form = RegisterSensorForm(request.form)
    room = Room.query.filter_by(public_id=room_id, user_id=current_user.id).first_or_404()

    if form.validate_on_submit():
        name = form.name.data
        value1 = form.value1.data
        value2 = form.value2.data
        value3 = form.value3.data

        new_sensor = Sensor(
            name=name,
            public_id=token_hex(8),
            room_id=room.id,
            user_id=current_user.id,
            last_update=""
        )

        value_map = {}

        value_map[value1] = {"unit": form.unit1.data, "color": "rgba(0,0,0, 0.2)"}
        if value2:
            value_map[value2] = {"unit": form.unit2.data, "color": "rgba(255,51,51, 0.2)"}
        if value3:
            value_map[value3] = {"unit": form.unit3.data, "color": "rgba(51,153,255, 0.2)"}

        new_sensor.value_map = value_map

        db.session.add(new_sensor)
        db.session.flush()
        db.session.commit()
        flash(u"New sensor created: " + new_sensor.name, category="success")
        return redirect(url_for('views.roomView', room_id=room.public_id))
    return render_template("view-templates/registerSensor.html", user=current_user, room=room, form=form)


@views.route('/sensor/<sensor_id>/', methods=["GET"])
@login_required
def sensorView(sensor_id):
    sensor = Sensor.query.filter_by(public_id=sensor_id, user_id=current_user.id).first_or_404()
    room_id = sensor.room.public_id
    return render_template("view-templates/sensorView.html", user=current_user, room_id=room_id, sensor=sensor)



