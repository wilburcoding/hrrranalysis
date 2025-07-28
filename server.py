from flask import Flask, send_file, request, render_template
import os
app = Flask(__name__)


@app.route("/")
def hello():
    return render_template("index.html")


@app.route("/data/<run>/<field>/<hour>.png")
def serve_data(run, field, hour):
    return send_file("./data/" + run + "/" +field + "/" + hour + ".png", mimetype='image/png')

@app.route("/datalist")
def serve_datalist():
    # basically just an overview of existing data
    edata = {}
    for run in os.listdir("./data"):
        # get size of directory
        maxruns = len(os.listdir("./data/" + run + "/refc"))
        edata[run] =maxruns-1
    return edata
if __name__ == "__main__":
    app.run(host='0.0.0.0')
