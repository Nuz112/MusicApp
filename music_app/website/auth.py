from flask import Blueprint, url_for, redirect, render_template, request, flash, session
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db



auth = Blueprint('auth', __name__)


@auth.route('/', methods = ['GET', 'POST'])
def login():

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email = email).first()
        if user:
            if check_password_hash(user.password, password):

                session['user_name'] = user.first_name
                session['user'] = user.id
                return redirect(url_for('views.home'))
            
            else:
                flash('Incorrect Password, Try again', category='error')
        else:
            flash("You dont have an account with this email id. Please create one.", category='error')


    return render_template("login.html")


@auth.route('/sign_up', methods = ['GET', 'POST'])





def  sign_up():
    if request.method == 'POST':
        email = request.form['email']
        fname = request.form['firstname']
        lname = request.form['lastname']
        password1 = request.form['password1']
        password2 = request.form['password2']
        
        session['user_name'] = fname
        
        # Check if the email already exists in the database
        existing_user = User.query.filter_by(email=email).first()

        if existing_user:
            flash('You already creat an account. You should login with this email id or use a different email id.', category='error')
        elif len(email) < 5:
            flash('email must be greater than 4 charachter', category='error')
        elif len(fname) < 3:
            flash('First name must be greater than 2 charachter', category='error')
        elif password1 != password2:
            flash('Your passwords should be match', category='error')
        elif len(password1) < 4:
            flash('minimum length of password should be 4', category='error')
        else:

            new_user = User(email= email, first_name = fname, password = generate_password_hash(password1, method= 'sha256') , last_name = lname )
            db.session.add(new_user)
            db.session.commit()
            session['user'] = new_user.id
            return redirect(url_for("views.home"))
            

    

    return render_template("signup.html")

@auth.route('/logout')

def logout():
    user_name = session.get('user_name')
    user = session.get('user')
    if user_name:
        session.pop('user_name', None)
        session.pop('user', None)
    return redirect(url_for('auth.login'))
