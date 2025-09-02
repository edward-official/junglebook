from bson import ObjectId
from flask import Flask
from flask.json.provider import JSONProvider
import json
from router.api_router import api_blueprint
from router.view_router import reder_blueprint

app = Flask(__name__)


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
app.register_blueprint(api_blueprint)
app.register_blueprint(reder_blueprint)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
