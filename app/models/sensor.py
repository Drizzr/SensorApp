from unicodedata import name
from .. import db

class Sensor(db.Model):

    #sensor properties
    __tablename__ = "sensor"

    #sensor properties
    id : int = db.Column(db.Integer, primary_key=True)
    public_id : str = db.Column(db.String(50), unique=True)
    name : str = db.Column(db.String(150))
    type : str = db.Column(db.String(25))
    last_update : str = db.Column(db.String(50))
    value_map : dict = db.Column(db.JSON)

    # realtionships (1 to many)
    room_id : int = db.Column(db.Integer, db.ForeignKey("room.id", ondelete='CASCADE'))
    user_id : int = db.Column(db.Integer, db.ForeignKey("user.id", ondelete='CASCADE'))

    data : list = db.relationship('SensorDataSet', backref="sensor", lazy="select", cascade="all,delete")


    #auth_token = db.Column(db.str(50))
    #last_update_timestamp = db.Column(db.Integer) looking for a more elegant solution
    def __repr__(self):
        return f'<Sensor {self.id}, {self.name}>'
    
    def to_json(self):
        return dict(sensor_id=self.public_id, sensor_name=self.name, value_map = self.value_map)

class SensorDataSet(db.Model):

    __name__ = "sensor_data_set"

    id : int = db.Column(db.Integer, primary_key=True)
    sensor_id : int = db.Column(db.Integer, db.ForeignKey("sensor.id", ondelete='CASCADE'))
    time : str = db.Column(db.String)
    values : dict = db.relationship('DataPoint', backref="dataset", lazy="joined", cascade="all,delete")


    def __repr__(self):
        return f'<DataSet {self.sensor_id}, {self.time}>'

    def to_json(self):
        return dict(time=self.time, values=self.values)


class DataPoint(db.Model):

    __name__ = "data_point"
    id : int = db.Column(db.Integer, primary_key=True)
    description : str = db.Column(db.String(50))
    sensorData_id : int = db.Column(db.Integer, db.ForeignKey("sensor_data_set.id", ondelete='CASCADE'))
    value : int = db.Column(db.Integer)

    def __repr__(self):
        return f'<Value {self.description}: {self.value}>'

