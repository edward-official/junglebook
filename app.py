from flask import Flask
from flask.json.provider import JSONProvider
from bson import ObjectId
import json
from routes.view_router import render_blueprint
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
from routes.auth import auth_bp
from flask_jwt_extended import JWTManager

app = Flask(__name__)
mongoDB = MongoClient('localhost', 27017)
database = mongoDB.jungle_book
bcrypt = Bcrypt(app)

app.config['DB'] = database
app.config['BCRYPT'] = bcrypt
app.config['JWT_SECRET_KEY'] = "super-secret-key"
jwt = JWTManager(app)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)

class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)
    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)


app.json = CustomJSONProvider(app)
<<<<<<< HEAD
app.register_blueprint(render_blueprint)
=======
app.register_blueprint(auth_bp)
>>>>>>> 610c960 (login/signup complete)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
