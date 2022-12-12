from flask import request, jsonify, make_response, g, _request_ctx_stack
from app.models import User
from app.utils.security.decorators import access_token_required
from app import db
from app.utils.constants.http_codes import *
from app.utils.security.tools import roles_required
from app.models import Sensor, DayAnalytics, Device, Log
import os
import signal
import datetime
from flask import Blueprint
from app.utils.analytics import tracking



api_admin = Blueprint('api_admin', __name__)


@api_admin.before_request
def callback():
    tracking(view=False)



@api_admin.route("/dashboard/get-data/today", methods=["GET"])
@access_token_required()
def dashboardToday(current_user):
    roles_required(current_user, or_roles=["Admin", "Admin-Editor", "Admin-Analyse-Only"])
    stats_today = DayAnalytics.query.order_by(DayAnalytics.date.desc()).limit(1).first_or_404()
    user_count = User.query.count()
    sensor_count = Sensor.query.count()

    stats_today_json = stats_today.to_json()
    stats_today_json["total_sensors"] = sensor_count
    stats_today_json["total_users"] = user_count

    return make_response(jsonify({"message": "Success!", "payload": stats_today_json}), HTTP_200_OK)


@api_admin.route("/dashboard/chart-data", methods=["GET"])
@access_token_required()
def getAdminChartData(current_user):
    roles_required(current_user, or_roles=["Admin", "Admin-Editor", "Admin-Analyse-Only"])

    try:
        amount = request.args["amount"]
    except KeyError:
        return jsonify({"message": "error", "text": "Wrong Format"})

    stats = DayAnalytics.query.order_by(DayAnalytics.date.desc()).limit(int(amount)).all()

    payload = {"data": {"view-calls": [], "api-calls": [], "auth-api-calls": [], "auth-view-calls": []},
               "timestamps": [], "colors": {}}

    for dataset in reversed(stats):
        payload["timestamps"].append(dataset.date)
        payload["data"]["view-calls"].append(dataset.view_calls)
        payload["data"]["api-calls"].append(dataset.api_calls)
        payload["data"]["auth-api-calls"].append(dataset.authorized_api_calls)
        payload["data"]["auth-view-calls"].append(dataset.authorized_view_calls)

    payload["colors"]["view-calls"] = "rgb(143,22,50)"
    payload["colors"]["api-calls"] = "rgb(255,51,51)"
    payload["colors"]["auth-api-calls"] = "rgb(51,153,255)"
    payload["colors"]["auth-view-calls"] = "rgb(51,255,120)"

    return make_response(jsonify({"message": "Success!", "payload": payload}), HTTP_200_OK)


@api_admin.route("/emergency/shutdown", methods=["POST"])
@access_token_required()
def shutdown(current_user):
    roles_required(current_user, role="Admin")
    now = datetime.datetime.utcnow()
    speed = (now - g.start_time).total_seconds()
    client_ip = request.environ['REMOTE_ADDR']
    ip_query = Device.query.filter_by(ip=client_ip).first()
    ctx = _request_ctx_stack.top

    new_log = Log(
        url=ctx.request.url,
        method=ctx.request.method,
        blueprint=ctx.request.blueprint,
        user_agent={
            "browser": ctx.request.user_agent.browser,
            "platform": ctx.request.user_agent.platform,
            "version": ctx.request.user_agent.version,
            "string": ctx.request.user_agent.string
        },
        url_args=ctx.request.args,
        status="201 CREATED",
        timestamp=now.isoformat(),
        speed=speed,
        device=ip_query.id,
        xforwardedfor=ctx.request.headers.get('X-Forwarded-For', None),
        path=ctx.request.path,
        user=g.user_id if g.user_id else "not authenticated"
    )

    db.session.add(new_log)
    db.session.commit()
    os.kill(os.getpid(), signal.SIGINT)
    print("Server is shutting down...")
    return jsonify({"message": "Success!", "text": "Server is shutting down..."})


"""
@webapi_admin.route("admin/reset/", methods=["POST"])
@roles_required_decorator(role="Admin")
def resetParam(config_param):

    current_app[config_param] = 
"""