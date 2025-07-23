from flask import Flask, send_file, request
app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route("/data/<run>/<hour>/<field>.png")
def serve_data(run, hour, field):
    return send_file("./data/" + run + "/" +field + "/" + hour + ".png", mimetype='image/png')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
