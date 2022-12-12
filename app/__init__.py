from app.utils.constants.http_codes import HTTP_403_FORBIDDEN
from .error_handlers import (methodNotAllowed,
                             pageNotFound,
                             csrfError,
                             internalServerError,
                             tooManyRequests,
                             unauthorizedUser)

from .utils.tools import referrerRequest

from app.utils.constants.http_codes import (HTTP_405_METHOD_NOT_ALLOWED,
                                            HTTP_404_NOT_FOUND,
                                            HTTP_401_UNAUTHORIZED,
                                            HTTP_500_INTERNAL_SERVER_ERROR)

from .admin import (DeviceView,
                    MyAdminIndexView,
                    UserView,
                    SensorView,
                    AnalyticsView,
                    UserDayCallView,
                    DeviceDayCallView,
                    ExpiredTokenView,
                    ModelView,
                    LogView,
                    RoomView,
                    RoleView
                    )

from flask import Flask, request, url_for, redirect, flash, g, _request_ctx_stack
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_login import LoginManager, current_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_migrate import Migrate
from flask_mail import Mail
import datetime
from werkzeug.utils import import_string
from os import path
from redis import Redis
import rq

db = SQLAlchemy()  # lazy initializing required flask-packages
csrf = CSRFProtect()
migrate = Migrate()
mail = Mail()

"""
config variables are stored as an object 
to make them accessable from out of context such as in
the authentication.py file
"""

config = import_string("app.config.DevelopmentConfig")


def create_app(developing=True):
    app = Flask(__name__)

    app.config.from_object(config)  # all flask config variables are stored in the config object

    csrf.init_app(app)
    db.init_app(app)
    mail.init_app(app)
    
    app.redis = Redis.from_url(app.config["REDIS_URL"])
    app.task_queue = rq.Queue('urbanwaters-tasks', connection=app.redis)

    from app.routes.views.views import views
    app.register_blueprint(views, url_prefix="/")

    from app.routes.views.auth import view_auth
    app.register_blueprint(view_auth, url_prefix="/auth")

    from app.routes.api.api import api_routes
    app.register_blueprint(api_routes, url_prefix="/api")

    from app.routes.api.auth import api_auth
    app.register_blueprint(api_auth, url_prefix="/api/auth")

    from app.routes.api.admin import api_admin
    app.register_blueprint(api_admin, url_prefix="/api/admin")


    app.register_error_handler(HTTP_404_NOT_FOUND, pageNotFound)
    app.register_error_handler(HTTP_401_UNAUTHORIZED, unauthorizedUser)
    app.register_error_handler(CSRFError, csrfError)
    app.register_error_handler(HTTP_500_INTERNAL_SERVER_ERROR, internalServerError)
    app.register_error_handler(HTTP_405_METHOD_NOT_ALLOWED, methodNotAllowed)
    app.register_error_handler(HTTP_403_FORBIDDEN, tooManyRequests)

    # makes the function referrerRequest globally accessable in all HTML5-files
    app.jinja_env.globals.update(referrerRequest=referrerRequest)

    from .models import (User,
                         Sensor,
                         SensorDataSet,
                         DayAnalytics,
                         Device,
                         Room,
                         DeviceDayCalls,
                         UserDayCalls,
                         ExpiredToken,
                         DataPoint,
                         Log,
                         Role)

    login_manager = LoginManager()
    login_manager.login_view = 'views.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        """
        callback function, necessary for the flask_login-manager, handling user authorisation for the browser
        """
        return User.query.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized_handler():
        flash("You have to be logged in to access this page.", category="error")
        # instead of using request.path to prevent Open Redirect Vulnerability
        next_url = url_for(request.endpoint, **request.view_args)
        return redirect(url_for('views.login', next=next_url))

    create_database(app)

    # the admin dashboard gets initialized
    admin = Admin(app, index_view=MyAdminIndexView(), template_mode="bootstrap4")
    admin.add_view(UserView(User, db.session, category="DB-Models"))  # register db-models for the admin-dashboard-view
    admin.add_view(SensorView(Sensor, db.session, category="DB-Models"))
    admin.add_view(AnalyticsView(DayAnalytics, db.session, category="DB-Models"))
    admin.add_view(DeviceView(Device, db.session, category="DB-Models"))
    admin.add_view(RoomView(Room, db.session, category="DB-Models"))
    admin.add_view(UserDayCallView(UserDayCalls, db.session, category="DB-Models"))
    admin.add_view(DeviceDayCallView(DeviceDayCalls, db.session, category="DB-Models"))
    admin.add_view(ExpiredTokenView(ExpiredToken, db.session, category="DB-Models"))
    admin.add_view(ModelView(SensorDataSet, db.session, category="DB-Models"))
    admin.add_view(ModelView(DataPoint, db.session, category="DB-Models"))
    admin.add_view(LogView(Log, db.session, category="DB-Models"))
    admin.add_view(RoleView(Role, db.session, category="DB-Models"))

    migrate.init_app(app=app, db=db)

    @app.before_request
    def request_callback():
        g.start_time = datetime.datetime.utcnow()
        g.user_id = current_user.id if current_user.is_authenticated else None
    
    @app.after_request
    def logging_callback(response):
        now = datetime.datetime.utcnow()

        """
        necessary because before request call doesnt seem to activated when calling forms via post directly
        """
        try:
            speed = (now - g.start_time).total_seconds()
            user = g.user_id if g.user_id else "not authenticated"
        except AttributeError:              
            speed = 0
            user = "not authenticated"

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
                    status=response.status,
                    timestamp=now.isoformat(),
                    speed=speed,
                    device=ip_query.id,
                    xforwardedfor=ctx.request.headers.get('X-Forwarded-For', None),
                    path=ctx.request.path,
                    user=user
                    )   
        
        db.session.add(new_log)
        db.session.commit()
        return response

    return app
    
    
def create_database(app):
    if not path.exists('app/' + app.config["DB_NAME"]):
        db.create_all(app=app)
        print('Created Database!')
