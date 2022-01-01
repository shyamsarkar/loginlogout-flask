from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json
import os

with open('config.json') as f:
    values = json.load(f)['values']

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/website'
app.config['UPLOAD_FOLDER'] = values['UPLOAD_FOLDER']
db = SQLAlchemy(app)
app.secret_key = 'This_is_a_very_complex_secret_key'
app.permanent_session_lifetime = timedelta(minutes=15)


""" SignUp Class """


class Personaldetail(db.Model):
    serial = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50), nullable=False)
    lname = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    timing = db.Column(db.String(20))
    image = db.Column(db.String(10))


""" Deleted Account Class """


class DeletedAC(db.Model):
    serial = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(50))
    lname = db.Column(db.String(50))
    email = db.Column(db.String(50))
    password = db.Column(db.String(255))
    createdon = db.Column(db.String(20))
    deletedon = db.Column(db.String(20))
    image = db.Column(db.String(10), nullable=True)


""" News Class = all articles """


class News(db.Model):
    serial = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(1000), nullable=False)
    date = db.Column(db.String(20), nullable=False)


""" Home Route """


@app.route('/')
def home():
    if "userEmail" in session:
        user_name = Personaldetail.query.filter_by(email=session['userEmail'])
        cook_key = request.cookies.get('articletype')
        if cook_key == None:
            cookie_less = News.query.paginate(
                per_page=values['article_length'], page=1)

            return render_template('index.html', user_name=user_name, values=values, all_news=cookie_less, number=1, total_pages=2)
        else:
            cookie_found = News.query.filter_by(cook_key)
            return render_template('index.html', user_name=user_name, values=values, all_news=cookie_found)
    else:
        return redirect(url_for('logout'))


""" Pagination """


@app.route('/page/<string:page_number>', methods=['GET', 'POST'])
def pagination(page_number):
    if "userEmail" in session:
        user_name = Personaldetail.query.filter_by(email=session['userEmail'])
        user_pass_home = False
        for elements in user_name:
            user_pass_home = elements.password
        cook_key = request.cookies.get('articletype')
        if cook_key == None:
            number = int(page_number)
            total_article = News.query.all()
            if len(total_article) % values['article_length'] == 0:
                total_pages = len(total_article) / values['article_length']
            else:
                total_pages = len(total_article) / values['article_length'] + 1

            cookie_less = News.query.paginate(
                per_page=values['article_length'], page=number)
            return render_template('index.html', user_name=user_name, values=values, all_news=cookie_less, number=number, total_pages=total_pages)
        else:
            cookie_found = News.query.filter_by(cook_key)
            return render_template('index.html', user_name=user_name, values=values, all_news=cookie_found)
    return redirect(url_for('login'))


""" SignUP Route  """


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')
        existEmail = Personaldetail.query.filter_by(email=email)
        existed = False
        for element in existEmail:
            existed = element.email
        if not existed:
            if fname and lname and email and password and cpassword:
                if len(password) >= 8 and len(password) <= 20:
                    if password == cpassword:
                        timing = datetime.now()
                        session.permanent = True
                        session['userEmail'] = email
                        pass_hash = generate_password_hash(
                            password, method='sha256')
                        OBJ = Personaldetail(fname=fname, lname=lname, email=email, password=pass_hash,
                                             timing=timing, image="")
                        db.session.add(OBJ)
                        db.session.commit()
                        flash('Account Created Successfully!', 'success')
                        return redirect(url_for('home'))
                    else:
                        flash('Password Mismatch!', 'warning')
                else:
                    flash('Password Must be between 8 and 20 characters.', 'danger')
        else:
            flash('Email Already Exists', 'warning')
    return render_template('signup.html')


""" Login Route """


