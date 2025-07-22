from flask import Flask, send_file, request
app = Flask(__name__)

@app.route("/")
def hello():
  return "Hello World!"


@app.route("/data/<run>/<hour>.png")
def serve_data(run, hour):
  return send_file("./data/" + run + "/" + hour + ".png", mimetype='image/png')

if __name__ == "__main__":
  app.run(host='0.0.0.0')


