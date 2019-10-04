from flask import Flask, render_template, flash, redirect, url_for, session, logging, request, Response, make_response
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, FileField
from passlib.hash import sha256_crypt
from functools import wraps
import os
from io import BytesIO
import base64
import PIL
import pgeocode
from PIL import Image

#Application Config below
#<------------------------->
app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
#Mysql config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'computr.io'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
#init mysql
mysql = MySQL(app)

#Non app route functions
#<----------------------->
#Function used to check if session is logged in to ensure orders are created with a logged in account
def is_logged_in_for_order(zip, support_Type):
    if 'logged_in' in session:
        return True
    else:
        flash("Unauthorized, please login", "danger")
        return redirect(url_for('login', zip=zip, support_Type=support_Type))

#Function used to check if a session is active before accessing dashboard
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Unauthorized, please login", "danger")
            return redirect(url_for('login'))
    return wrap

#Function  used to pull userid from session Username
def get_userid():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT id FROM users WHERE username=%s", [session['username']])
    if result >0:
        data = cur.fetchone()
        userid = data['id']
        return userid
        cur.close()
    else:
        flash("Userid was not found, please login to continue", "danger")
        cur.close()

#Function used to define and check permissions for accessing different applications
def permission():
    if 'logged_in' in session:
        cur = mysql.connection.cusor()
        result = cur.execute("SELECT permission FROM users where userid=%s", [get_userid()])
        if result >0:
            data = cur.fetchone()
            perm = data['permission']
            return perm
            cur.close()
        else:
            flash("No permission value found, please try again!", "danger")
            return redirect(url_for('home'))
            cur.close()
    else:
        flash("Unauthorized, please login", "danger")
        return redirect(url_for('home'))
        cur.close()

#Function used to check if user meets permission minimum
def permCheck(required_Value):
    if permission() >= required_Value:
        return True
    else:
        return False

#Function used to fetch profile pictures by userid
def profile_Image(userid):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT image from profiles WHERE userid=%s", [userid])
    if result > 0:
        data = cur.fetchone()
        profile_Pic = data['image']
        return str(profile_Pic)

def zipcode(offerzip, techzip):
    dist = pgeocode.GeoDistance('us')
    distance = dist.query_postal_code(offerzip, techzip)
    distance = (distance/1.609)
    return round(distance)

#Class used for generating order form on Home page
class orderForm(Form):
    zip = StringField('Zip Code', [validators.Length(min=5, max=9)])
    support_Type = StringField('Support Type', [validators.DataRequired()])

#Class used for generating final order form on Order page
class finalOrderForm(Form):
    support_Type = StringField("Support Type", [validators.DataRequired()])
    name = StringField("Name", [validators.DataRequired()])
    address = StringField("Street Address", [validators.DataRequired()])
    city = StringField("City", [validators.DataRequired()])
    state = StringField("State", [validators.DataRequired()])
    zip = StringField("Zip Code", [validators.DataRequired()])
    country = StringField("Country", [validators.DataRequired()])
    phone = StringField("Mobile Phone Number", [validators.DataRequired()])
    email = StringField("Email", [validators.DataRequired()])
    issue = TextAreaField("Describe Your Issue", [validators.DataRequired()])
    computer = StringField("Computer Make and Model", [validators.DataRequired()])
    operating_System = StringField("Operating System", [validators.DataRequired()])

#Class used for generating ticket form on Ticket page
class ticketForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=100)])
    cell = StringField("Cell Phone Number", [validators.Length(min=10, max=10)])
    issue = TextAreaField("Describe Your Issue", [validators.DataRequired()])

#Class used for generating registration page
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=100)])
    password = PasswordField('Password', [validators.DataRequired(), validators.EqualTo('confirm', message='Passwords do not match!')])
    confirm = PasswordField('Confirm Password')
    street_address = StringField("Street Address", [validators.Length(min=10, max=100)])
    city = StringField("City", [validators.Length(min=3, max=100)])
    state = StringField("State", [validators.Length(min=4, max=25)])
    zip = StringField("Zip Code", [validators.Length(min=5, max=10)])
    phone = StringField("Phone Number", [validators.Length(min=10, max=10)])
    cell = StringField("Cell Phone Number", [validators.Length(min=10, max=10)])
class writeUpForm(Form):
    fault = TextAreaField('Fault', [validators.Length(min=1, max=500)])
    corrective = TextAreaField('Corrective', [validators.Length(min=1, max=500)])

