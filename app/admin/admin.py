from ..utils.tools import referrerRequest
from flask import redirect, url_for, abort, request, flash
from flask_login import current_user
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView, BaseView
from flask_admin.form import SecureForm
from wtforms import PasswordField
from wtforms.validators import InputRequired
from werkzeug.security import generate_password_hash


# form exclude cols for more detailed access protocoll depending on role

class CustomPasswordField(PasswordField): 

    # creates a custom password field for the admin edit page
    # it hashes the input via the sh256 algorythm

    def populate_obj(self, obj, name):
        setattr(obj, name, generate_password_hash(self.data, "sha256", 10)) 

            
class ModelView(ModelView):
    column_display_pk = True
    column_hide_backrefs = False
    can_export = True
    can_view_details = True
    details_modal = True
    edit_modal = True
    create_modal = True
    export_types = ["csv"]
    can_set_page_size = True

    access_roles = ["Admin", "Admin-Editor", "Admin-Analyse-Only"]
    roles_can_edit = ["Admin"]
    roles_can_create = ["Admin"]
    roles_can_delete = ["Admin"]
    
    def is_accessible(self):
        access = False
        self.can_delete = False
        self.can_create = False
        self.can_edit = False

        if current_user.is_authenticated:
            for role in current_user.roles:
                
                if role.name in self.roles_can_edit:
                    self.can_edit = True 
                if role.name in self.roles_can_create:
                    self.can_create = True
                if role.name in self.roles_can_delete:
                    self.can_delete = True
                if role.name in self.access_roles:
                    access = True
                
        return access

    def inaccessible_callback(self, name, **kwargs):

        # if a user is unauthorized to access the db-models he gets redirected via the referrerRequest() function
        next_url = url_for(request.endpoint,**request.view_args)
        return redirect(url_for('views.home', next=next_url))

    
class MyAdminIndexView(AdminIndexView):
    
    access_roles = ["Admin", "Admin-Editor", "Admin-Analyse-Only"]
    
    def is_accessible(self):
        access = False
        if current_user.is_authenticated:
            for role in current_user.roles:
                if role.name in self.access_roles:
                    access = True
        return access

    def inaccessible_callback(self, name, **kwargs):

        # if a user is unauthorized to access the db-models he gets redirected via the referrerRequest() function
        next_url = url_for(request.endpoint,**request.view_args)
        if current_user.is_authenticated:
            abort(401)
        return redirect(url_for('views.home', next=next_url))
    
    
class UserView(ModelView):
    #inline_models = ['post', ]

    column_list = ["public_id", "email", "roles", "devices", "sensors", "rooms", "name", "expired_token", "password"]
    form_columns = ["email", "devices", "rooms", "sensors", "name", "expired_token", "disabled", "roles"]
    column_filters = ["devices", "rooms", "calls_per_date"]
    column_searchable_list = ['public_id', 'email']
    roles_can_edit = ["Admin", "Admin-Editor"]
    column_editable_list = ["email", "name"]
    
    form_extra_fields = {
        'password': CustomPasswordField('Password'),
    }

    
class DeviceDayCallView(ModelView):
    
    # access configuration
    roles_can_delete = ["Admin"]
    roles_can_edit = ["Admin"]
    roles_can_create = ["Admin"]
    access_roles = ["Admin", "Admin-Editor"]
    
    # options for model visualisation
    column_list = ["dateInfo", "api_calls", "view_calls", "device"]
    column_filters = ["device"]


class UserDayCallView(ModelView):
    
    # access configuration
    roles_can_delete = ["Admin"]
    roles_can_edit = ["Admin"]
    roles_can_create = ["Admin"]
    access_roles = ["Admin", "Admin-Editor"]
    
    # options for model visualisation
    column_list = ["dateInfo", "api_calls", "view_calls", "user"]
    column_filters = ["user"]


class SensorView(ModelView):
    roles_can_delete = ["Admin", "Admin-Editor"]
    roles_can_edit = ["Admin", "Admin-Editor"]
    roles_can_create = ["Admin", "Admin-Editor"]
    
    column_searchable_list = ['public_id']
    column_editable_list = ["name", "owner", "room"]


class AnalyticsView(ModelView):
    column_searchable_list = ['date']
    column_filters = ["view_calls", "api_calls"]


class ExpiredTokenView(ModelView):
    # changes role-accessability -> only Admins and Admin-Editors are allowed to access the page
    access_roles = ["Admin", "Admin-Editor"]
    
    column_list = ['user', "expiration_date", "type"]
    column_searchable_list = ['user_id']
    column_filters = ["user", "type"]


class DeviceView(ModelView):
    
    column_list = ["ip", "country", "city", "calls_all_time", "users", "flagged"]
    column_searchable_list = ['ip']
    column_filters = ["country", "city", "region", "flagged", "users", "calls_per_date"]


class LogView(ModelView):
    # ensures that nobody can create or delete logs by hand
    roles_can_create = [] 
    roles_can_delete = []
    
    # only the admin has access to the log entries
    access_roles = ["Admin"]
    
    column_list = ["timestamp", "method", "blueprint", "url", "status", "speed", "user", "device"]
    column_searchable_list = ['device', "user", "url"]
    
    
class RoleView(ModelView):
    # only the admin can edit log entries
    roles_can_edit = ["Admin"]
    
    # ensures that only the admin can create or delete roles by hand
    roles_can_create = ["Admin"] 
    roles_can_delete = ["Admin"]
    
    # only the admin has access to the log entries
    access_roles = ["Admin"]
    

    column_searchable_list = ['name']


class RoomView(ModelView):
    roles_can_delete = ["Admin", "Admin-Editor"]
    roles_can_edit = ["Admin", "Admin-Editor"]
    roles_can_create = ["Admin", "Admin-Editor"]
    column_editable_list = ["name", "description", "owner"]




