from .. import db
from .user import User
from .device import Device

class Log(db.Model):

    __tablename__ = "log"

    id : int = db.Column(db.Integer, primary_key=True)
    url : str = db.Column(db.String(100))
    method : str = db.Column(db.String(10))
    user_agent : dict = db.Column(db.JSON)
    blueprint : str = db.Column(db.String(10))
    url_args : dict = db.Column(db.JSON)
    status : str = db.Column(db.String(10))
    speed : str = db.Column(db.Float) # in seconds
    path : str = db.Column(db.String(10))
    timestamp : str = db.Column(db.String(20))
    xforwardedfor : str = db.Column(db.String(20))

    device : str = db.Column(db.String(20), db.ForeignKey("device.id"))
    user : int  = db.Column(db.Integer, db.ForeignKey("user.id"))

    def to_json(self):
        return dict(url=self.url, user_agent=self.user_agent, blueprint=self.blueprint,
                    url_args=self.url_args, status=self.status, speed=self.speed, 
                    path=self.path, timestamp=self.timestamp, xforwardedfor=self.xforwardedfor,
                    device=Device.query.filter_by(id=self.device).with_entities(Device.ip).first()[0], user=User.query.filter_by(id=self.user).with_entities(User.email).first()[0]
                )