#Technition Pages below
#<--------------------------------------->
#App route used to generate technian Dashboard
@app.route('/tech/dashboard')
@is_logged_in
def techDashboard():
    cur = mysql.connection.cursor()
    username = session['username']
    result = cur.execute("SELECT * FROM users WHERE username=%s", [username])
    if result > 0:
        data = cur.fetchone()
        userid = data['id']
        street = data['street']
        city = data['city']
        state= data['state']
        zip= data['zip']
    result_2 = cur.execute("SELECT * FROM profiles WHERE userid=%s", [userid])
    if result_2 > 0:
        profile = cur.fetchone()
    else:
        flash("No data found", "danger")
    return render_template('techDashboard.html', street=street, city=city, state=state, zip=zip, userid=userid, pic=profile_Image(userid), data=profile)

@app.route('/tech/offers')
@is_logged_in
def techOffer():
    int = 0
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM orders WHERE status='offer'",)
    offerData = list(cur.fetchall())
    result_2 = cur.execute("SELECT * FROM users WHERE username=%s", [session['username']])
    techData = cur.fetchall()
    techZip = techData[0]['zip']
    for row in offerData:
        offerZip = row['zip']
        if zipcode(offerZip, techZip) > 100:
            print("------DELETED--------")
            print(offerData[int]['id'])
            print(int)
            print(offerData[int])
            print("-------------------------")
            del offerData[int]
            int = int + 1
        else:
            print("---------SAVE-------------")
            print(offerData[int]['id'])
            print(int)
            print(offerData[int])
            int = int + 1
            print("-------------------------")
    return render_template('techoffers.html', data=offerData, pic=profile_Image(get_userid()))

