#Data models

from flask_sqlalchemy import SQLAlchemy

db=SQLAlchemy()

class User(db.Model):
    __tablename__="user"
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.String,unique=True,nullable=False)
    password=db.Column(db.String,nullable=False)
    role=db.Column(db.Integer,nullable=False)
    customers=db.relationship("Customer",cascade="all,delete",backref="user",lazy=True)
    professionals=db.relationship("Professional",cascade="all,delete",backref="user",lazy=True)

class Customer(db.Model):
    __tablename__="customer"
    customer_id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,db.ForeignKey("user.user_id"),nullable=False)
    full_name=db.Column(db.String,nullable=False)
    pin_code=db.Column(db.Integer,nullable=False)
    customer_requests=db.relationship("Service_requests",cascade="all,delete",backref="customer",lazy=True)

class Professional(db.Model):
    __tablename__="professional"
    professional_id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,db.ForeignKey("user.user_id"),nullable=False)
    full_name=db.Column(db.String,nullable=False)
    pin_code=db.Column(db.Integer,nullable=False)
    experience=db.Column(db.Integer,nullable=False)
    approval_status=db.Column(db.String,default="pending")
    service_id=db.Column(db.Integer,db.ForeignKey("services.service_id"),nullable=False)
    rating=db.Column(db.Integer)
    professional_requests=db.relationship("Service_requests",cascade="all,delete",backref="professional",lazy=True)

class Services(db.Model):
    __tablename__="services"
    service_id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String,nullable=False)
    price=db.Column(db.Float,nullable=False)
    description=db.Column(db.String,unique=True,nullable=False)
    time_required=db.Column(db.Integer,nullable=False)
    service_professionals=db.relationship("Professional",cascade="all,delete",backref="services",lazy=True)
    service_service_requests=db.relationship("Service_requests",cascade="all,delete",backref="services",lazy=True)

class Service_requests(db.Model):
    __tablename__="service_requests"
    request_id=db.Column(db.Integer,primary_key=True)
    service_id=db.Column(db.Integer,db.ForeignKey("services.service_id"),nullable=False)
    customer_id=db.Column(db.Integer,db.ForeignKey("customer.customer_id"),nullable=False)
    professional_id=db.Column(db.Integer,db.ForeignKey("professional.professional_id"),nullable=False)
    date_requested=db.Column(db.DateTime,nullable=False)
    date_completed=db.Column(db.DateTime,nullable=False)
    status=db.Column(db.String,default="requested")
    rating=db.Column(db.Integer,nullable=False)
    remarks=db.Column(db.String)  