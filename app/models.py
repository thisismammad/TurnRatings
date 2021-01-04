import datetime
from app import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.BigInteger, db.ForeignKey("employee.id"), nullable=False, primary_key=True)
    password = db.Column(db.String(60), nullable=False)
    access_level = db.Column(db.SmallInteger, db.ForeignKey("employee.status"), nullable=False)

    def __repr__(self):
        return f"User({self.id}','{self.password}','{self.access_level}')"


class Employee(db.Model):
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    NC = db.Column(db.BigInteger, nullable=False)
    phone = db.Column(db.BigInteger, nullable=False)
    medical = db.Column(db.Integer, db.ForeignKey("medical.id"), nullable=False)
    position = db.Column(db.SmallInteger, nullable=False)
    status = db.Column(db.SmallInteger, default=1)

    def __eq__(self, other):
        if not isinstance(other, Employee):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.name == other.name and \
               self.last_name == other.last_name and \
               self.NC == other.NC and \
               self.phone == other.phone and \
               self.medical == other.medical and \
               self.position == other.position

    def __repr__(self):
        return f"Employee({self.id}','{self.name}','{self.last_name}','{self.NC}','{self.phone}')"


class Sick(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=True)
    last_name = db.Column(db.String(60), nullable=True)
    NC = db.Column(db.BigInteger, nullable=False)
    phone = db.Column(db.BigInteger, nullable=True)

    def __eq__(self, other):
        if not isinstance(other, Sick):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.name == other.name and \
               self.last_name == other.last_name and \
               self.NC == other.NC and \
               self.phone == other.phone

    def __repr__(self):
        return f"Sick('{self.id}','{self.name}','{self.last_name}','{self.NC}','{self.phone}')"


class Doctor(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    NC = db.Column(db.BigInteger, nullable=False)
    phone = db.Column(db.BigInteger, nullable=False)
    medical = db.Column(db.Integer, db.ForeignKey("medical.id"), nullable=False)
    specialty = db.Column(db.Integer, db.ForeignKey("specialty.id"), nullable=False)
    status = db.Column(db.SmallInteger, default=1)
    daily_capacity = db.Column(db.SmallInteger, nullable=False)

    def __eq__(self, other):
        if not isinstance(other, Doctor):
            # don't attempt to compare against unrelated types
            return NotImplemented

        return self.name == other.name and \
               self.last_name == other.last_name and \
               self.NC == other.NC and \
               self.phone == other.phone and \
               self.medical == other.medical and \
               self.specialty == other.specialty and \
               self.daily_capacity == other.daily_capacity

    def __repr__(self):
        return f"Doctor({self.id}','{self.name}','{self.last_name}','{self.NC}','{self.phone}','{self.specialty}','{self.medical}')"


class Medical(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    address = db.Column(db.String(500), nullable=False)
    phone = db.Column(db.BigInteger, nullable=False)
    city = db.Column(db.Integer, db.ForeignKey("city.id"), nullable=False)
    status = db.Column(db.SmallInteger, default=1)

    def __eq__(self, other):
        if not isinstance(other, Medical):
            # don't attempt to compare against unrelated types
            return NotImplemented
        return self.name.strip() == other.name.strip() and \
               self.address.strip() == other.address.strip() and \
               self.phone == other.phone and \
               self.city == other.city

    def __repr__(self):
        return f"Medical('{self.id}','{self.name}','{self.address}','{self.phone}','{self.city}')"


class Turn(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sick = db.Column(db.Integer, db.ForeignKey("sick.id"), nullable=False)
    doctor = db.Column(db.Integer, db.ForeignKey("doctor.id"), nullable=False)
    medical = db.Column(db.Integer, db.ForeignKey("medical.id"), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.date.today())
    status = db.Column(db.SmallInteger, nullable=False, default=1)

    def __repr__(self):
        return f"Turn('{self.id}','{self.sick}','{self.doctor}','{self.medical}','{self.date}' ,'{self.status}')"


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(200), nullable=False)
    status = db.Column(db.SmallInteger, default=1)

    def __repr__(self):
        return f"City('{self.id}','{self.name}')"


class Specialty(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(500), nullable=False)
    status = db.Column(db.SmallInteger, default=1)

    def __repr__(self):
        return f"Specialty('{self.id}','{self.name}')"
