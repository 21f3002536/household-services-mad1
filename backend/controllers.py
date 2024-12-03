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
    services=get_services()
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
            return render_template("professional_signup.html",msg="Sorry, this mail already registered!!!",services=services)
        new_usr=User(user_id=uname,password=pwd,role=1)
        db.session.add(new_usr)
        new_prof=Professional(email=uname,full_name=full_name,pin_code=pin_code,service_id=service_id,experience=experience)
        db.session.add(new_prof)
        db.session.commit()
        return render_template("login.html",msg="Registration successfull, try login now")
    
    return render_template("professional_signup.html",msg="",services=services)

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
    pending_requests=get_pending_requests(id)
    accepted_requests=get_accepted_requests(id)
    closed_requests=get_closed_requests(id)
    return render_template("professional_dashboard.html",pending_requests=pending_requests,closed_requests=closed_requests,name=name,id=id,accepted_requests=accepted_requests)

@app.route("/customer/<name>/<id>", methods=["GET", "POST"])
def customer_dashboard(name,id):
    services=get_services()
    customer_requests=get_customer_requests(id)
    return render_template("customer_dashboard.html",customer_requests=customer_requests,services=services,name=name,id=id)

@app.route("/admin/add_service", methods=["GET", "POST"])
def new_service():
    if request.method=="POST":
        sname=request.form.get("name")
        price=request.form.get("price") 
        description=request.form.get("description")
        time=request.form.get("time")
        newservice= Services(name=sname,price=price,description=description,time_required=time)
        db.session.add(newservice)
        db.session.commit()
        return redirect(url_for("admin_dashboard"))
    return render_template("add_service.html")

@app.route("/admin/search", methods=["GET","POST"])
def search_admin():
    if request.method=="POST":
        search_txt=request.form.get("search_txt")
        by_services=search_by_services(search_txt)
        by_professionals=search_by_professionals(search_txt)
        services= get_services()
        professionals = get_professionals()
        requests = get_requests()
        if by_services:
            return render_template("admin_dashboard.html",services=by_services,professionals=professionals,requests=requests)
        elif by_professionals:
            return render_template("admin_dashboard.html",professionals=by_professionals,services=services,requests=requests)
    return redirect(url_for("admin_dashboard"))

@app.route("/customer/<name>/<id>/search", methods=["GET","POST"])
def search_customer(name,id):
    if request.method=="POST":
        search_txt=request.form.get("search_txt")
        by_services=search_by_services(search_txt)
        customer_requests=get_customer_requests(id)
        return render_template("customer_dashboard.html",services=by_services,name=name,id=id,customer_requests=customer_requests)
    return redirect(url_for("customer_dashboard",name=name,id=id))

@app.route("/admin/edit_service/<id>",methods=["GET","POST"])
def edit_service(id):
    s=get_service(id)
    if request.method=="POST":
        sname=request.form.get("name")
        price=request.form.get("price")
        description=request.form.get("description")
        time=request.form.get("time")
        s.name=sname
        s.price=price
        s.description=description
        s.time_required=time
        db.session.commit()
        return redirect(url_for("admin_dashboard"))
    
    return render_template("edit_service.html",service=s)

@app.route("/admin/delete_service/<id>",methods=["GET","POST"])
def delete_service(id):
    s=get_service(id) 
    db.session.delete(s)
    db.session.commit()
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/delete_prof/<id>",methods=["GET","POST"])
def delete_prof(id):
    p=get_professional(id) 
    db.session.delete(p)
    db.session.commit()
    return redirect(url_for("admin_dashboard"))

@app.route("/customer/<name>/<id>/<sid>/book", methods=["GET", "POST"])
def book_service(name,id,sid):
    date_requested=datetime.now()
    new_request=Service_requests(service_id=sid,customer_id=id,professional_id=None,date_requested=date_requested,date_completed=None,status="requested",rating=None,remarks=None)
    db.session.add(new_request)
    db.session.commit()
    return redirect(url_for("customer_dashboard",name=name,id=id))

@app.route("/professional/<name>/<id>/<rid>/accept",methods=["GET","POST"])
def accept_request(name,id,rid):
    r=get_request(rid)
    r.professional_id=id
    r.status="accepted"
    db.session.commit()
    return redirect(url_for("professional_dashboard",name=name,id=id))

