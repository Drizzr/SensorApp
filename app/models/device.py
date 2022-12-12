from .. import db

class Device(db.Model):

    __tablename__ = "device"

    # device properties
    id : int = db.Column(db.Integer, primary_key=True)
    ip : str = db.Column("ip", db.String(50))
    country : str  = db.Column(db.String(20))
    region : str = db.Column(db.String(20))
    city : str = db.Column(db.String(20))
    calls_all_time : int = db.Column(db.Integer)
    last_call : str = db.Column(db.String(50))
    flagged : bool = db.Column(db.Boolean)

    # 1 to 1 relationship 
    sensor_id : int = db.Column(db.Integer, db.ForeignKey("sensor.id", ondelete='CASCADE'))
    
    calls_per_date : list = db.relationship('DeviceDayCalls', backref="device", lazy="select")

    loggs : list = db.relationship('Log', lazy="select")

    def __repr__(self):
        return f'<Device {self.ip}>'
    
    def to_json(self):
        return dict(ip=self.ip, userAgent=self.user_agent, flagged=self.flagged, last_call=self.last_call, country=self.country, region=self.region)

    
