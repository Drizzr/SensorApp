from .. import db

class Role(db.Model):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(50), unique=True)
    access_scope = db.Column(db.String(100), unique=True)

    def __repr__(self):
        return f'<Role {self.name}>'