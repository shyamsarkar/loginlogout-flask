from flask import Flask

app = Flask(__name__)


@app.route("/")
def Home():
    return "<h1>This is Home</h1><br><h2>Let's Solve everyting!</>"

# app.run()


"""CMD"""
# set FLASK_APP=sample
# set FLASK_ENV=development
# flask run


# shell
# $env:FLASK_APP = "sample"
# $env:FLASK_ENV = "development"
# flask run

# in this condition use command "python -m flask run"
