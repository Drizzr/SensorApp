from datetime import datetime, timedelta
from lib2to3.pgen2 import token
from secrets import token_hex
from flask import abort, jsonify, make_response, render_template, request, flash, redirect, current_app, url_for
from flask_login import login_user, current_user, login_required
from app.models import User, Device, DayAnalytics
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models.user import ExpiredToken
from app.utils.constants.http_codes.http_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_404_NOT_FOUND
from app.utils.security.decorators import logoutRequired, verifiedRequired, notVerifiedRequired
from app.utils.security.tools import createJwtToken
from app.utils.tools import referrerRequest
from app.utils.forms import LoginForm, SignUpForm
from app.utils.analytics import tracking
from flask import Blueprint
from app.task import launch_task
import jwt


view_auth = Blueprint('view_auth', __name__)

@view_auth.before_request
def request_callback():
    
    tracking(view=True)


@view_auth.route('/login', methods=['GET', 'POST'])
@logoutRequired
def login():
    """
    implements the login logic for the login-form
    """

    form = LoginForm(request.form)  # a login-Form instance gets created
    if form.validate_on_submit():
        try:
            # function fetches the data when the form has been validated
            email = form.email.data
            password = form.password.data
            next_url = request.form.get("next")
            remember_me = form.remember_me.data

            user = User.query.filter_by(email=email).first()  # the servers queries

            if user:
                if check_password_hash(user.password, password):
                    client_ip = request.environ['REMOTE_ADDR']
                    ip_query = Device.query.filter_by(ip=client_ip).first()
                    login_user(user, remember=True) if remember_me else login_user(user, remember=False)
                    if user not in ip_query.users:
                        ip_query.users.append(user)
                        db.session.commit()
                    if user.verified:
                        flash('Logged in successfully!', category='success')
                        current_app.task_queue.enqueue("app.task.send_email",  "send_email", 
                                    "sending login information", 
                                    "new_login", sender="noreply@urbanwaters.com",
                                    recipients = [user.email],
                                    text_body=render_template("email/login_information/login_information.txt", user=user, device=ip_query),
                                    html_body=render_template("email/login_information/login_information.html", user=user, device=ip_query),
                                    )
                        return redirect(next_url)
                    else:
                        
                        verify_token = createJwtToken(current_app.config["SECRET_KEY"], user, verify_token=True)[0]

                        print(verify_token)
                        launch_task(current_app, "send_email", 
                            "sending verification link", 
                            "verify-sccount", sender="noreply@urbanwaters.com",
                            recipients = [user.email],
                            text_body=render_template("email/verfiy_account/verify_account.txt", user=user, verify_token=verify_token),
                            html_body=render_template("email/verfiy_account/verify_account.html", user=user, verify_token=verify_token),

                                )
                        response = make_response(redirect(url_for("view_auth.not_verified")))
                        return response
                else:
                    # returns error-message hiding the distinct cause of error
                    flash('The combination of email and password does not exist!', category='error')

            else:
                # returns error-message hiding the distinct cause of error
                flash('The combination of email and password does not exist!', category='error')

            return redirect(f"/login?next={next_url}")

        except Exception as e:
            print(e)
            abort(404)

    return render_template("auth/login.html", user=current_user, form=form)



@view_auth.route("/sign-up", methods=["GET", "POST"])
@logoutRequired
def signUp():
    form = SignUpForm(request.form)
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        username = form.name.data
        next_url = request.form.get("next")

        user = User.query.filter_by(email=email).first()

        if user:
            flash('This e-mail already exists.', category='error')
        else:
            public_id = token_hex(16)
            client_ip = request.environ['REMOTE_ADDR']
            ip_query = Device.query.filter_by(ip=client_ip).first()
            day_query = DayAnalytics.query.filter_by(date=ip_query.last_call[:10]).first()
            new_user = User(public_id=public_id,
                            email=email,
                            name=username,
                            password=generate_password_hash(password, 'sha256', 10),
                            disabled=False,
                            #locale=request.accept_languages.best_match(current_app.config['LANGUAGES']),
                            )
            new_user.set_admin_role()
            new_user.set_role("User")

            ip_query.users.append(new_user)
            day_query.new_registered_users += 1
            db.session.add(new_user)
            db.session.commit()

            login_user(new_user, remember=True)

            verify_token = createJwtToken(current_app.config["SECRET_KEY"], new_user, verify_token=True)[0]
            print(verify_token)

            launch_task(current_app, "send_email", 
                        "sending verification link", 
                        "verify account", sender="noreply@urbanwaters.com",
                        recipients = [new_user.email],
                        text_body=render_template("email/verfiy_account/verify_account.txt", user=user, verify_token=verify_token),
                        html_body=render_template("email/verfiy_account/verify_account.html", user=user, verify_token=verify_token),
                                    )
            
            return redirect(url_for("views.auth.not_verified"))
        return redirect(f"/sign-up?next={next_url}")
    return render_template("auth/signUp.html", user=current_user, form=form)


@view_auth.route('/not-verified/', methods=["GET"])
@notVerifiedRequired
def not_verified():
    return render_template("auth/verify_account/not-verified.html", user=current_user)


@view_auth.route('/verify-account/', methods=["GET"])
def verify_account():
    try:

        verify_token = request.args.get("verify_token")
        verify_data = jwt.decode(algorithms=["HS256"], jwt=verify_token, key=current_app.config["SECRET_KEY"],
                                    options={"verify_exp": True})
        
        token_query = ExpiredToken.query.filter_by(token=verify_token).first()

        if not token_query:
            if verify_data["scope"] == "verify-token":
                user = User.query.filter_by(public_id=verify_data["public_id"]).first_or_404()

                if not user.verified:
                    user.verified = True

                    new_expired_token = ExpiredToken(
                                user_id=user.id,
                                token=verify_token,
                                expiration_date=verify_data["exp"], # stored in utc-float timestamp
                                type="verify-token"
                    )

                    db.session.add(new_expired_token)

                    flash("your account has been verified!")
                    return redirect(url_for("views.home"))
                else:
                    abort(HTTP_404_NOT_FOUND)
            else:
                abort(HTTP_404_NOT_FOUND)
        else:
            abort(HTTP_401_UNAUTHORIZED)
    
    except jwt.ExpiredSignatureError as e:
        return render_template("auth/verify_account/verified-error.html", user=current_user)

    except KeyError as e:
        print(e)
        abort(HTTP_404_NOT_FOUND)


@view_auth.route('/verify-status', methods=["GET"])
@login_required
def check_verify_status():
    if current_user.verified:
        flash("your account has been verified!")
    return make_response(jsonify({"message": "success", "verified": current_user.verified}), HTTP_200_OK)


@view_auth.route('/verify/new-link', methods=["POST"])
@notVerifiedRequired
def request_new_verify_link():
    verify_token = createJwtToken(current_app.config["SECRET_KEY"], current_user, verify_token=True)[0]

    launch_task(current_app, "send_email", 
                    "sending verification link", 
                    "verify account", sender="noreply@urbanwaters.com",
                    recipients = [current_user.email],
                    text_body=render_template("email/verfiy_account/verify_account.txt", user=current_user, verify_token=verify_token),
                    html_body=render_template("email/verfiy_account/verify_account.html", user=current_user, verify_token=verify_token),

                                        )

    print(verify_token)
    return make_response(jsonify({"message": "success", "verifed": "new link send to user-email"}), HTTP_201_CREATED)
            
