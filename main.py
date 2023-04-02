from app import create_app, db
from app.models import User, Log, Task, Role
from socket import gethostbyname, gethostname

app = create_app() # intitialisation of the flask-app (c.f. /app/__init__.py file)

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Log': Log, 'Message': Task, "Roles": Role}


if __name__ == "__main__":
    app.run(debug=True)