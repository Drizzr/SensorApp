from .. import db

deviceUserLink = db.Table("ipUserLink",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")), # CASCADE enables deletion if parent is deleted via session.query().filter().delete()
    db.Column("device_id", db.Integer, db.ForeignKey("device.id"))
)