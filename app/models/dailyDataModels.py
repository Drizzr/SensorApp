from .. import db

class DayAnalytics(db.Model):

    __tablename__ = "day_analytics"

    date : str = db.Column(db.String(10), primary_key=True)
    authorized_view_calls : int = db.Column(db.Integer)
    view_calls : int  = db.Column(db.Integer)
    new_access_token : int = db.Column(db.Integer)
    new_refresh_token : int = db.Column(db.Integer)
    unique_users : int = db.Column(db.Integer)
    authorized_api_calls : int = db.Column(db.Integer)
    api_calls : int = db.Column(db.Integer)
    new_registered_users : int = db.Column(db.Integer)
    
    device_calls : list = db.relationship('DeviceDayCalls', backref="dateInfo", lazy="select")
    user_calls : list = db.relationship('UserDayCalls', backref="dateInfo", lazy="select")

    def to_json(self):
        return dict(date=self.date, authorized_view_calls=self.authorized_view_calls, 
                    view_calls=self.view_calls, authorized_api_calls=self.authorized_api_calls, 
                    api_calls=self.api_calls, unique_users=self.unique_users, new_registered_users=self.new_registered_users)


class DeviceDayCalls(db.Model):
    id : int = db.Column(db.Integer, primary_key=True)
    date : str = db.Column(db.String(10), db.ForeignKey("day_analytics.date"))
    device_ip : str = db.Column(db.String(20), db.ForeignKey("device.id", ondelete='CASCADE'))
    view_calls : int = db.Column(db.Integer)
    api_calls : int =  db.Column(db.Integer)

    def __repr__(self):
        return f'<View-Calls: {self.view_calls}, API-Calls: {self.api_calls}>'
    
    def to_json(self):
        return dict(date=self.date, device=self.device_ip, 
                    view_calls=self.view_calls, 
                    api_calls=self.api_calls)


class UserDayCalls(db.Model):
    id : int = db.Column(db.Integer, primary_key=True)
    date : str = db.Column(db.String(10), db.ForeignKey("day_analytics.date"))
    user_id : int = db.Column(db.Integer, db.ForeignKey("user.id", ondelete='CASCADE'))
    view_calls : int = db.Column(db.Integer)
    api_calls : int =  db.Column(db.Integer)

    def __repr__(self):
        return f'<View-Calls: {self.view_calls}, API-Calls: {self.api_calls}>'
    
    def to_json(self):
        return dict(date=self.date, device=self.user_id, 
                    view_calls=self.view_calls, 
                    api_calls=self.api_calls)
