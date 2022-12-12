from .. import db

# Define the UserRoles association table

userRoleLink = db.Table("userRoleLink",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")), # CASCADE enables deletion if parent is deleted via session.query().filter().delete()
    db.Column("role_id", db.Integer, db.ForeignKey("role.id"))
)