@app.route("/customer/<name>/<id>/<rid>/close",methods=["GET","POST"])
def close_request(name,id,rid):
    r=get_request(rid)
    if request.method=="POST":
        rating=int(request.form.get("rating"))
        remarks=request.form.get("remarks")
        r.status="completed"
        date_completed=datetime.now()
        r.date_completed=date_completed
        r.rating=rating
        r.remarks=remarks
        if r.request_professional.rating:
            total_rating=r.request_professional.rating*r.request_professional.count
        else:
            total_rating=0
        r.request_professional.count+=1
        db.session.commit()
        r.request_professional.rating=(total_rating+rating)/r.request_professional.count
        db.session.commit()
        return redirect(url_for("customer_dashboard",name=name,id=id))
    return render_template("close_service.html",name=name,id=id,request=r)

@app.route("/admin/summary")
def admin_summary():
    plot1_path = generate_admin_summary_plot1()
    plot2_path = generate_admin_summary_plot2()
    return render_template(
        "admin_summary.html",
        request_summary_plot=plot1_path,
        service_summary_plot=plot2_path
    )

@app.route("/admin/view_prof/<pid>")
def view_prof_admin(pid):
    professional=get_professional(pid)
    return render_template("view_professional_admin.html", professional=professional)

@app.route("/admin/view_request/<rid>")
def view_request_admin(rid):
    request=get_request(rid)
    return render_template("view_request_admin.html", request=request)

@app.route("/professional/<name>/<pid>/view")
def view_professional(name,pid):
    professional=get_professional(pid)
    return render_template("view_professional.html", name=name, id=pid, professional=professional)


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

def get_pending_requests(id):
    prof=Professional.query.filter_by(professional_id=id).first()
    service_id=prof.service_id
    pending_requests=Service_requests.query.filter_by(status="requested",service_id=service_id).all()
    return pending_requests

def get_accepted_requests(id):
    accepted_requests=Service_requests.query.filter_by(status="accepted", professional_id=id).all()
    return accepted_requests

def get_closed_requests(id):
    closed_requests=Service_requests.query.filter_by(status="completed", professional_id=id).order_by(Service_requests.date_completed.desc()).all()
    return closed_requests

def get_customer_requests(id):
    customer_requests=Service_requests.query.filter_by(customer_id=id).all()
    return customer_requests

def search_by_services(search_txt):
    services=Services.query.filter(Services.name.ilike(f"%{search_txt}%")).all()
    return services

def search_by_professionals(search_txt):
    professionals=Professional.query.filter(Professional.full_name.ilike(f"%{search_txt}%")).all()
    return professionals

def get_service(id):
    s=Services.query.filter_by(service_id=id).first()
    return s

def get_professional(id):
    p=Professional.query.filter_by(professional_id=id).first()
    return p

def get_request(id):
    r=Service_requests.query.filter_by(request_id=id).first()
    return r

def generate_admin_summary_plot1():
    # Plot 1: Number of Service Requests by Status
    status_counts = (
        db.session.query(Service_requests.status, func.count(Service_requests.request_id))
        .group_by(Service_requests.status)
        .all()
    )
    statuses, counts = zip(*status_counts) if status_counts else ([], [])
    
    # Generate plot
    plt.figure(figsize=(8, 6))
    plt.bar(statuses, counts, color="skyblue")
    plt.title("Number of Service Requests by Status")
    plt.xlabel("Status")
    plt.ylabel("Count")
    
    # Save plot
    file_path = "./static/images/request_summary.jpeg"
    plt.savefig(file_path)
    plt.close()  # Close the figure to free memory
    return file_path


def generate_admin_summary_plot2():
    # Plot 2: Number of Service Requests per Service Type
    service_counts = (
        db.session.query(Services.name, func.count(Service_requests.request_id))
        .join(Service_requests, Services.service_id == Service_requests.service_id)
        .group_by(Services.name)
        .all()
    )
    service_names, service_request_counts = zip(*service_counts) if service_counts else ([], [])
    
    # Generate plot
    plt.figure(figsize=(10, 6))
    plt.barh(service_names, service_request_counts, color="lightcoral")
    plt.title("Number of Service Requests per Service Type")
    plt.xlabel("Count")
    plt.ylabel("Service Type")
    
    # Save plot
    file_path = "./static/images/service_summary.jpeg"
    plt.savefig(file_path)
    plt.close()  # Close the figure to free memory
    return file_path