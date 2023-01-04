#Import important libraries

from flask import Flask, config, render_template, request, redirect, url_for, flash, session
from pandas import options
from werkzeug.utils import secure_filename
import numpy as np
import os
import sys
import pandas as pd
from flask_mysqldb import MySQL

# initailise Flask instance and configure parameters
app = Flask(__name__)

# To use flash message and keep user logged in (by creating a 24 character session key)
app.secret_key = os.urandom(24)


# MYSQL database config.  Add you data base details here.
app.config['MYSQL_HOST'] = ''
app.config['MYSQL_USER'] = ''
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = ''

mysql = MySQL(app)

# Declare the routes of the web app. 

# Route for homepage (logged out)
@app.route('/')
def index():
    if 'user_id' in session:                   # if session is acctive redirect to the logeed in Homepage.
        return redirect('/Home')
    else:
        return render_template('index.html')   # otherwise open the logged out homepage. 


# Route for Homepage (logged in)
@app.route('/Home')
def home():
    if 'user_id' in session:
        return render_template('Home.html')
    else:
        return redirect('/')

# Route for login page
@app.route('/Login', methods = ['POST', 'GET'])
def Login():
    if 'user_id' in session:            # if session is active
        return redirect('/Home')        # goto home page logged in
    else:                               # otherwise, check if the user information provided in form, matches to database.
        if request.method == 'POST':   

            Email = request.form['Email']
            password = request.form['password']
            cur = mysql.connection.cursor()
            #cur = connection.cursor()
            cur.execute( "SELECT * FROM users WHERE Email = %s AND password = %s",(Email,password) )
            user = cur.fetchall()
            
            if len(user)>0:
                session['user_id']=user[0][0]     # save the user id in the user id session
                session['user'] = user            # dave the complete info of user in user sesiion (to be used in other functions)
                return redirect(url_for('home'))  # Take the user to logged in homepage
            else:                                 # If details do not match the database
                flash('Enter correct Email and Password') # falsh this message
            return redirect(url_for('Login'))             # Show the login page again 
        return render_template('Login.html')

# Route for register page
@app.route('/Register', methods = ['POST', 'GET'])
def Register():
    if 'user_id' in session:                    # If session is active
        return redirect('/Home')                # goto logged in home page
    else:                                       # otherwise, take the info from register form
        if request.method == 'POST':
            First_name = request.form['First_name']
            Last_name = request.form['Last_name']
            age_verification = request.form['age_verification'] 
            Email1 = request.form['u_Email']
            Email2 = request.form['re_Email']
            password1 = request.form['u_password']
            password2 = request.form['re_password']

            if Email1==Email2 and password1==password2:  # Check for humman error in spellings
                Email = Email1
                password = password1
                cur = mysql.connection.cursor()         # activate cursor
                # push the data to users data base if the data does not already exsisit 
                cur.execute( "SELECT * FROM users WHERE Email = %s AND password = %s",(Email,password) )
                user = cur.fetchall()
                if len(user)>0:  # if already exsist
                    flash('Email ID already exsist. Login instead.') # flash this message
                    return redirect(url_for('Register'))             # and redirect to register page
                else:
                    cur.execute( "INSERT INTO users (First_name,Last_name,age_verification,Email,password) VALUES('{}', '{}', '{}', '{}', '{}')".format(First_name,Last_name,age_verification,Email,password))
                    mysql.connection.commit() # commit the change
                    cur.close()               # close the cursor
                    return redirect('/Login')
            else:
                flash('Email or Password do not match.') # if spelling check fails
                return redirect(url_for('Register'))     # flash this message
        return render_template('Register.html')


# Route for feedback page
@app.route('/Feedback', methods = ['POST', 'GET'])
def Feedback():
    if 'user_id' in session:       # if session is active, post the user info and submitted feedback to the feedbcak table in database
        if request.method == 'POST':
            user = session.get('user', None)
            user_id = user[0][0]
            First_name = user[0][1]
            Last_name = user[0][2]
            Email = user[0][4]
            print(First_name)
            feedback = request.form['feedback']   # get the feedback from form
            
            cur = mysql.connection.cursor()
            cur.execute( "INSERT INTO feedback (user_id,First_name,Last_name,Email,feedback) VALUES('{}','{}','{}','{}','{}')".format(user_id,First_name,Last_name,Email,feedback))
            mysql.connection.commit()  # Commit the change
            
            cur.close()                 # close the cursor
            return redirect(url_for('ThankYou'))  # Go to thanku=you page after feedback is uploaded
        return render_template('Feedback.html')
    else:                            # if there is no session,
        return redirect('/Login')    # do not let the user go to feed back page manually, and always take them to login page

# Route for logout
@app.route('/Logout')
def Logout():
    if 'user_id' in session:        # if session is active
        session.pop('user_id')      # logout the session and
        return redirect('/Login')   # take back to login page
    else:                           # otherwise
        return redirect('/Login')   # Go straight to login page

# Route for contact us page
@app.route('/Contact')
def Contact():
    return render_template('Contact.html')

# Route for about us page
@app.route('/About')
def About():
    return render_template('About.html')

# Route for
@app.route('/ThankYou')
def ThankYou():
    if 'user_id' in session:           # when feedback is submitted after logging in,  
        return render_template('ThankYou.html')   # show thanks page 
    else:                              # but if there is no session 
        return redirect('/')           # redirect to unlogged home page

# Route for Getstarted page
@app.route('/GetStarted')
def GetStarted():
    if 'user_id' in session:   #if session is active go to getstarted page else goto login page
        return render_template('GetStarted.html')
    else:
        return redirect('/Login')


# Route for session expired page
@app.route('/401')
def SessionExpired():  
    return render_template('SessionExpired.html')


   
if __name__ == '__main__':
    app.run(debug= True,host='0.0.0.0', port=5000)      # app will run on 0.0.0.0:5000