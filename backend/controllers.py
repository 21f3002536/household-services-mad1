#App routes
from flask import Flask,render_template,request,url_for,redirect
from .models import *
from flask import current_app as app
from datetime import datetime
from sqlalchemy import func
from sqlalchemy import asc, desc
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
            return redirect(url_for("admin_dashboard"))
        elif usr and usr.role==1: #Existed and professional
            return redirect(url_for("professional_dashboard", name=usr.professionals.full_name,id=usr.professionals.professional_id))
        elif usr and usr.role==2: #Existed and customer
            return redirect(url_for("customer_dashboard", name=usr.customers.full_name,id=usr.customers.customer_id))
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

@app.route("/admin", methods=["GET","POST"])
def admin_dashboard():
    services= get_services()
    professionals = get_professionals()
    requests = get_requests()
    return render_template("admin_dashboard.html", services=services,professionals=professionals,requests=requests)

@app.route("/professional/<name>/<id>", methods=["GET", "POST"])
def professional_dashboard(name,id):
    pending_requests=get_pending_requests()
    closed_requests=get_closed_requests(id)
    return render_template("professional_dashboard.html",pending_requests=pending_requests,closed_requests=closed_requests,name=name,id=id)

@app.route("/customer/<name>/<id>", methods=["GET", "POST"])
def customer_dashboard(name,id):
    services=get_services()
    customer_requests=get_customer_requests(id)
    return render_template("customer_dashboard.html",customer_requests=customer_requests,services=services,name=name,id=id)



#other functions
def get_services():
    services=Services.query.all()
    return services

def get_professionals():
    professionals = Professional.query.all()
    return professionals

def get_requests():
    requests= Service_requests.query.all()
    return requests

def get_pending_requests():
    pending_requests=Service_requests.query.filter_by(status="requested").all()
    return pending_requests

def get_closed_requests(id):
    closed_requests=Service_requests.query.filter_by(status="closed", professional_id=id).order_by(Service_requests.date_completed.desc()).all()
    return closed_requests

def get_customer_requests(id):
    customer_requests=Service_requests.query.filter_by(customer_id=id).all()
    return customer_requests