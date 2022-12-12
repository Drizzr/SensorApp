from flask import jsonify, render_template, make_response, request
from flask_login import current_user
from app.utils.constants.http_codes.http_codes import (HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND,
                                                       HTTP_401_UNAUTHORIZED,
                                                       HTTP_500_INTERNAL_SERVER_ERROR,
                                                       HTTP_405_METHOD_NOT_ALLOWED)

def checkForViews():
    if  not request.path.startswith('/web/'):
        return True
    else:
        return False

def pageNotFound(e):
    resp = make_response(render_template("error-templates/404.html", user=current_user), HTTP_404_NOT_FOUND) if checkForViews() else make_response(jsonify({"message": "page not found"}), HTTP_404_NOT_FOUND)
    return resp

def csrfError(e):
    resp = make_response(render_template("error-templates/csrf.html", user=current_user), HTTP_401_UNAUTHORIZED) if checkForViews() else make_response(jsonify({"message": "CSRF-Token missing"}), HTTP_401_UNAUTHORIZED)
    return resp

def tooManyRequests(e):
    resp = make_response(render_template("error-templates/403.html", user=current_user), HTTP_403_FORBIDDEN) if checkForViews() else make_response(jsonify({"message": "This ip has been permanently banned by the admin! Please contact the support!"}), HTTP_403_FORBIDDEN)
    return resp

def methodNotAllowed(e):
    resp = make_response(render_template("error-templates/405.html", user=current_user), HTTP_405_METHOD_NOT_ALLOWED) if checkForViews() else make_response(jsonify({"message": "method not allowed"}), HTTP_405_METHOD_NOT_ALLOWED)
    return resp   

def internalServerError(e):
    resp = make_response(render_template("error-templates/500.html", user=current_user), HTTP_500_INTERNAL_SERVER_ERROR) if checkForViews() else make_response(jsonify({"message": "An errror occured we are working on it!"}), HTTP_500_INTERNAL_SERVER_ERROR)
    return resp

def unauthorizedUser(e):
    resp = make_response(render_template("error-templates/401.html", user=current_user), HTTP_401_UNAUTHORIZED) if checkForViews() else make_response(jsonify({"message": "unauthorized to access this page"}), HTTP_401_UNAUTHORIZED)
    return resp