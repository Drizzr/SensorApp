from flask import request, jsonify, make_response, current_app, g, flash, _request_ctx_stack, abort
from flask_login import login_required, current_user, logout_user
from app.models import User, ExpiredToken
from werkzeug.security import check_password_hash
from app.utils.security.decorators import access_token_required
from app.utils.security.tools import loginApiCall
from app import db
from app.utils.constants.http_codes import *
from app.utils.security.tools import createJwtToken, roles_required
from app.models import Sensor, SensorDataSet, DataPoint, DayAnalytics, Device, Room, Log
import jwt
import os
import signal
import datetime
from flask import Blueprint
from app.utils.analytics import trackUserApiCalls, tracking


api_auth = Blueprint('api_auth', __name__)

@api_auth.before_request
def callback():
    tracking(view=False)


@api_auth.route("/api-connect/web", methods=["POST"])
def api_connect():
    if current_user.is_authenticated:
        accessToken = request.cookies.get("x-access-token")
        refreshToken = request.cookies.get("x-refresh-token")
        accessExpirationTime = None
        refreshExpirationTime = None

        if accessToken and refreshToken:
            try:
                accessData = jwt.decode(algorithms=["HS256"], jwt=accessToken, key=current_app.config["SECRET_KEY"],
                                        options={"verify_exp": True})
                if accessData["scope"] == "api-token":
                    token_query = ExpiredToken.query.filter_by(token=accessToken, type="refresh", ).first()

                    if not token_query:
                        user = User.query.filter_by(public_id=accessData["public_id"]).first()
                        accessExpirationTime = accessData["exp"]
                        if user and current_user.id == user.id:
                            trackUserApiCalls(current_user, False)
                        else:
                            raise jwt.InvalidTokenError
                else:
                    raise jwt.InvalidTokenError

            except jwt.InvalidTokenError as e:
                print(e)
                try:
                    refreshData = jwt.decode(algorithms=["HS256"], jwt=refreshToken, key=current_app.config["SECRET_KEY"],
                                            options={"verify_exp": True})
                    if refreshData["scope"] == "api-token":
                        token_query = ExpiredToken.query.filter_by(token=refreshToken, type="refresh", ).first()

                        if not token_query:
                            user = User.query.filter_by(public_id=refreshData["public_id"]).first()
                            refreshExpirationTime = refreshData["exp"]
                            if user and current_user.id == user.id:
                                new_expired_refresh_token = ExpiredToken(token=refreshToken,
                                                                        type="refresh",
                                                                        expiration_date=refreshExpirationTime,
                                                                        user_id=current_user.id)

                                db.session.add(new_expired_refresh_token)
                                accessToken, accessExpirationTime = createJwtToken(current_app.config["SECRET_KEY"],
                                                                                user=current_user, access_token=True)
                                refreshToken, refreshExpirationTime = createJwtToken(current_app.config["SECRET_KEY"],
                                                                                    user=current_user, refresh_token=True)
                                trackUserApiCalls(current_user, True)
                            else:
                                raise jwt.InvalidTokenError
                    else:
                        raise jwt.ExpiredSignatureError

                except (jwt.DecodeError, jwt.ExpiredSignatureError, jwt.InvalidTokenError, jwt.InvalidAlgorithmError) as e:
                    accessToken, accessExpirationTime = createJwtToken(current_app.config["SECRET_KEY"], user=current_user, access_token=True)
                    refreshToken, refreshExpirationTime = createJwtToken(current_app.config["SECRET_KEY"],
                                                                        user=current_user, refresh_token=True)
                    trackUserApiCalls(current_user, new_access_token=True, new_refresh_token=True)
                    g.user_id = current_user.id
                    db.session.commit()

        if not accessToken:
            accessToken, accessExpirationTime = createJwtToken(current_app.config["SECRET_KEY"], user=current_user, access_token=True)
            trackUserApiCalls(current_user, new_access_token=True)
        if not refreshToken:
            refreshToken, refreshExpirationTime = createJwtToken(current_app.config["SECRET_KEY"], user=current_user,
                                                                refresh_token=True)
            trackUserApiCalls(current_user, new_access_token=True)

        g.user_id = current_user.id
        db.session.commit()
        response = make_response(
            jsonify({"message": "success", "payload": {"x-access-token": accessToken, "x-refresh-token": refreshToken}}),
            HTTP_200_OK)
        response.set_cookie("x-access-token", accessToken, httponly=True, expires=accessExpirationTime)
        response.set_cookie("x-refresh-token", refreshToken, httponly=True, expires=refreshExpirationTime)
        return response
    abort(401)


@api_auth.route("/mobile/login", methods=["POST"])
def login_mobile():
    """
    This function implements login via api class f.E. for mobile devices using a future app.
    If all the credentials are valid the user server creates an access-token and a refresh-token
    with the help of the 'loginApiCall()' method
    """
    try:
        data = request.get_json()
        password = data["password"]
        email = data["email"]

        user = User.query.filter_by(email=email).first()

        if user:
            if check_password_hash(user.password, password):
                return make_response(loginApiCall(user))

            else:
                return make_response(jsonify({"message": "Wrong Password!"}), HTTP_406_NOT_ACCEPTABLE)

        else:
            return make_response(jsonify({"message": "Email does not exist!"}), HTTP_406_NOT_ACCEPTABLE)

    except KeyError as e:
        print(e)
        return make_response(jsonify({"message": "Wrong format!"}), HTTP_406_NOT_ACCEPTABLE)



@api_auth.route("/api/logout", methods=["POST"])
@access_token_required()
def api_logout():
    """
    This function implements user logout with the help of the accessTokenRequired decorator
    """

    return make_response(jsonify({"message": "logged out successfully!"}), HTTP_200_OK)



@api_auth.route("/web/logout", methods=["POST"])
@access_token_required(logout=True)
# @login_required
def web_logout():
    logout_user()
    flash(f'logged out!', category='success')
    response = make_response(jsonify({"message": "Success!"}), HTTP_200_OK)
    response.delete_cookie("x-access-token")
    response.delete_cookie("x-refresh-token")

    return response