@app.route('/login', methods=['GET', 'POST'])
def login():
    if "userEmail" in session:
        return redirect(url_for('home'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email and password:
            session.permanent = True
            OBJ = Personaldetail.query.filter_by(email=email)
            userPassword = False
            userEmail = False
            for elements in OBJ:
                userPassword = elements.password
                userEmail = elements.email
            if userEmail == False:
                flash('Account does not exist!', 'warning')
            elif check_password_hash(userPassword, password):
                session['userEmail'] = email
                flash('Login Successful', 'success')
                return redirect(url_for('home'))
            else:
                flash('Invalid Password!', 'danger')
    return redirect(url_for('signup'))


"""" LogOut Route """


@app.route('/logout')
def logout():
    if 'userEmail' in session:
        session.pop('userEmail', None)
        flash("Logged Out Successfully", "success")
    return redirect(url_for('signup'))


""" Update Profile Route """


@app.route('/updateprofile', methods=['GET', 'POST'])
def resetname():
    if "userEmail" in session:
        OBJ = Personaldetail.query.filter_by(email=session['userEmail'])
        user_pass_rename = False
        for elements in OBJ:
            user_pass_rename = elements.password
        if check_password_hash(user_pass_rename, session['pasword']):
            if request.method == 'POST':
                fname = request.form.get('fname')
                lname = request.form.get('lname')
                dpimg = request.files['dpimg']
                extension_file = dpimg.filename.split(".")[-1]
                name_detail = Personaldetail.query.filter_by(
                    email=session['emailid']).first()
                name_detail.fname = fname
                name_detail.lname = lname
                if extension_file == "jpg" or extension_file == "png":
                    image_name = str(name_detail.serial)
                    full_name_image = image_name+".png"
                    dpimg.save(os.path.join(
                        app.config['UPLOAD_FOLDER'], full_name_image))
                    name_detail.image = full_name_image
                else:
                    print("Invalid image")
                db.session.commit()
                flash('Details Updated', 'success')
            return render_template('update.html', user_name=user_name)
    return redirect(url_for('login'))


""" Delete Account Route """


@app.route('/delete', methods=['GET', 'POST'])
def deleteac():
    if "userEmail" in session:
        OBJ = Personaldetail.query.filter_by(email=session['emailid'])
        if request.method == 'POST':
            confirm_pass = request.form.get('cpass')
            user_password = "0"
            for elements in OBJ:
                user_fname = elements.fname
                user_lname = elements.lname
                user_email = elements.email
                user_password = elements.password
                user_timing = elements.timing
                user_deletedon = datetime.now()
                user_image = elements.image
            if check_password_hash(user_password, confirm_pass):
                user_detail = Personaldetail.query.filter_by(
                    email=session['userEmail']).first()
                backup_data = DeletedAC(fname=user_fname, lname=user_lname, email=user_email,
                                        password=user_password, createdon=user_timing, deletedon=user_deletedon, image=user_image)
                db.session.add(backup_data)
                db.session.delete(user_detail)
                db.session.commit()
                flash('Account Deleted Sucessfully', 'warning')
                return redirect(url_for('home'))
            else:
                flash('Invalid Credential!', 'danger')
                return redirect(url_for('home'))
        return render_template('delete.html', user_name=user_name)
    flash('To Delete Account, You must Login First.', 'warning')
    return redirect(url_for('login'))


""" Reset Password Route """


@app.route('/resetpass', methods=['GET', 'POST'])
def resetpass():
    if "emailid" in session:
        user_name = Personaldetail.query.filter_by(email=session['userEmail'])
        if request.method == 'POST':
            old_pass = request.form.get('oldpass')
            new_pass = request.form.get('newpass')
            confirm_pass = request.form.get('cpass')
            user_pass_reset = False
            for elements in user_name:
                user_pass_reset = elements.password
            if check_password_hash(user_pass_reset, old_pass) and (new_pass == confirm_pass):
                update_pass = Personaldetail.query.filter_by(
                    email=session['userEmail']).first()
                pass_hash = generate_password_hash(new_pass, method='sha256')
                update_pass.password = pass_hash
                db.session.commit()
                session.pop('userEmail', None)
                flash('Password Reset Successful', 'success')
                return redirect(url_for('login'))
            else:
                flash(
                    'Something Went Wrong! This caused because of incorrect data.', 'danger')
                return redirect(url_for('login'))
        return render_template('resetpass.html', user_name=user_name)
    flash('Login First!', 'warning')
    return redirect(url_for('login'))


"""alternate option for reset password or Forgot password """


@app.route('/resetpassalt', methods=['GET', 'POST'])
def resetpassalt():
    if request.method == 'POST':
        fname = request.form.get('fname')
        lname = request.form.get('lname')
        email = request.form.get('email')
        new_pass = request.form.get('new_pass')
        cnew_pass = request.form.get('cnew_pass')
        if new_pass == cnew_pass:
            OBJ = Personaldetail.query.filter_by(email=email)
            user_pass_reset = False
            user_fname_reset = False
            user_lname_reset = False
            for elements in OBJ:
                user_pass_reset = elements.password
                user_fname_reset = elements.fname
                user_lname_reset = elements.lname
            if (user_pass_reset != False):
                if (fname == user_fname_reset) and (lname == user_lname_reset):
                    update_pass = Personaldetail.query.filter_by(
                        email=email).first()
                    pass_hash = generate_password_hash(
                        new_pass, method='sha256')
                    update_pass.password = pass_hash
                    db.session.commit()
                    session.pop('userEmail', None)
                    flash('Password Reset Successful', 'success')
                    return redirect(url_for('login'))
                else:
                    flash('Name did not match!', 'danger')
            else:
                flash('Account Not Found!', 'danger')
                return redirect(url_for('login'))
        else:
            flash('Password did not match!', 'danger')
    return render_template('forgotpass.html')


""" Cookies Route """


@app.route('/articles', methods=['GET', 'POST'])
def articles():
    if request.method == 'POST':
        search = request.form.get('search')
        response = make_response("Your cookie is set...")
        response.set_cookie('articletype', search)
    return redirect(url_for('home'))


""" Add New Article or News """


@app.route('/addarticle', methods=['GET', 'POST'])
def addarticle():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        date = datetime.now()
        add_article = News(title=title, content=content, date=date)
        db.session.add(add_article)
        db.session.commit()
        flash('Article Added Successfully', 'success')
    return render_template('article.html')


if __name__ == '__main__':
    # app.run(debug=True, host="", port=80)
    app.run(debug=True)
