from flask import redirect, make_response, g, request, jsonify
from flask_login import current_user
from app.models import User, ExpiredToken
from app.utils.constants.http_codes import *
from app.utils.tools import referrerRequest
from app import db, config
from functools import wraps
import jwt
from ..tools import createJwtToken
from app.utils.analytics import trackUserApiCalls


class access_token_required(object):

    def __init__(self, logout: bool = False):
        self.logout = logout

    def __call__(self, function):
        @wraps(function)
        def decorator(*args, **kwargs):
            key = config.SECRET_KEY  # SECRET KEY used for encrypting is stored in the config-object
            accessToken = None
            refreshToken = None


            try:
                # trying to load access and refresh tokens out of the request's http-header
                
                accessToken = request.headers["x-access-token"]
                refreshToken = request.headers["x-refresh-token"]

            except KeyError as e:
                # on of the two tokens cant be found in the request header
                return make_response(jsonify({"message": "Api-key is missing!", "http-code": "401"}),
                                     HTTP_401_UNAUTHORIZED)

            try:
                # trying to extract the token-data in order to identify the user
                accessData = jwt.decode(algorithms=["HS256"], jwt=accessToken, key=key, options={"verify_exp": True})
                if accessData["scope"] == "api-token":
                    token_query = ExpiredToken.query.filter_by(token=accessToken, type="access",).first()
                    if not token_query:
                        current_user = User.query.filter_by(public_id=accessData["public_id"]).first()
                        expirationTime = accessData["exp"]
                        # if the extraction was successful the server checks whether the token has been labeled expired

                        # the server deletes every token that is stored despite being expired
                        

                        if current_user:
                            # token is valid
                            # user is authorized
                            # this function tracks the amount of tokens created per day and increases the api_calls counter
                            trackUserApiCalls(current_user)
                            g.user_id = current_user.id

                            if self.logout:  # checks whether the current user needs to be logged out

                                # current access-token is stored in the ExpiredToken-Tabel and is therefor invalid

                                new_expired_access_token = ExpiredToken(token=accessToken,
                                                                        type="access",
                                                                        expiration_date=expirationTime,
                                                                        user_id=current_user.id)

                                db.session.add(new_expired_access_token)
                                raise jwt.ExpiredSignatureError  # this exception makes it possible to jump to the refresh-token validation

                            db.session.commit()
                            return function(current_user, *args, **kwargs)  # route function gets called
        
                    
                        else:
                            # user-id can't be found -> user got deleted, entire table got dropped or the SECRET KEY is public
                            print(f"[MAJOR SECURTITY BREECH]: EITHER THE DATABASE HAS BEEN DELETED OR THE API-SECRET-KEY IS PUBLIC")
                            return make_response(
                                jsonify({"message": "This account has recently been deleted!", "http-code": "404"}),
                                HTTP_404_NOT_FOUND)


                    else:
                        raise jwt.ExpiredSignatureError  # access token has been labled as expired -> refresh token has to be checked

                else:
                    return make_response(
                        jsonify({"message": "Woring token-scope!", "http-code": "401"}),
                            HTTP_404_NOT_FOUND)

            except jwt.ExpiredSignatureError:
                # when the access-token is expired the following code gets executed

                try:
                    # the server now tries to decrypt the refresh token

                    refreshData = jwt.decode(algorithms=["HS256"], jwt=refreshToken, key=key,
                                             options={"verify_exp": True})
                    if accessData["scope"] == "api-token":
                        token_query = ExpiredToken.query.filter_by(token=refreshToken, type="refresh").first()

                        if not token_query:
                            # decryption was succesfull, server now checks whether the token has already been used, thus checks for it
                            # in the expired token list stored in the database
                            current_user = User.query.filter_by(public_id=refreshData["public_id"]).first()
                            expirationTime = refreshData["exp"]
                            

                            if current_user:
                                # the token is valid, the user is therefore authorized
                                # the refresh token is now stored in the expired token tabel, since it has been used
                                # this code-snippet therefore implements the refresh-token-rotation
                                # a new access and refresh-token pair is generated and send to the user

                                new_expired_refresh_token = ExpiredToken(token=refreshToken,
                                                                        type="refresh",
                                                                        expiration_date=expirationTime,
                                                                        user_id=current_user.id)

                                db.session.add(new_expired_refresh_token)

                                if not self.logout:  # a new pair of tokens is only created when the current user doesnt need to get logged out
                                    trackUserApiCalls(current_user, new_access_token=True, new_refresh_token=True)
                                    g.user_id = current_user.id
                                    newAccessToken = createJwtToken(key, user=current_user, access_token=True)[0]
                                    newRefreshToken = createJwtToken(key, user=current_user, refresh_token=True)[0]
                                    db.session.commit()
                                    return make_response(jsonify({"message": "Expired, new token pair created", "x-access-token": newAccessToken, "x-refresh-token": newRefreshToken},))
                                else:
                                    # if the user needs to get logged out the loggout view-function gets returned
                                    db.session.commit()
                                    return function(*args, **kwargs)
                                
                            else:
                                #  user-id cant be found -> user got deleted, eintire table got dropped or the SECRET KEY is public
                                print(f"[MAJOR SECURTITY BREECH]: EITHER THE DATABASE HAS BEEN DELETED OR THE API-SECRET-KEY IS PUBLIC")
                                return make_response(
                                    jsonify({"message": "This account has recently been deleted!", "http-code": "404"}),
                                    HTTP_404_NOT_FOUND)

                        else:
                            return make_response(jsonify({"message": "Token is invalid!", "http-code": "401"}),
                                                    HTTP_401_UNAUTHORIZED)
                    
                    else:
                        return make_response(
                        jsonify({"message": "Woring token-scope!", "http-code": "401"}),
                            HTTP_404_NOT_FOUND)

                except (jwt.DecodeError, jwt.InvalidTokenError) as e:
                    # decryption of the refresh token was not successful
                    # the user couldn't authorized
                    print(f"[API-LOGIN-EXCEPTION]: {e}")
                    return make_response(jsonify({"message": "Token is invalid!", "http-code": "401"}),
                                         HTTP_401_UNAUTHORIZED)

            except (jwt.DecodeError, jwt.InvalidTokenError) as e:
                # access-token did not expire, decryption still was not successfull
                # -> signature invalid etc. -> user cannot be authorized
                print(f"[API-LOGIN-EXCEPTION]: {e}")

                return make_response(jsonify({"message": "Token is invalid!", "http-code": "401"}),
                                     HTTP_401_UNAUTHORIZED)

        return decorator



def logoutRequired(function):
    # this decorator is used for the view login and sign-up routes
    # if the user is already logged in and tries to access these pages he gets automatically redirected
    @wraps(function)
    def decorated(*args, **kwargs):
        if current_user.is_authenticated:
            return redirect(referrerRequest())
        else:
            return function(*args, **kwargs)
    return decorated