@app.route('/tech/offers/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def techOfferInspect(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM orders WHERE id=%s", [id])
    orderData = cur.fetchone()
    cur.close()

    if request.method == "POST":
        cur = mysql.connection.cursor()
        cur.execute("UPDATE orders set status=%s WHERE id=%s", ("active", id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('techOffer'))
    else:
        pass

    return render_template('techoffersinspect.html', data=orderData, pic=profile_Image(get_userid()))


@app.route('/tech/history')
@is_logged_in
def techHistory():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM orders WHERE assignedid=%s", [get_userid()])
    data = cur.fetchall()
    return render_template('techHistory.html', data=data, pic=profile_Image(get_userid()))

@app.route('/tech/history/active')
@is_logged_in
def techHistoryActive():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM orders WHERE status='active' AND assignedid=%s", [get_userid()])
    data = cur.fetchall()
    return render_template('techHistory.html', data=data, pic=profile_Image(get_userid()))

@app.route('/tech/check/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def techCheckOrder(id):
    form = writeUpForm(request.form)
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM orders WHERE id=%s", [id])
    orderData = cur.fetchall()
    writeUp = cur.execute("SELECT * FROM order_writeups WHERE orderid=%s", [id])
    write = cur.fetchall()

    if request.method == "POST":
        cur = mysql.connection.cursor()
        fault = form.fault.data
        corrective = form.corrective.data
        cur.execute("INSERT INTO order_writeups(orderid, fault, corrective) VALUES (%s, %s, %s)", ([id], fault, corrective))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('techCheckOrder', id=id))

    return render_template('techCheck.html', form=form, data=orderData, writeUps=write, pic=profile_Image(get_userid()))


#Basic information, and entry pages below
#<--------------------------------------->
#App route used to generate Home page
@app.route('/', methods=['GET', 'POST'])
def index():
    form = orderForm(request.form)
    if request.method == "POST" and form.validate():
        #Creates order form on index page
        zip = form.zip.data
        support_Type = form.support_Type.data
        flash("Order being placed, please continue your order after redirect!", "success")
        #Redirects to finalize order
        return redirect(url_for('order', zip=zip, support_Type=support_Type))
    return render_template('home.html', form=form, entries=["Home", "Remote", "Center", "Unsure"])

#App route used to generate About page
@app.route('/about')
def about():
    return render_template('about.html')

#App route used to generate FAQ page
@app.route('/faq')
def faq():
    return render_template('faq.html')

#Order information, and pages below
#<----------------------------------->
#App route used to create order from new order page
@app.route('/order', methods=['GET', 'POST'])
def orderM():
    username = session['username']
    app.logger.info(username)
    form = finalOrderForm(request.form)
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM  users WHERE username=%s", [username])
    if result > 0:
        #Attempts to auto populate order information
        data = cur.fetchone()
        userid = data['id']
        form.name.data = data['name']
        form.email.data = data['email']
        form.address.data = data['street']
        form.city.data = data['city']
        form.state.data = data['state']
        form.zip.data = data['zip']
        form.phone.data = data['cell']
        cur.close()
    else:
        cur.close()
        pass
    if request.method == "POST":
        cur = mysql.connection.cursor()
        app.logger.info("REQUEST")
        userid = data['id']
        name = form.name.data
        address = form.address.data
        city = form.city.data
        state = form.state.data
        country = form.country.data
        zipcode = form.zip.data
        phone = form.phone.data
        email = form.email.data
        issue = form.issue.data
        computer = form.computer.data
        operating_System = form.operating_System.data
        support_Type = form.support_Type.data
        cur.execute("INSERT INTO orders(userid, name, email, phone, street, city, state, country, zip, issue, support_Type, computer, operating_System, status) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (userid, name, email, phone, address, city, state, country, zipcode, issue, support_Type, computer, operating_System, "offer"))
        mysql.connection.commit()
        cur.close()
        flash("Success", "success")
    return render_template('order.html', form=form, entries=["Home", "Remote", "Center", "Unsure"], os=["Windows", "Mac", "Linux"], pic=profile_Image(get_userid()))

def orderInformation(id):
    cur = mysql.connection.cursor()
    order = cur.execute("SELECT * FROM orders WHERE id=%s", [id])
    writeup = cur.execute("SELECT * FROM order_writeups WHERE orderid=%s", [id])
    write = cur.fetchall()
    orderData=cur.fetchall()

@app.route('/order/check/<string:id>', methods=['GET', 'POST'])
@is_logged_in
def checkOrder(id):
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM orders WHERE id=%s", [id])
    orderData = cur.fetchall()
    writeUp = cur.execute("SELECT * FROM order_writeups WHERE orderid=%s", [id])
    write = cur.fetchall()
    return render_template('check.html', data=orderData, writeUps=write, pic=profile_Image(get_userid()))

#Function used to redirect orders which began being placed while not logged into an account
@app.route('/order/<string:zip>/<string:support_Type>', methods=['GET', 'POST'])
def order(zip, support_Type):
    if is_logged_in_for_order(zip, support_Type) == True:
        username = session['username']
        app.logger.info(username)
        form = finalOrderForm(request.form)
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM  users WHERE username=%s", [username])
        if result > 0:
            #Attempts to auto populate order information
            data = cur.fetchone()
            form.name.data = data['name']
            form.email.data = data['email']
            form.address.data = data['street']
            form.city.data = data['city']
            form.state.data = data['state']
            form.zip.data = data['zip']
            form.phone.data = data['cell']
            cur.close()
        else:
            cur.close()
            pass
        if request.method == "POST":
            cur = mysql.connection.cursor()
            app.logger.info("REQUEST")
            userid = data['id']
            name = form.name.data
            address = form.address.data
            city = form.city.data
            state = form.state.data
            country = form.country.data
            zipcode = form.zip.data
            phone = form.phone.data
            email = form.email.data
            issue = form.issue.data
            computer = form.computer.data
            operating_System = form.operating_System.data
            support_Type = form.support_Type.data
            cur.execute("INSERT INTO orders(userid, name, email, phone, street, city, state, country, zip, issue, support_Type, computer, operating_System, status) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (userid, name, email, phone, address, city, state, country, zipcode, issue, support_Type, computer, operating_System, "offer"))
            mysql.connection.commit()
            cur.close()
            flash("Success", "success")
        return render_template('order.html', form=form, entries=["Home", "Remote", "Center", "Unsure"], os=["Windows", "Mac", "Linux"])
    else:
        return redirect(url_for('login_With_Order', zip=zip, support_Type=support_Type))

#App route used to generate page for reviewing order history
@app.route('/history')
@is_logged_in
def history():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM orders WHERE userid=%s", [get_userid()])
    if result > 0:
        data = cur.fetchall()
    else:
        flash("No orders found! Please contact support if you believe this is an error", "danger")
    return render_template('history.html', data=data, pic=profile_Image(get_userid()))

#App route used to generate page from reviewing active order history
@app.route('/history/active')
@is_logged_in
def history_Active():
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM orders WHERE (status='active' AND userid=%s) OR (status='offer' AND userid=%s)", ([get_userid()], [get_userid()]))
    if result > 0:
        data = cur.fetchall()
    else:
        flash("No orders found! Please contact support if you believe this is an error", "danger")
    return render_template('history.html', data=data, pic=profile_Image(get_userid()))

#Support pages below
#<------------------->
#App route used to generate support tickets
@app.route('/ticket', methods=['GET', 'POST'])
@is_logged_in
def ticket():
    form = ticketForm(request.form)
    cur = mysql.connection.cursor()
    result = cur.execute("SELECT * FROM tickets WHERE userid=%s", [get_userid()])
    if result > 0:
        ticket_Data = cur.fetchall()
    else:
        flash("No support tickets detected!", "danger")
        form.name.data = data['name']
        form.username.data = data['username']
        form.email.data = data['email']
        form.cell.data = data['cell']
    if request.method == 'POST':
        name = form.name.data
        username = form.username.data
        email = form.email.data
        cell = form.cell.data
        issue = form.issue.data
        cur.execute("INSERT into tickets(userid, name, username, email, cell, issue) VALUES(%s,%s,%s,%s,%s,%s)", (userid, name, username, email, cell, issue))
        mysql.connection.commit()
        flash("Support ticket succesfully submitted, please wait 24 business hours for your ticket to be reviewed and responded to!", "success")

    return render_template('ticket.html', pic=profile_Image(get_userid()), form=form, data=ticket_Data)

#Account pages below
#<------------------>
#App route used to generate account page used for editing profile images, bio, country, etc...
@app.route('/account', methods=['GET', 'POST'])
def account():
    cur = mysql.connection.cursor()
    userid = get_userid()
    if request.method == 'POST':
        name = request.form['name']
        country = request.form['country']
        bio = request.form['bio']
        file = request.files['inputFile']
        #Process image into 100 base width by percentage to keep aspect ratio
        basewidth = 100
        img = Image.open(file)
        wpercent = (basewidth / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
        #Pull userid from database
        #Directory to save static profile images to
        save_Dir = ("C:\\Users\\Sage Hopkins\\Documents\\GitHub\\computr.io\\Computr.io\\static\\profiles\\" + str(userid))
        if os.path.exists(save_Dir) != True:
            os.mkdir(save_Dir)
        else:
            pass
        img.save(save_Dir + "\\" + str(userid) + ".jpg", format="jpeg")
        cur.execute("INSERT INTO profiles(userid , image, bio, name, country) VALUES(%s, %s, %s, %s, %s)", (userid, "profiles" + "/" + str(userid) + "/" + str(userid) + ".jpg", bio, name, country))
        mysql.connection.commit()
        flash("Profile picture succesfully updated!", "success")
        cur.close()
    return render_template('account.html', pic=profile_Image(userid))

#App route used to generate Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))
        street = form.street_address.data
        city = form.city.data
        state = form.state.data
        zip = form.zip.data
        phone = form.phone.data
        cell = form.cell.data
        #SQL Cursor
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users(name, email, username, password, street, city, state, zip, phone, cell) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (name, email, username, password, street, city, state, zip, phone, cell))
        mysql.connection.commit()
        cur.close()
        flash("You've been succesfully registered to Computr.io!", "success")
        return redirect(url_for('index'))
    return render_template('register.html', form=form)

#App route used to generate login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM  users WHERE username=%s", [username])
        if result > 0:
            data = cur.fetchone()
            password = data['password']
            if sha256_crypt.verify(password_candidate, password):
                app.logger.info(username + ' password autheticated!')
                session['logged_in'] = True
                session['username'] = username
                flash('You are now logged in', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = 'Invalid login!'
                app.logger.info(username + ' password does not match!')
                return render_template('login.html', error=error)
                cur.close()
        else:
            error = 'Username not found!'
            app.logger.info(username + ' does not exist!')
            return render_template('login.html', error=error)
    return render_template('login.html')

#App route used to generate login page, when an order is placed from home page, and passes information along
@app.route('/login/<string:zip>/<string:support_Type>', methods=['GET', 'POST'])
def login_With_Order(zip, support_Type):
    if request.method == 'POST':
        username = request.form['username']
        password_candidate = request.form['password']
        cur = mysql.connection.cursor()
        result = cur.execute("SELECT * FROM  users WHERE username=%s", [username])
        if result > 0:
            data = cur.fetchone()
            password = data['password']
            if sha256_crypt.verify(password_candidate, password):
                app.logger.info(username + ' password autheticated!')
                session['logged_in'] = True
                session['username'] = username
                flash('You are now logged in', 'success')
                return redirect(url_for('order', zip=zip, support_Type=support_Type))
            else:
                error = 'Invalid login!'
                app.logger.info(username + ' password does not match!')
                return render_template('login.html', error=error)
                cur.close()
        else:
            error = 'Username not found!'
            app.logger.info(username + ' does not exist!')
            return render_template('login.html', error=error)
    return render_template('login.html')

#App route used to generate logout page
@app.route('/logout')
def logout():
    session.clear()
    flash("You've been logged out!", 'success')
    return redirect(url_for('index'))

#App route used to generate dashboard page
@app.route('/dashboard')
@is_logged_in
def dashboard():
    cur = mysql.connection.cursor()
    username = session['username']
    result = cur.execute("SELECT * FROM users WHERE username=%s", [username])
    if result > 0:
        data = cur.fetchone()
        userid = data['id']
        street = data['street']
        city = data['city']
        state= data['state']
        zip= data['zip']
    result_2 = cur.execute("SELECT * FROM profiles WHERE userid=%s", [userid])
    if result_2 > 0:
        profile = cur.fetchone()
    else:
        flash("No data found", "danger")
    return render_template('dashboard.html', street=street, city=city, state=state, zip=zip, userid=userid, pic=profile_Image(userid), data=profile)

if __name__ == '__main__':
    app.secret_key='secret123'
    app.run(debug=True)
