from app import config
from app.models import Device, Role
from app.utils.constants.http_codes import HTTP_201_CREATED, HTTP_401_UNAUTHORIZED
from flask import request, jsonify, abort
import jwt
from datetime import datetime, timedelta


def loginApiCall(user):
    # generates access and refresh-token when user has validated is identity (email, password)
    # via the api-login call (for a future mobile app)
    key = config.SECRET_KEY
    ip_query = Device.query.filter_by(ip=request.environ['REMOTE_ADDR']).first()
    ip_query.users.append(user)
    accessToken = createJwtToken(key, user=user, access=True)
    refreshToken = createJwtToken(key, user=user, access=False)
    return jsonify({"message": "Login successful", "x-access-token": accessToken, "x-refresh-token": refreshToken, "http-code": "201"}), HTTP_201_CREATED


def createJwtToken(key, user=None, request_verify_token : bool = False, verify_token : bool = False, access_token: bool = False, refresh_token : bool = False):

    # generates jwt-tokens for the mobile api (updating data send by sensors), expiration varies betwen access and refresh-tokens
    if access_token or refresh_token:
        exp = datetime.utcnow() + timedelta(hours=3) if access_token and not refresh_token else datetime.utcnow() + timedelta(days=30)
        api_key = jwt.encode({"public_id": user.public_id,
                            "exp": exp,
                            "scope": "api-token"}, key)

        return (api_key, exp)
    elif request_verify_token:
        exp = datetime.utcnow() + timedelta(minutes=15) 
        request_verify_token = jwt.encode({"public_id": user.public_id, "exp": exp, "scope": "request-verify-token"}, key)
        return (request_verify_token, exp)
    else:
        exp = datetime.utcnow() + timedelta(minutes=5) 
        verify_token = jwt.encode({"public_id": user.public_id, "exp": exp, "scope": "verify-token"}, key)
        return (verify_token, exp)



def roles_required(user, role : str = None, or_roles: list = None):
    if role and not or_roles:
        role_query = Role.query.filter_by(name=role).first()
        if role_query in user.roles:
            return True
        else:
            abort(HTTP_401_UNAUTHORIZED)
    elif role and or_roles:
        role_query = Role.query.filter_by(name=role).first()
        if role_query in user.roles:
            for or_role in or_roles:
                secondary_role_query = Role.query.filter_by(name=or_role).first()
                if secondary_role_query not in user.roles:
                    abort(HTTP_401_UNAUTHORIZED)
            return True
    elif not role and or_roles:
        for or_role in or_roles:
            role_query = Role.query.filter_by(name=or_role).first()
            if role_query in user.roles:
                return True
        abort(401)