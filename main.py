from flask import Flask, render_template, request, redirect, url_for, session, flash
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123@localhost/login_system_flask'
db = SQLAlchemy(app)
app.secret_key = 'secrete_key'
app.permanent_session_lifetime = timedelta(minutes=15)


class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    usertype = db.Column(db.String(10), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False,
                           server_default=func.now())
    updated_at = db.Column(db.DateTime, nullable=False,
                           server_default=func.now(), onupdate=func.now())


@app.route('/')
def Home():
    if "user_id" in session:
        return redirect(url_for('Dashboard'))
    return render_template('index.html')


@app.route('/dashboard')
def Dashboard():
    if "user_id" in session:
        user_id = session['user_id']
        username = Users.query.filter_by(user_id=user_id).first().username
        usertype = session['usertype']
        return render_template("dashboard.html", username=username, usertype=usertype)
    return redirect(url_for("Home"))


@app.route('/signup', methods=['GET', 'POST'])
def Signup():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        usertype = "admin"
        created_at = datetime.now()
        cnt = Users.query.filter_by(
            username=username, password=password).count()
        if cnt == 0:
            sql = Users(
                username=username,
                password=password,
                usertype=usertype,
                created_at=created_at
            )
            db.session.add(sql)
            db.session.commit()
            flash('Account created Successfully!', 'success')
            return redirect(url_for("Login"))
        else:
            # flash message is not being handled
            flash('User Name Already Exists', 'warning')
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def Login():
    if "user_id" in session:
        return redirect(url_for('Home'))
    if request.method == 'POST':
        username = request.form.get('username').strip()
        password = request.form.get('password').strip()
        cnt = Users.query.filter_by(
            username=username, password=password)
        if cnt.count() > 0:
            user_id = cnt.first().user_id
            usertype = cnt.first().usertype
            session['user_id'] = user_id
            session['usertype'] = usertype
            flash('Login Successful', 'success')
            return redirect(url_for('Dashboard'))
        else:
            flash('Account Not found!', 'danger')
    return redirect(url_for("Home"))


@app.route('/logout')
def Logout():
    if 'user_id' in session:
        session.pop('user_id', None)
        if 'usertype' in session:
            session.pop('usertype', None)
        flash("Logged Out Successfully", "success")
    return redirect(url_for('Login'))
