from flask import request, jsonify, make_response, flash
from app.utils.security.decorators import access_token_required
from app import db
from app.utils.constants.http_codes import *
from app.models import Sensor, SensorDataSet, DataPoint, Room
from flask import Blueprint
from app.utils.analytics import tracking

api_routes = Blueprint('api_routes', __name__)


@api_routes.before_request
def callback():
    tracking(view=False)



@api_routes.route("/sensor/<sensor_id>/update", methods=["POST"])
@access_token_required()
def update_sensor_data(current_user, sensor_id):
    """
    This function implements sensor data update 
    """
    sensor = Sensor.query.filter_by(public_id=sensor_id,
                                    user_id=current_user.id).first_or_404()  # the servers queries sensor with the help of the sensor_id

    try:
        new_data = request.get_json()  # the program tries to fetch the new data

        new_data_set = SensorDataSet(time=new_data["timestamp"], sensor_id=sensor.id)  # server creates a new dataset
        db.session.add(new_data_set)
        for key in sensor.value_map:  # creates new data points according to the stored value_map
            new_data_point = DataPoint(sensorData_id=new_data_set.id, description=key, value=new_data["values"][key])
            new_data_set.values.append(new_data_point)  # the datapoints are stored in the new dataset
            db.session.add(new_data_point)

        # when everything was successful the last update variable gets updated
        sensor.last_update = new_data["timestamp"]
        db.session.commit()
    except Exception as e:
        print(e)
        return make_response(
            jsonify({"message": "Wrong Format! Possibly used wrong values!", "http-code": "406"}),
            HTTP_406_NOT_ACCEPTABLE)

    data = {"message": "Sensor-Data updated!"}

    return make_response(jsonify(data), HTTP_201_CREATED)  # the server returns a response with the http-code 201



@api_routes.route("/delete/sensor/<sensor_id>", methods=["DELETE"])
@access_token_required()
def deleteSensor(current_user, sensor_id):
    try:
        sensor = Sensor.query.filter_by(public_id=sensor_id, user_id=current_user.id).first_or_404()
        db.session.delete(sensor)
        db.session.commit()
        flash(f'Sensor: {sensor_id} deleted!', category='success')
        return make_response(jsonify({"message": "Success!"}), HTTP_201_CREATED)
    except Exception as e:
        print(e)
        return make_response(jsonify({"message": "Sensor couldn't get deleted!"}), HTTP_500_INTERNAL_SERVER_ERROR)


@api_routes.route("/delete/room/<room_id>", methods=["DELETE"])
@access_token_required()
def deleteRoom(current_user, room_id):
    try:
        Room.query.filter_by(public_id=room_id, user_id=current_user.id).delete()
        db.session.commit()
        flash(f'Room: {room_id} deleted!', category='success')
        return make_response(jsonify({"message": "Success!"}), HTTP_201_CREATED)
    except Exception:
        return make_response(jsonify({"message": "Sensor couldn't get deleted!"}), HTTP_500_INTERNAL_SERVER_ERROR)


@api_routes.route("sensor/<sensor_id>/get-update", methods=["GET"])
@access_token_required()
def getLastEntry(current_user, sensor_id):
    sensor = Sensor.query.filter_by(public_id=sensor_id, user_id=current_user.id).first_or_404()
    print(1)
    last_sensor_data_set = SensorDataSet.query.order_by(SensorDataSet.id.desc()).filter_by(
        sensor_id=sensor.id).first_or_404()
    sensor_payload = sensor.to_json()

    values = {}

    for datapoint in last_sensor_data_set.values:
        values[datapoint.description + " in " + sensor.value_map[datapoint.description]["unit"]] = datapoint.value

    sensor_payload["data"] = values
    sensor_payload["last_update"] = sensor.last_update

    return make_response(jsonify({"message": "Success!", "payload": sensor_payload}), HTTP_200_OK)


@api_routes.route("sensor/<sensor_id>/get-data", methods=["GET"])
@access_token_required()
def getSensorData(current_user, sensor_id):
    try:
        amount = request.args["amount"]
    except KeyError:
        return jsonify({"message": "error", "text": "Wrong Format"})

    sensor = Sensor.query.filter_by(public_id=sensor_id, user_id=current_user.id).first_or_404()
    sensor_data = SensorDataSet.query.order_by(SensorDataSet.id.desc()).filter_by(sensor_id=sensor.id).limit(
        amount).all()
    timestamps = []
    values = {}

    for key in sensor.value_map:
        values[key] = []

    for dataset in reversed(sensor_data):
        timestamps.append(dataset.time)

        for datapoint in dataset.values:
            values[datapoint.description].append(datapoint.value)

    payload = sensor.to_json()
    payload["timestamps"] = timestamps
    payload["data"] = values
    payload["last_update"] = sensor.last_update

    return make_response(jsonify({"message": "Success!", "payload": payload}), HTTP_200_OK)


@api_routes.route("room/<room_id>/updates", methods=["GET"])
@access_token_required()
def getRoomUpdates(current_user, room_id):
    room = Room.query.filter_by(public_id=room_id, user_id=current_user.id).first_or_404()

    payload = {}

    if room.sensors:
        for sensor in room.sensors:
            payload[sensor.public_id] = {"values": {}}
            payload[sensor.public_id]["last_update"] = sensor.last_update
            dataset = SensorDataSet.query.order_by(SensorDataSet.id.desc()).filter_by(sensor_id=sensor.id).limit(
                1).first()
            if dataset:
                for dataPoint in dataset.values:
                    payload[sensor.public_id]["values"][dataPoint.description] = dataPoint.value
                    payload[sensor.public_id]["value_map"] = sensor.value_map

    return make_response(jsonify({"message": "Success!", "payload": payload}), HTTP_200_OK)


