from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


class User(db.Model, UserMixin):
    id = db.Column(db.BigInteger, db.ForeignKey("employee.id"), nullable=False, primary_key=True)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User({self.id}','{self.password}' )"


class Employee(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    NC = db.Column(db.BigInteger, nullable=False)
    phone = db.Column(db.BigInteger, nullable=False)
    medical = db.Column(db.Integer, db.ForeignKey("medical.id"), nullable=False)

    def __repr__(self):
        return f"Employee({self.id}','{self.name}','{self.last_name}','{self.NC}','{self.phone}' )"


class Sick(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=True)
    last_name = db.Column(db.String(60), nullable=True)
    NC = db.Column(db.BigInteger, nullable=False)
    phone = db.Column(db.BigInteger, nullable=True)

    def __repr__(self):
        return f"Sick('{self.id}','{self.name}','{self.last_name}','{self.NC}','{self.phone}' )"


class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    NC = db.Column(db.BigInteger, nullable=False)
    phone = db.Column(db.BigInteger, nullable=False)
    medical = db.Column(db.Integer, db.ForeignKey("medical.id"), nullable=False)
    specialty = db.Column(db.Integer, db.ForeignKey("specialty.id"), nullable=False)

    def __repr__(self):
        return f"Doctor({self.id}','{self.name}','{self.last_name}','{self.NC}','{self.phone}','{self.specialty}','{self.medical}')"


class Medical(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    address = db.Column(db.String(500), nullable=False)
    phone = db.Column(db.BigInteger, nullable=False)
    city = db.Column(db.Integer, db.ForeignKey("city.id"), nullable=False)

    def __repr__(self):
        return f"Medical('{self.id}','{self.name}','{self.address}','{self.phone}','{self.city}'  )"


class Turn(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sick = db.Column(db.Integer, db.ForeignKey("sick.id"), nullable=False)
    doctor = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False)
    medical = db.Column(db.Integer, db.ForeignKey("medical.id"), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now().strftime("%Y/%m/%d"))
    status = db.Column(db.SmallInteger, nullable=False , default=1)

    def __repr__(self):
        return f"Turn('{self.id}','{self.sick}','{self.doctor}','{self.medical}','{self.date}' ,'{self.status}' )"


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"City('{self.id}','{self.name}')"


class Specialty(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"Specialty('{self.id}','{self.name}')"


class EMMedical(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee = db.Column(db.BigInteger, db.ForeignKey("employee.id"), nullable=False)
    medical = db.Column(db.Integer, db.ForeignKey("medical.id"), nullable=False)

    def __repr__(self):
        return f"Specialty('{self.id}','{self.employee}','{self.medical}')"
