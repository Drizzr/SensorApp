
from .. import db

class Room(db.Model):

    __tablename__ = "room"

    # room properties
    id : int = db.Column(db.Integer, primary_key=True)
    public_id : int = db.Column(db.String(50), unique=True)
    name : str = db.Column(db.String(50))
    description : str = db.Column(db.String(150))

    # foreign key (1 to many)
    user_id : int  = db.Column(db.Integer, db.ForeignKey("user.id", ondelete='CASCADE'))

    # relationship (1 to many)
    sensors : list = db.relationship('Sensor', backref="room", lazy="select", cascade="all,delete")


    def __repr__(self):
        return f'<Room {self.id}, {self.name}>'
    
    def to_json(self):
        return dict(user=self.user_id, id=self.public_id, name=self.name, description=self.description)