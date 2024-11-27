#App routes
from flask import Flask,render_template,request,url_for,redirect
from .models import *
from flask import current_app as app
from datetime import datetime
from sqlalchemy import func
from werkzeug.utils import secure_filename
import matplotlib.pyplot as plt

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login",methods=["GET","POST"])
def signin():
    if request.method=="POST":
        uname=request.form.get("user_name")
        pwd=request.form.get("password")
        usr=User.query.filter_by(user_id=uname,password=pwd).first()
        if usr and usr.role==0: #Existed and admin
            return render_template("admin_home_layout.html")
        elif usr and usr.role==1: #Existed and professional
            return render_template("professional_home_layout.html")
        elif usr and usr.role==2: #Existed and customer
            return render_template("customer_home_layout.html")
        else:
            return render_template("login.html",msg="Invalid user credentials...")

    return render_template("login.html",msg="")

@app.route("/professional_register", methods=["GET","POST"])
def prof_signup():
    if request.method=="POST":
        uname=request.form.get("user_name")
        pwd=request.form.get("password") 
        full_name=request.form.get("full_name")
        pin_code=request.form.get("pin_code")
        service=request.form.get("service")
        service_des=Services.query.filter_by(description=service).first()
        service_id=service_des.service_id
        experience=request.form.get("experience")
        usr=User.query.filter_by(user_id=uname).first()
        if usr:
            return render_template("professional_signup.html",msg="Sorry, this mail already registered!!!")
        new_usr=User(user_id=uname,password=pwd,role=1)
        db.session.add(new_usr)
        new_prof=Professional(email=uname,full_name=full_name,pin_code=pin_code,service_id=service_id,experience=experience)
        db.session.add(new_prof)
        db.session.commit()
        return render_template("login.html",msg="Registration successfull, try login now")
    
    return render_template("professional_signup.html",msg="")

@app.route("/customer_register", methods=["GET","POST"])
def cust_signup():
    if request.method=="POST":
        uname=request.form.get("user_name")
        pwd=request.form.get("password") 
        full_name=request.form.get("full_name")
        pin_code=request.form.get("pin_code")
        usr=User.query.filter_by(user_id=uname).first()
        if usr:
            return render_template("customer_signup.html",msg="Sorry, this mail already registered!!!")
        new_usr=User(user_id=uname,password=pwd,role=2)
        db.session.add(new_usr)
        new_cust=Customer(email=uname,full_name=full_name,pin_code=pin_code)
        db.session.add(new_cust)
        db.session.commit()
        return render_template("login.html",msg="Registration successfull, try login now")
    
    return render_template("customer_signup.html",msg="")