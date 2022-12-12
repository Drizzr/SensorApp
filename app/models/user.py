from email.policy import default
from .. import db
from .user_device_link import deviceUserLink
from .user_role_link import userRoleLink
from .role import Role
from .task import Task
from flask_login import UserMixin
from flask import current_app
from .. import config

class User(db.Model, UserMixin):
    
    __tablename__ = "user"
    
    # user properties
    id : int = db.Column(db.Integer, primary_key=True)
    public_id : str = db.Column(db.String(50), unique=True) # this id is used for all tokens etc. therefore possible introudor has no clue over the actual amount of users in the database
    name : str = db.Column(db.String(24))
    email : str = db.Column(db.String(24), unique=True)
    password : str = db.Column(db.String(150)) # only stored in a sha256 hash-string
    disabled : bool = db.Column(db.Boolean) 
    api_calls_alltime : int = db.Column(db.Integer) # tracking api-calls for a future monetiz
    locale : str = db.Column(db.String(10))

    verified : bool = db.Column(db.Boolean, default=False) 

    # relationship many to many (see ipUserLink-Table)
    devices : list = db.relationship("Device", secondary=deviceUserLink, backref="users", lazy="select")

    # 1 to many relationship
    rooms : list = db.relationship('Room', backref="owner", lazy="select", cascade="all,delete") # enbales cascade deletion of child elements when session.delete(user) is used
    sensors : list = db.relationship('Sensor', backref="owner", lazy="select", cascade="all,delete")

    calls_per_date : list = db.relationship('UserDayCalls', backref="user", lazy="select", cascade="all,delete")

    expired_token : list = db.relationship("ExpiredToken", backref="user", lazy="select", cascade="all,delete")
    loggs : list = db.relationship('Log', lazy="select")

    roles = db.relationship('Role', secondary=userRoleLink)

    tasks = db.relationship('Task', backref='user', lazy='dynamic')


    def set_admin_role(self):
        if self.email in config.ADMINS:
            self.roles.append(Role.query.filter_by(name="Admin").first())
    
    def set_role(self, role):
        self.roles.append(Role.query.filter_by(name=role).first())

    def __repr__(self):
        return f'<User {self.email}>'
    
    def to_json(self):
        return dict(id=self.public_id, name=self.name, email=self.email, is_admin=self.admin)


class ExpiredToken(db.Model):

    __name__ = "expired_token"

    id : int = db.Column(db.Integer, primary_key=True)
    user_id : int = db.Column(db.Integer, db.ForeignKey("user.id", ondelete='CASCADE')) 
    token : str = db.Column(db.String(250))
    expiration_date : float = db.Column(db.Float) # stored in utc-float timestamp
    type : str = db.Column(db.String(15))

    def to_json(self):
        return dict(user=self.user_id, type=self.type, token=self.token, exp=self.expiration_date)




