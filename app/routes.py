from flask import render_template, request, flash, redirect, url_for, session, abort
from app import app
from app.models import *
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, current_user, logout_user, login_required



@app.route('/')
def home():
    if session.get("NC"):
        return redirect(url_for("panel"))
    else:
        return render_template('login.html')


@app.route('/login-page')
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for('admin_login', input='panel'))
    return render_template('admin-login.html')


@app.route('/logout')
def logout():
    logout_user()
    return render_template('admin-login.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_login', input='panel'))
    if not request.form['user'] or not request.form['password']:
        flash('نام کاربری و رمز عبور را وارد کنید', category='danger')
        return redirect(url_for('login_page'))
    else:
        try:
            entry_user = int(request.form['user'])
            login_password = request.form['password']
            user = User.query.filter_by(id=entry_user).first()
            if user:
                if check_password_hash(user.password, login_password):
                    login_user(user)
                    return redirect(url_for('admin_login', input='panel'))
                else:
                    flash('رمز عبور صحیح نیست', category='danger')
                    return redirect(url_for('login_page'))
            else:
                flash('حساب کاربری با این کد پرسنلی یافت نشد', category='danger')
                return redirect(url_for('login_page'))
        except:
            flash('نام کاربری وارد شده صحیح نیست ، نام کاربری کد پرسنلی شما می باشد', category='danger')
            return redirect(url_for('login_page'))


@app.route('/user-panel', methods=['POST', 'GET'])
def panel():
    if request.method == "POST":
        if request.form['NC']:
            try:
                nc = int(request.form['NC'])
                if len(str(nc)) == 10:
                    session["NC"] = nc
                    if not Sick.query.filter_by(NC=nc).first():
                        sick = Sick(NC=nc)
                        db.session.add(sick)
                        db.session.commit()
                    return redirect(url_for("panel"))
                else:
                    flash("کد ملی وارد شده صحیح نیست کد ملی باید دقیقا 10 رقم عددی باشد", category='danger')
            except:
                flash("کد ملی وارد شده صحیح نیست کد ملی باید دقیقا 10 رقم عددی باشد", category='danger')
        else:
            flash("کد ملی را وارد کنید", category='danger')
    elif request.method == "GET":
        if session.get("NC"):
            return render_template('panel.html')
        else:
            session.clear()
            return redirect(url_for('home'))
    return redirect(url_for('home'))


@app.route('/user-turn', methods=['GET'])
def user_turn():
    date = datetime.date.today() + datetime.timedelta(days=+1)
    if session.get("NC"):
        NC = session.get("NC")
        cites = []
        for city in City.query.all():
            if city.status == 1:
                cites.append(city)
        return render_template('turn.html', values=locals())
    else:
        abort(404)


@app.route('/user-report', methods=['GET'])
def user_report():
    turns = []
    if session.get("NC"):
        sick = Sick.query.filter_by(NC=session.get("NC")).first()
        for turn in Turn.query.filter_by(sick=sick.id):
            doctor = Doctor.query.filter_by(id=turn.doctor).first()
            medical = Medical.query.filter_by(id=turn.medical).first()
            specialty = Specialty.query.filter_by(id=doctor.specialty).first()
            city = City.query.filter_by(id=medical.city).first()
            if turn.date.date() < datetime.date.today():
                    turn.status = 3
                    db.session.commit()
            turns.append({"id": turn.id,
                          "sick": session.get("NC"),
                          "speciality": specialty.name,
                          "doctor": doctor.name + '-' + doctor.last_name,
                          "date": turn.date.date(),
                          "medical": city.name + '-' + medical.name,
                          "status": turn.status})
        return render_template('report.html', values=locals())
    else:
        abort(404)


@app.route('/<input>', methods=['GET', 'POST'])
@login_required
def admin_login(input):
    data = []
    if current_user.access_level == 1:
        access_level = current_user.access_level
        if input == 'city':
            data.clear()
            for city in City.query.all():
                if city.status == 1:
                    data.append(city)
            return render_template('admin-' + input + '.html', values=locals())
        elif input == 'speciality':
            data.clear()
            for speciality in Specialty.query.all():
                if speciality.status == 1:
                    data.append(speciality)
            return render_template('admin-' + input + '.html', values=locals())
        elif input == 'doctor':
            data.clear()
            for doctor in Doctor.query.all():
                if doctor.status == 1:
                    medical = Medical.query.filter_by(id=doctor.medical).first()
                    sp = Specialty.query.filter_by(id=doctor.specialty).first()
                    city = City.query.filter_by(id=medical.city).first()
                    data.append({"id": doctor.id,
                                 "name": doctor.name,
                                 "last_name": doctor.last_name,
                                 "NC": doctor.NC,
                                 "phone": '0' + str(doctor.phone),
                                 "medical": medical.name + '-' + city.name,
                                 "speciality": sp.name,
                                 "daily_capacity" : doctor.daily_capacity})
            specialties = []
            for speciality in Specialty.query.all():
                if speciality.status == 1:
                    specialties.append(speciality)

            medicals = []
            for medical in Medical.query.all():
                if medical.status == 1:
                    city = City.query.filter_by(id=medical.city).first()
                    medicals.append({"medical_id": medical.id, "medical_name": medical.name + "-" + city.name})
            return render_template('admin-' + input + '.html', values=locals())
        elif input == 'user':
            data.clear()
            for employee in Employee.query.all():
                if employee.status == 1:
                    medical = Medical.query.filter_by(id=employee.medical).first()
                    if medical:
                        city = City.query.filter_by(id=medical.city).first()
                        data.append({"id": employee.id,
                                     "NC": employee.NC,
                                     "name": employee.name,
                                     "last_name": employee.last_name,
                                     "position": employee.position,
                                     "phone": '0' + str(employee.phone),
                                     "medical": medical.name + "-" + city.name,
                                     })
                    else:
                        data.append({"id": employee.id,
                                     "NC": employee.NC,
                                     "name": employee.name,
                                     "last_name": employee.last_name,
                                     "position": employee.position,
                                     "phone": '0' + str(employee.phone),
                                     "medical": '-',
                                     })
            medicals = []
            for medical in Medical.query.all():
                if medical.status == 1:
                    city = City.query.filter_by(id=medical.city).first()
                    medicals.append({"medical_id": medical.id, "medical_name": medical.name + "-" + city.name})
            return render_template('admin-' + input + '.html', values=locals())
        elif input == 'medical':
            data.clear()
            for medical in Medical.query.all():
                if medical.status == 1:
                    city = City.query.filter_by(id=medical.city).first()
                    data.append({"id": medical.id,
                                 "name": medical.name,
                                 "address": medical.address,
                                 "phone": '0' + str(medical.phone),
                                 "city": city.name,
                                 "status": medical.status})
            cites = []
            for city in City.query.all():
                if city.status == 1:
                    cites.append(city)
            return render_template('admin-' + input + '.html', values=locals())
        elif input == 'reception':
            data.clear()
            for turn in Turn.query.all():
                if turn.date.date() == datetime.date.today():
                    if turn.status == 1:
                        sick = Sick.query.filter_by(id=turn.sick).first()
                        doctor = Doctor.query.filter_by(id=turn.doctor).first()
                        medical = Medical.query.filter_by(id=turn.medical).first()
                        city = City.query.filter_by(id=medical.city).first()
                        specialty = Specialty.query.filter_by(id=doctor.specialty).first()
                        data.append({"id": turn.id,
                                     "sick": sick.NC,
                                     "speciality": specialty.name,
                                     "doctor": doctor.name+'-'+doctor.last_name,
                                     "date": turn.date.date(),
                                     "medical": medical.name + '-' + city.name,
                                     "status": turn.status})
                elif turn.date.date() < datetime.date.today():
                    turn.status = 3
                    db.session.commit()
            return render_template('admin-' + input + '.html', values=locals())
        elif input == 'report':
            specialties = []
            for speciality in Specialty.query.all():
                if speciality.status == 1 and speciality not in specialties:
                    specialties.append(speciality)

            medicals = []
            for medical in Medical.query.all():
                if medical.status == 1:
                    city = City.query.filter_by(id=medical.city).first()
                    medicals.append({"medical_id": medical.id, "medical_name": medical.name + "-" + city.name})

            doctors = []
            for doctor in Doctor.query.all():
                if doctor.status == 1:
                    doctors.append(doctor)

            cities = []
            for city in City.query.all():
                if city.status == 1:
                    cities.append(city)
            return render_template('admin-' + input + '.html', values=locals())
        elif input == 'turn':
            date = datetime.date.today()
            cites = []
            for city in City.query.all():
                if city.status == 1:
                    cites.append(city)
            return render_template('admin-' + input + '.html', values=locals())
        elif input == 'changepassword':
            return render_template('admin-' + input + '.html', values=locals())
        else:
            return render_template('admin-panel.html', values=locals())

    elif current_user.access_level == 2:
        em = Employee.query.filter_by(id=current_user.id).first()
        medical = Medical.query.filter_by(id=em.medical).first()
        access_level = current_user.access_level
        if input == 'user':
            data.clear()
            for employee in Employee.query.filter_by(medical=em.medical):
                if employee.status == 1:
                    data.append({"id": employee.id,
                                 "NC": employee.NC,
                                 "name": employee.name,
                                 "last_name": employee.last_name,
                                 "position": employee.position,
                                 "phone": '0' + str(employee.phone)
                                 })
            return render_template('admin-' + input + '.html', values=locals())
        elif input == 'doctor':
            data.clear()
            for doctor in Doctor.query.filter_by(medical=em.medical):
                if doctor.status == 1:
                    medical = Medical.query.filter_by(id=doctor.medical).first()
                    sp = Specialty.query.filter_by(id=doctor.specialty).first()
                    data.append({"id": doctor.id,
                                 "name": doctor.name,
                                 "last_name": doctor.last_name,
                                 "NC": doctor.NC,
                                 "phone": '0' + str(doctor.phone),
                                 "medical": medical.name,
                                 "speciality": sp.name,
                                 "daily_capacity" : doctor.daily_capacity})
            return render_template('admin-' + input + '.html', values=locals())
        elif input == 'reception':
            data.clear()
            for turn in Turn.query.filter_by(medical=em.medical):
                if turn.date.date() == datetime.date.today():
                    if turn.status == 1:
                        sick = Sick.query.filter_by(id=turn.sick).first()
                        doctor = Doctor.query.filter_by(id=turn.doctor).first()
                        specialty = Specialty.query.filter_by(id=doctor.specialty).first()
                        data.append({"id": turn.id,
                                     "sick": sick.NC,
                                     "speciality": specialty.name,
                                     "doctor": doctor.name+'-'+doctor.last_name,
                                     "date": turn.date.date(),
                                     "status": turn.status})
                elif turn.date.date() < datetime.date.today():
                    turn.status = 3
                    db.session.commit()
            return render_template('admin-' + input + '.html', values=locals())
        elif input == 'report':
            specialties = []
            doctors = []
            medical = Medical.query.filter_by(id=em.medical).first()
            for doctor in Doctor.query.filter_by(medical=medical.id):
                doctors.append(doctor)
                for speciality in Specialty.query.filter_by(id=doctor.specialty):
                    if not speciality in specialties:
                        specialties.append(speciality)
            city = City.query.filter_by(id=medical.city).first()
            return render_template('admin-' + input + '.html', values=locals())
        elif input == 'turn':
            medical = Medical.query.filter_by(id=em.medical).first()
            city = City.query.filter_by(id=medical.city).first()
            date = datetime.date.today()
            specialties = []
            if Doctor.query.filter_by(medical=medical.id):
                for doctor in Doctor.query.filter_by(medical=medical.id):
                    if doctor.daily_capacity > 0:
                        specialty = Specialty.query.filter_by(id=doctor.specialty).first()
                        if specialty.name not in specialties:
                            specialties.append({"sp_name": specialty.name,
                                                "sp_id": specialty.id})
            return render_template('admin-' + input + '.html', values=locals())
        elif input == 'changepassword':
            return render_template('admin-' + input + '.html', values=locals())
        else:
            return render_template('admin-panel.html', values=locals())

    elif current_user.access_level == 3:
        em = Employee.query.filter_by(id=current_user.id).first()
        access_level = current_user.access_level
        if input == 'reception':
            data.clear()
            for turn in Turn.query.filter_by(medical=em.medical):
                if turn.date.date() == datetime.date.today():
                    if turn.status == 1:
                        sick = Sick.query.filter_by(id=turn.sick).first()
                        doctor = Doctor.query.filter_by(id=turn.doctor).first()
                        specialty = Specialty.query.filter_by(id=doctor.specialty).first()
                        data.append({"id": turn.id,
                                     "sick": sick.NC,
                                     "speciality": specialty.name,
                                     "doctor": doctor.name+'-'+doctor.last_name,
                                     "date": turn.date.date(),
                                     "status": turn.status})
                elif turn.date.date() < datetime.date.today():
                    turn.status = 3
                    db.session.commit()
            return render_template('admin-' + input + '.html', values=locals())
        elif input == 'turn':
            medical = Medical.query.filter_by(id=em.medical).first()
            city = City.query.filter_by(id=medical.city).first()
            date = datetime.date.today()
            specialties = []
            if Doctor.query.filter_by(medical=medical.id):
                for doctor in Doctor.query.filter_by(medical=medical.id):
                    if doctor.daily_capacity > 0:
                        specialty = Specialty.query.filter_by(id=doctor.specialty).first()
                        if specialty.name not in specialties:
                            specialties.append({"sp_name": specialty.name,
                                                "sp_id": specialty.id})
            return render_template('admin-' + input + '.html', values=locals())
        elif input == 'changepassword':
            return render_template('admin-' + input + '.html', values=locals())
        else:
            return render_template('admin-panel.html', values=locals())
    else:
        return redirect(url_for('logout'))


@app.route('/add-city', methods=['POST', 'GET'])
@login_required
def add_city():
    if current_user.access_level == 1:
        if request.method == 'POST':
            if not request.form['name']:
                flash('نام شهر را وارد کنید', category='danger')
                return redirect(url_for('admin_login', input='city'))
            else:
                if not any(char.isdigit() for char in request.form['name']):
                    city = City(name=request.form['name'])
                    db.session.add(city)
                    db.session.commit()
                    flash('شهر با موفقت اضافه شد', category='success')
                    return redirect(url_for('admin_login', input='city'))
                else:
                    flash('نام شهر وارد شده صحیح نیست. نام شهر نباید شامل عدد باشد', category='danger')
                    return redirect(url_for('admin_login', input='city'))
        return redirect(url_for('admin_login', input='city'))
    else:
        return redirect(url_for('admin_login', input='panel'))


@app.route('/add-speciality', methods=['GET', 'POST'])
@login_required
def add_speciality():
    if current_user.access_level == 1:
        if request.method == 'POST':
            if not request.form['name']:
                flash('نام تخصص را وارد کنید', category='danger')
                return redirect(url_for('admin_login', input='speciality'))
            else:
                if not any(char.isdigit() for char in request.form['name']):
                    speciality = Specialty(name=request.form['name'])
                    db.session.add(speciality)
                    db.session.commit()
                    flash('تخصص با موفقت اضافه شد', category='success')
                    return redirect(url_for('admin_login', input='speciality'))
                else:
                    flash('نام تخصص وارد شده صحیح نیست. نام تخصص نباید شامل عدد باشد', category='danger')
                    return redirect(url_for('admin_login', input='speciality'))
        return redirect(url_for('admin_login', input='speciality'))
    else:
        return redirect(url_for('admin_login', input='panel'))


@app.route('/add-medical', methods=['GET', 'POST'])
@login_required
def add_medical():
    if current_user.access_level == 1:
        if request.method == 'POST':
            if not request.form['name'] or any(char.isdigit() for char in request.form['name']) \
                    or not request.form['address'] \
                    or not request.form['phone'] \
                    or not request.form['city'] or request.form['city'] == '0':
                flash('پر کردن تمام فیلد ها ضروری است. نام نباید شامل عدد باشد', category='danger')
                return redirect(url_for('admin_login', input='medical'))
            else:
                try:
                    phone = int(request.form['phone'])
                    if len(str(phone)) == 10:
                        medical = Medical(name=request.form['name'],
                                          address=request.form['address'],
                                          phone=phone,
                                          city=request.form['city'])
                        db.session.add(medical)
                        db.session.commit()
                        flash('مرکز درمانی با موفقت اضافه شد', 'success')
                        return redirect(url_for('admin_login', input='medical'))
                    else:
                        flash(
                            'شماره تلفن وارد شده صحیح نیست. شماره را بدون +98 وارد کرده و شماره تلفن ثابت را نیز با 076 '
                            'وارد کنید', category='danger')
                        return redirect(url_for('admin_login', input='medical'))
                except:
                    flash('شماره تلفن وارد شده صحیح نیست. شماره را بدون +98 وارد کرده و شماره تلفن ثابت را نیز با 076'
                          'وارد کنید', category='danger')
                    return redirect(url_for('admin_login', input='medical'))
        return redirect(url_for('admin_login', input='medical'))
    else:
        return redirect(url_for('admin_login', input='panel'))


@app.route('/add-doctor', methods=['GET', 'POST'])
@login_required
def add_doctor():
    if current_user.access_level == 1:
        if request.method == 'POST':
            if not request.form['name'] or any(char.isdigit() for char in request.form['name']) \
                    or not request.form['last_name'] or any(char.isdigit() for char in request.form['last_name']) \
                    or not request.form['NC'] \
                    or not request.form['daily_capacity'] \
                    or not request.form['phone'] \
                    or not request.form['speciality'] or request.form['speciality'] == '0' \
                    or not request.form['medical'] or request.form['medical'] == '0':
                flash('پر کردن تمام فیلد ها ضروری است.', category='danger')
                flash(' نام و نام خانوادگی نباید شامل عدد باشد', category='danger')
                return redirect(url_for('admin_login', input='doctor'))
            else:
                try:
                    NC = int(request.form['NC'])
                    try:
                        phone = int(request.form['phone'])
                        try:
                            daily_capacity = int(request.form['daily_capacity'])
                            if len(str(NC)) == 10:
                                if len(str(phone)) == 10:
                                    if len(str(daily_capacity)) < 20:
                                        doctor = Doctor(name=request.form['name'],
                                                        last_name=request.form['last_name'],
                                                        NC=NC,
                                                        phone=phone,
                                                        specialty=request.form['speciality'],
                                                        medical=request.form['medical'],
                                                        daily_capacity=daily_capacity)
                                        db.session.add(doctor)
                                        db.session.commit()
                                        flash('پزشک با موفقت اضافه شد', 'success')
                                        return redirect(url_for('admin_login', input='doctor'))
                                    else:
                                        flash(
                                            'تعداد نوبت روزانه وارد شده صحیح نیست . تعداد نوبت روزانه وارد باید عدد وکوپتر از 50 باشد',
                                            category='danger')
                                        return redirect(url_for('admin_login', input='doctor'))
                                else:
                                    flash(
                                        'شماره تلفن وارد شده صحیح نیست. شماره را بدون +98 وارد کرده و شماره تلفن ثابت را نیز '
                                        'با 076 '
                                        'وارد کنید', category='danger')
                                    return redirect(url_for('admin_login', input='doctor'))
                            else:
                                flash('کدملی وارد شده صحیح نیست . کدملی باید دقیقا 10 رقم عددی باشد', category='danger')
                                return redirect(url_for('admin_login', input='doctor'))

                        except:
                            flash(
                                'تعداد نوبت روزانه وارد شده صحیح نیست . تعداد نوبت روزانه وارد باید عدد وکوپتر از 50 باشد',
                                category='danger')
                            return redirect(url_for('admin_login', input='doctor'))
                    except:
                        flash(
                            'شماره تلفن وارد شده صحیح نیست. شماره را بدون +98 وارد کرده و شماره تلفن ثابت را نیز با 076 '
                            'وارد کنید', category='danger')
                        return redirect(url_for('admin_login', input='doctor'))

                except:
                    flash('کدملی وارد شده صحیح نیست . کدملی باید دقیقا 10 رقم عددی باشد', category='danger')
                    return redirect(url_for('admin_login', input='doctor'))
        return redirect(url_for('admin_login', input='doctor'))
    else:
        return redirect(url_for('admin_login', input='panel'))


@app.route('/add-user', methods=['GET', 'POST'])
@login_required
def add_user():
    if current_user.access_level == 1 or current_user.access_level == 2:
        if request.method == 'POST':
            if not request.form['id'] \
                    or not request.form['name'] or any(char.isdigit() for char in request.form['name']) \
                    or not request.form['last_name'] or any(char.isdigit() for char in request.form['last_name']) \
                    or not request.form['NC'] \
                    or not request.form['phone'] \
                    or not request.form['position'] or request.form['position'] == '0':
                flash('پر کردن تمام فیلد ها ضروری است.', category='danger')
                flash(' نام و نام خانوادگی نباید شامل عدد باشد', category='danger')
                return redirect(url_for('admin_login', input='user'))
            else:
                if current_user.access_level == 2:
                    if int(request.form['position']) == 1:
                        return redirect(url_for('admin_login', input='panel'))
                try:
                    user_id = int(request.form['id'])
                    try:
                        NC = int(request.form['NC'])
                        try:
                            phone = int(request.form['phone'])
                            if len(str(user_id)) == 10:
                                if len(str(NC)) == 10:
                                    if len(str(phone)) == 10:
                                        print(request.form['medical'])
                                        if request.form["position"] == '2' or request.form["position"] == '3':
                                            if request.form['medical'] != '0':
                                                employee = Employee(id=user_id,
                                                                    NC=NC,
                                                                    name=request.form['name'],
                                                                    last_name=request.form['last_name'],
                                                                    phone=phone,
                                                                    position=int(request.form['position']),
                                                                    medical=int(request.form['medical']))
                                            else:
                                                flash(
                                                    'انتخاب مرکز درمانی برای مدیر و کارمندان مراکز درمانی الزامی است.',
                                                    category='danger')
                                                return redirect(url_for('admin_login', input='user'))
                                        elif request.form["position"] == '1':
                                            employee = Employee(id=user_id,
                                                                NC=NC,
                                                                name=request.form['name'],
                                                                last_name=request.form['last_name'],
                                                                phone=phone,
                                                                position=int(request.form['position']))
                                        user = User(id=employee.id,
                                                    password=generate_password_hash(str(employee.NC)),
                                                    access_level=employee.position)
                                        if Employee.query.filter_by(id=int(user_id)).first():
                                            new_employee = Employee.query.filter_by(id=int(user_id)).first()
                                            print(new_employee)
                                            if request.form["position"] == '2' or request.form["position"] == '3':
                                                if request.form['medical'] != '0':
                                                    new_employee.name = request.form["name"]
                                                    new_employee.last_name = request.form["last_name"]
                                                    new_employee.NC = NC
                                                    new_employee.phone = phone
                                                    new_employee.medical = int(request.form["medical"])
                                                    new_employee.position = int(request.form["position"])
                                                    new_employee.status = 1
                                                else:
                                                    flash(
                                                        'انتخاب مرکز درمانی برای مدیر و کارمندان مراکز درمانی الزامی است.',
                                                        category='danger')
                                                    return redirect(url_for('admin_login', input='user'))
                                            elif request.form["position"] == '1':
                                                new_employee.name = request.form["name"]
                                                new_employee.last_name = request.form["last_name"]
                                                new_employee.NC = NC
                                                new_employee.phone = phone
                                                new_employee.medical = "null"
                                                new_employee.position = int(request.form["position"])
                                                new_employee.status = 1
                                        else:
                                            db.session.add(employee)

                                        db.session.add(user)
                                        db.session.commit()
                                        flash('کارمند با موفقت اضافه شد', 'success')
                                        return redirect(url_for('admin_login', input='user'))
                                    else:
                                        flash(
                                            'شماره تلفن وارد شده صحیح نیست. شماره را بدون +98 وارد کرده و شماره تلفن ثابت را نیز '
                                            'با 076 '
                                            'وارد کنید', category='danger')
                                        return redirect(url_for('admin_login', input='user'))
                                else:
                                    flash('کدملی وارد شده صحیح نیست . کدملی باید دقیقا 10 رقم عددی باشد',
                                          category='danger')
                                    return redirect(url_for('admin_login', input='user'))
                            else:
                                flash('کدپرسنلی وارد شده صحیح نیست . کدپرسنلی باید دقیقا 10 رقم عددی باشد',
                                      category='danger')
                                return redirect(url_for('admin_login', input='user'))
                        except:
                            flash(
                                'شماره تلفن وارد شده صحیح نیست. شماره را بدون +98 وارد کرده و شماره تلفن ثابت را نیز با 076 '
                                'وارد کنید', category='danger')
                            return redirect(url_for('admin_login', input='user'))

                    except:
                        flash('کدملی وارد شده صحیح نیست . کدملی باید دقیقا 10 رقم عددی باشد', category='danger')
                        return redirect(url_for('admin_login', input='user'))
                except:
                    flash('کدپرسنلی وارد شده صحیح نیست . کدپرسنلی باید دقیقا 10 رقم عددی باشد', category='danger')
                    return redirect(url_for('admin_login', input='user'))
        return redirect(url_for('admin_login', input='user'))
    else:
        return redirect(url_for('admin_login', input='panel'))


@app.route('/add-turn', methods=['POST'])
def add_turn():
    if request.method == 'POST':
        if not request.form['phone'] \
                or not request.form['city'] or request.form['city'] == '0' \
                or not request.form['medical'] or request.form['medical'] == '0' \
                or not request.form['speciality'] or request.form['speciality'] == '0' \
                or not request.form['doctor'] or request.form['doctor'] == '0':
            flash('پر کردن تمام فیلد ها ضروری است', category='danger')
            return redirect(url_for('user_turn'))
        else:
            try:
                if session.get("NC"):
                    phone = int(request.form['phone'])
                    if len(str(phone)) == 10:
                        doctor = Doctor.query.filter_by(id=int(request.form['doctor'])).first()
                        if doctor.daily_capacity > 0:
                            sick = Sick.query.filter_by(NC=session.get("NC")).first()
                            turn = Turn(sick=sick.id,
                                        doctor=doctor.id,
                                        medical=int(request.form['medical']))

                            sick.phone = phone
                            db.session.add(turn)
                            doctor.daily_capacity = doctor.daily_capacity - 1
                            db.session.commit()
                            flash('نوبت با موفقت ثبت شد', category='success')
                            flash('میتوانید از صفحه پیگیری نویت ، نوبت های خود را پیگیری کنید', category='success')
                            return redirect(url_for('panel'))
                        else:
                            flash('تعداد نوبت روزانه پزشک موردنظر به پایان رسیده است', category='danger')
                            return redirect(url_for('user_turn'))
                    else:
                        flash(
                            'شماره تلفن وارد شده صحیح نیست. شماره را بدون +98 وارد کرده و شماره تلفن ثابت را نیز با 076 '
                            'وارد کنید', category='danger')
                        return redirect(url_for('user_turn'))
                else:
                    abort(404)

            except:
                flash('شماره تلفن وارد شده صحیح نیست. شماره را بدون +98 وارد کرده و شماره تلفن ثابت را نیز با 076 '
                      'وارد کنید', category='danger')
            return redirect(url_for('user_turn'))

    return redirect(url_for('user_turn'))


@app.route('/load-medicals', methods=['POST'])
def load_medicals():
    city = request.form.get('city_id')
    medicals = []
    if Medical.query.filter_by(city=int(city)):
        for medical in Medical.query.filter_by(city=int(city)):
            medicals.append({"medical_name": medical.name,
                             "medical_id": medical.id})
    return {"medicals": medicals}


@app.route('/load-specialties', methods=['GET', 'POST'])
def load_specialties():
    medical_id = int(request.form.get('medical_id'))
    specialties = []
    if Doctor.query.filter_by(medical=medical_id):
        for doctor in Doctor.query.filter_by(medical=medical_id):
            if doctor.daily_capacity > 0:
                specialty = Specialty.query.filter_by(id=doctor.specialty).first()
                if specialty.name not in specialties:
                    specialties.append({"sp_name": specialty.name,
                                        "sp_id": specialty.id})
    return {"specialties": specialties}


@app.route('/load-doctors', methods=['GET', 'POST'])
def load_doctors():
    sp_id = int(request.form.get('sp_id'))
    medical_id = int(request.form.get('medical_id'))
    doctors = []
    if Doctor.query.filter_by(medical=medical_id):
        for doctor in Doctor.query.filter_by(medical=medical_id):
            if doctor.specialty == sp_id and doctor.daily_capacity > 0:
                doctors.append({"doctor_name": doctor.name + "-" + doctor.last_name,
                                "doctor_id": doctor.id})
    return {"doctors": doctors}


@app.route('/delete-medical/<medical_id>', methods=['POST'])
@login_required
def delete_medical(medical_id):
    if current_user.access_level == 1:
        if request.method == "POST":
            medical = Medical.query.filter_by(id=int(medical_id)).first()
            for employee in Employee.query.filter_by(medical=medical.id):
                employee.status = 0
                User.query.filter_by(id=int(employee.id)).delete()
            for doctor in Doctor.query.filter_by(medical=medical.id):
                doctor.status = 0
            medical.status = 0
            db.session.commit()
            flash('مرکز درمانی با موفقیت حذف شد', category='success')
            return redirect(url_for("admin_login", input="medical"))
        return redirect(url_for("admin_login", input="medical"))
    else:
        return redirect(url_for('admin_login', input='panel'))


@app.route('/edit-medical/<medical_id>', methods=['POST'])
@login_required
def edit_medical(medical_id):
    if current_user.access_level == 1:
        if request.method == "POST":
            if not request.form["new_name"] \
                    or not request.form["new_phone"] \
                    or not request.form["new_city"] \
                    or not request.form["new_address"]:
                flash('پر کردن تمام فیلد ها ضروری است.', category='danger')
                flash(' نام نباید شامل عدد باشد', category='danger')
                return redirect(url_for('admin_login', input='medical'))
            else:
                try:
                    new_phone = int(request.form["new_phone"])
                    if len(str(new_phone)) == 10:
                        new_medical = Medical.query.filter_by(id=int(medical_id)).first()
                        comparison_medical = Medical(id=new_medical.id,
                                                     name=request.form['new_name'].strip(),
                                                     address=request.form['new_address'].strip(),
                                                     phone=new_phone,
                                                     city=request.form['new_city'])
                        if not new_medical == comparison_medical:
                            new_medical.name = request.form["new_name"]
                            new_medical.phone = new_phone
                            new_medical.city = int(request.form["new_city"])
                            new_medical.address = request.form["new_address"]
                            db.session.commit()
                            flash('اطلاعات جدید موفقیت ثبت شد', category='success')
                            return redirect(url_for('admin_login', input='medical'))

                    else:
                        flash(
                            'شماره تلفن وارد شده صحیح نیست. شماره را بدون +98 وارد کرده و شماره تلفن ثابت را نیز '
                            'با 076 '
                            'وارد کنید', category='danger')
                        return redirect(url_for("admin_login", input="medical"))
                except:
                    flash(
                        'شماره تلفن وارد شده صحیح نیست. شماره را بدون +98 وارد کرده و شماره تلفن ثابت را نیز '
                        'با 076 '
                        'وارد کنید', category='danger')
                    return redirect(url_for("admin_login", input="medical"))
        return redirect(url_for("admin_login", input="medical"))
    else:
        return redirect(url_for('admin_login', input='panel'))


@app.route('/delete-city/<city_id>', methods=['POST'])
@login_required
def delete_city(city_id):
    if current_user.access_level == 1:
        if request.method == "POST":
            city = City.query.filter_by(id=int(city_id)).first()
            for medical in Medical.query.filter_by(city=city.id):
                medical.status = 0
                for employee in Employee.query.filter_by(medical=medical.id):
                    employee.status = 0
                    User.query.filter_by(id=int(employee.id)).delete()
                for doctor in Doctor.query.filter_by(medical=medical.id):
                    doctor.status = 0
            city.status = 0
            db.session.commit()
            flash('شهر با موفقیت حذف شد', category='success')
            return redirect(url_for("admin_login", input="city"))
        return redirect(url_for("admin_login", input="city"))
    else:
        return redirect(url_for('admin_login', input='panel'))


@app.route('/edit-city/<city_id>', methods=['POST'])
@login_required
def edit_city(city_id):
    if current_user.access_level == 1:
        if request.method == "POST":
            if not request.form["new_name"] or any(char.isdigit() for char in request.form['new_name']):
                flash('پرکردن فیلد نام شهر الزامی است و نام شهر نباید شامل عدد باشد', category='danger')
                return redirect(url_for("admin_login", input="city"))
            else:
                new_city = City.query.filter_by(id=int(city_id)).first()
                if not new_city.name == request.form["new_name"]:
                    new_city.name = request.form["new_name"]
                    db.session.commit()
                    flash('اطلاعات جدید با موفقیت ثیت شد', category='success')
                    return redirect(url_for("admin_login", input="city"))
                else:
                    return redirect(url_for("admin_login", input="city"))
        return redirect(url_for("admin_login", input="city"))
    else:
        return redirect(url_for('admin_login', input='panel'))


@app.route('/delete-speciality/<speciality_id>', methods=['POST'])
@login_required
def delete_speciality(speciality_id):
    if current_user.access_level == 1:
        if request.method == "POST":
            speciality = Specialty.query.filter_by(id=int(speciality_id)).first()
            speciality.status = 0
            for doctor in Doctor.query.filter_by(specialty=speciality.id):
                doctor.status = 0
            db.session.commit()
            flash('تخصص با موفقیت حذف شد', category='success')
            return redirect(url_for("admin_login", input="speciality"))
        return redirect(url_for("admin_login", input="speciality"))
    else:
        return redirect(url_for('admin_login', input='panel'))


@app.route('/edit-speciality/<speciality_id>', methods=['POST'])
@login_required
def edit_speciality(speciality_id):
    if current_user.access_level == 1:
        if request.method == "POST":
            if not request.form["new_name"] or any(char.isdigit() for char in request.form['new_name']):
                flash('پرکردن نام فیلد تخصص الزامی است و نام تخصص نباید شامل عدد باشد', category='danger')
                return redirect(url_for("admin_login", input="speciality"))
            else:
                new_speciality = Specialty.query.filter_by(id=int(speciality_id)).first()
                if not new_speciality.name == request.form["new_name"]:
                    new_speciality.name = request.form["new_name"]
                    db.session.commit()
                    flash('اطلاعات جدید با موفقیت ثیت شد', category='success')
                    return redirect(url_for("admin_login", input="speciality"))
                else:
                    return redirect(url_for("admin_login", input="speciality"))
        return redirect(url_for("admin_login", input="speciality"))
    else:
        return redirect(url_for('admin_login', input='panel'))


@app.route('/delete-doctor/<doctor_id>', methods=['POST'])
@login_required
def delete_doctor(doctor_id):
    if current_user.access_level == 1:
        if request.method == "POST":
            doctor = Doctor.query.filter_by(id=int(doctor_id)).first()
            doctor.status = 0
            db.session.commit()
            return redirect(url_for("admin_login", input="doctor"))
        return redirect(url_for("admin_login", input="doctor"))
    else:
        return redirect(url_for('admin_login', input='panel'))


@app.route('/edit-doctor/<doctor_id>', methods=['POST'])
@login_required
def edit_doctor(doctor_id):
    if current_user.access_level == 1:
        if request.method == 'POST':
            if not request.form['new_name'] or any(char.isdigit() for char in request.form['new_name']) \
                    or not request.form['new_last_name'] or any(
                char.isdigit() for char in request.form['new_last_name']) \
                    or not request.form['new_NC'] \
                    or not request.form['new_phone'] \
                    or not request.form['new_daily_capacity'] \
                    or not request.form['new_specialty'] \
                    or not request.form['new_medical']:
                flash('پر کردن تمام فیلد ها ضروری است.', category='danger')
                flash(' نام و نام خانوادگی نباید شامل عدد باشد', category='danger')
                return redirect(url_for('admin_login', input='doctor'))
            else:
                try:
                    NC = int(request.form['new_NC'])
                    try:
                        phone = int(request.form['new_phone'])
                        if len(str(NC)) == 10:
                            if len(str(phone)) == 10:
                                new_daily_capacity = int(request.form['new_daily_capacity'])
                                print(new_daily_capacity)
                                new_doctor = Doctor.query.filter_by(id=int(doctor_id)).first()
                                comparison_doctor = Doctor(id=int(doctor_id),
                                                           name=request.form['new_name'],
                                                           last_name=request.form['new_last_name'],
                                                           NC=NC,
                                                           phone=phone,
                                                           specialty=request.form['new_medical'],
                                                           daily_capacity=new_daily_capacity,
                                                           medical=request.form['new_specialty'])
                                if not new_doctor == comparison_doctor:
                                    new_doctor.name = request.form["new_name"]
                                    new_doctor.last_name = request.form["new_last_name"]
                                    new_doctor.NC = NC
                                    new_doctor.phone = phone
                                    new_doctor.medical = int(request.form["new_medical"])
                                    new_doctor.specialty = int(request.form["new_specialty"])
                                    new_doctor.daily_capacity=new_daily_capacity
                                    db.session.commit()
                                    flash('اطلاعات با موفقیت ثبت شد', 'success')
                                    return redirect(url_for('admin_login', input='doctor'))
                            else:
                                flash(
                                    'شماره تلفن وارد شده صحیح نیست. شماره را بدون +98 وارد کرده و شماره تلفن ثابت را نیز '
                                    'با 076 '
                                    'وارد کنید', category='danger')
                                return redirect(url_for('admin_login', input='doctor'))
                        else:
                            flash('کدملی وارد شده صحیح نیست . کدملی باید دقیقا 10 رقم عددی باشد', category='danger')
                            return redirect(url_for('admin_login', input='doctor'))
                    except:
                        flash(
                            'شماره تلفن وارد شده صحیح نیست. شماره را بدون +98 وارد کرده و شماره تلفن ثابت را نیز با 076 '
                            'وارد کنید', category='danger')
                        return redirect(url_for('admin_login', input='doctor'))
                except:
                    flash('کدملی وارد شده صحیح نیست . کدملی باید دقیقا 10 رقم عددی باشد', category='danger')
                    return redirect(url_for('admin_login', input='doctor'))
        return redirect(url_for('admin_login', input='doctor'))
    else:
        return redirect(url_for('admin_login', input='panel'))


@app.route('/delete-user/<user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if current_user.access_level == 1 or current_user.access_level == 2:
        if request.method == "POST":
            employee = Employee.query.filter_by(id=int(user_id)).first()
            employee.status = 0
            User.query.filter_by(id=int(user_id)).delete()
            db.session.commit()
            flash('کارمند با موفقیت حذف شد', category='success')
            return redirect(url_for("admin_login", input="user"))
        return redirect(url_for("admin_login", input="user"))
    else:
        return redirect(url_for('admin_login', input='panel'))


@app.route('/edit-user/<user_id>', methods=['POST'])
@login_required
def edit_user(user_id):
    if current_user.access_level == 1 or current_user.access_level == 2:
        if request.method == 'POST':
            if not request.form['new_name'] or any(char.isdigit() for char in request.form['new_name']) \
                    or not request.form['new_last_name'] or any(
                char.isdigit() for char in request.form['new_last_name']) \
                    or not request.form['new_NC'] \
                    or not request.form['new_phone'] \
                    or not request.form['new_position']:
                flash('پر کردن تمام فیلد ها ضروری است.', category='danger')
                flash(' نام و نام خانوادگی نباید شامل عدد باشد', category='danger')
                return redirect(url_for('admin_login', input='user'))
            else:
                if current_user.access_level == 2:
                    if int(request.form['new_position']) == 1:
                        return redirect(url_for('admin_login', input='panel'))
                try:
                    NC = int(request.form['new_NC'])
                    try:
                        phone = int(request.form['new_phone'])
                        if len(str(NC)) == 10:
                            if len(str(phone)) == 10:
                                new_employee = Employee.query.filter_by(id=int(user_id)).first()
                                if request.form["new_position"] == '2' or request.form["new_position"] == '3':
                                    if request.form['new_medical'] != "0":
                                        comparison_employee = Employee(id=user_id,
                                                                       NC=NC,
                                                                       name=request.form['new_name'],
                                                                       last_name=request.form['new_last_name'],
                                                                       phone=phone,
                                                                       position=int(request.form['new_position']),
                                                                       medical=request.form['new_medical'])
                                        if not new_employee == comparison_employee:
                                            new_employee.name = request.form["new_name"]
                                            new_employee.last_name = request.form["new_last_name"]
                                            new_employee.NC = int(request.form["new_NC"])
                                            new_employee.phone = int(request.form["new_phone"])
                                            new_employee.medical = int(request.form["new_medical"])
                                            new_employee.position = int(request.form["new_position"])
                                            User.query.filter_by(
                                                id=new_employee.id).first().access_level = new_employee.position
                                            db.session.commit()
                                            flash('اطلاعات جدید با موفقیت ثبت شد', 'success')
                                            return redirect(url_for('admin_login', input='user'))
                                    else:
                                        flash('انتخاب مرکز درمانی برای مدیر و کارمندان مراکز درمانی الزامی است.',
                                              category='danger')
                                        return redirect(url_for('admin_login', input='user'))
                                elif request.form["new_position"] == '1':
                                    comparison_employee = Employee(id=user_id,
                                                                   NC=NC,
                                                                   name=request.form['new_name'],
                                                                   last_name=request.form['new_last_name'],
                                                                   phone=phone,
                                                                   position=int(request.form['new_position']),
                                                                   medical="null")
                                    if not new_employee == comparison_employee:
                                        new_employee.name = request.form["new_name"]
                                        new_employee.last_name = request.form["new_last_name"]
                                        new_employee.NC = int(request.form["new_NC"])
                                        new_employee.phone = int(request.form["new_phone"])
                                        new_employee.position = int(request.form["new_position"])
                                        new_employee.medical = "null"
                                        User.query.filter_by(
                                            id=new_employee.id).first().access_level = new_employee.position
                                        db.session.commit()
                                        flash('اطلاعات جدید با موفقیت ثبت شد', 'success')

                                        return redirect(url_for('admin_login', input='user'))
                            else:
                                flash(
                                    'شماره تلفن وارد شده صحیح نیست. شماره را بدون +98 وارد کرده و شماره تلفن ثابت را نیز '
                                    'با 076 '
                                    'وارد کنید', category='danger')
                                return redirect(url_for('admin_login', input='user'))
                        else:
                            flash('کدملی وارد شده صحیح نیست . کدملی باید دقیقا 10 رقم عددی باشد', category='danger')
                            return redirect(url_for('admin_login', input='user'))
                    except:
                        flash(
                            'شماره تلفن وارد شده صحیح نیست. شماره را بدون +98 وارد کرده و شماره تلفن ثابت را نیز با 076 '
                            'وارد کنید', category='danger')
                        return redirect(url_for('admin_login', input='user'))
                except:
                    flash('کدملی وارد شده صحیح نیست . کدملی باید دقیقا 10 رقم عددی باشد', category='danger')
                    return redirect(url_for('admin_login', input='user'))
        return redirect(url_for('admin_login', input='user'))
    else:
        return redirect(url_for('admin_login', input='panel'))


@app.route('/change-password/', methods=['POST'])
@login_required
def change_password():
    if request.method == "POST":
        if request.form["old_password"] \
                and request.form["new_password"] \
                and request.form["confirm_password"]:
            if check_password_hash(current_user.password, request.form["old_password"]):
                if len(request.form["new_password"]) >= 8:
                    if request.form["new_password"] == request.form["confirm_password"]:
                        current_user.password = generate_password_hash(request.form["new_password"])
                        db.session.commit()
                        flash('رمز عبور با موفقیت تغییر کرد', category='success')
                        return redirect(url_for("admin_login", input="changepassword"))
                    else:
                        flash('رمز عبور جدید و تکرار آن یکی نیست', category='danger')
                        return redirect(url_for("admin_login", input="changepassword"))
                else:
                    flash('رمز عبور باید حداقل 8 کاراکتر باشد ', category='danger')
                    return redirect(url_for("admin_login", input="changepassword"))

            else:
                flash('رمز عبور قدیمی وارد شده صحیح نیست', category='danger')
                return redirect(url_for("admin_login", input="changepassword"))
    return redirect(url_for("admin_login", input="changepassword"))


@app.route('/reset-password/<user_id>', methods=['GET'])
@login_required
def reset_password(user_id):
    if current_user.access_level == 1 or current_user.access_level == 2:
        if request.method == "GET":
            employee = Employee.query.filter_by(id=int(user_id)).first()
            user = User.query.filter_by(id=employee.id).first()
            user.password = generate_password_hash(str(employee.NC))
            db.session.commit()
            flash('رمز عبور به کدملی کارمند تغییر یافت', category="success")
            return redirect(url_for("admin_login", input="user"))
        return redirect(url_for("admin_login", input="user"))
    else:
        return redirect(url_for('admin_login', input='panel'))


@app.route('/reception/<turn_id>', methods=['POST', 'GET'])
@login_required
def reception(turn_id):
    if current_user.access_level == 1 or current_user.access_level == 2 or current_user.access_level == 3:
        turn = Turn.query.filter_by(id=int(turn_id)).first()
        turn.status = 2
        db.session.commit()
        flash('پذیرش بیمار انجام شد', category='success')
        return redirect(url_for("admin_login", input="reception"))
    else:
        return redirect(url_for('admin_login', input='panel'))


@app.route('/cancel-turn', methods=['POST', 'GET'])
def cancel_turn():
    turn = Turn.query.filter_by(id=int(request.form["turn_id"])).first()
    if session.get("NC"):
        if turn.person.NC == session.get("NC"):
            if turn.status != 0:
                turn.status = 0
                db.session.commit()
                flash('نوبت باموفقت لغو شد', category='success')
        else:
            flash('دسترسی غیر مجاز', category='danger')
        return redirect(url_for("user_report"))

    else:
        abort(404)


@app.route('/search-sick', methods=['POST', 'GET'])
@login_required
def search_sick():
    data = []
    access_level = current_user.access_level
    sick = Sick.query.filter_by(NC=int(request.form["sick_NC"])).first()
    if sick:
        is_search = True
        for turn in Turn.query.filter_by(sick=sick.id):
            doctor = Doctor.query.filter_by(id=turn.doctor).first()
            medical = Medical.query.filter_by(id=turn.medical).first()
            city = City.query.filter_by(id=medical.city).first()
            if current_user.access_level == 2 or current_user.access_level == 3:
                em = Employee.query.filter_by(id=current_user.id).first()
                if em.medical == medical.id:
                    specialty = Specialty.query.filter_by(id=doctor.specialty).first()
                    data.append({"id": turn.id,
                                 "sick": sick.NC,
                                 "speciality": specialty.name,
                                 "doctor": doctor.name + '-' + doctor.last_name,
                                 "date": turn.date.date(),
                                 "medical": medical.name + '-' + city.name,
                                 "status": turn.status})
            else:
                specialty = Specialty.query.filter_by(id=doctor.specialty).first()
                data.append({"id": turn.id,
                             "sick": sick.NC,
                             "speciality": specialty.name,
                             "doctor": doctor.name + '-' + doctor.last_name,
                             "date": turn.date.date(),
                             "medical": medical.name + '-' + city.name,
                             "status": turn.status})
    else:
        flash('بیمار با این کد ملی در سیستم وجود ندارد', category='danger')
        return redirect(url_for('admin_login', input="reception"))
    return render_template('admin-reception.html', values=locals())


@app.route('/edit-sick/<sick_id>', methods=['POST'])
@login_required
def edit_sick(sick_id):
    if request.method == "POST":
        if not request.form["new_name"] or any(char.isdigit() for char in request.form['new_name']) \
                or not request.form["new_last_name"] or any(char.isdigit() for char in request.form['new_last_name']) \
                or not request.form["new_NC"] \
                or not request.form["new_phone"]:
            flash('پر کردن تمام فیلد ها الزامی است ', category='danger')
            flash('نام و نام خانوادگی نباید شامل عدد باشد', category='danger')
            return redirect(url_for("admin_login", input="reception"))
        else:
            try:
                new_NC = int(request.form["new_NC"])
                try:
                    new_phone = int(request.form["new_phone"])
                    if len(str(new_NC)) == 10:
                        if len(str(new_phone)) == 10:
                            new_sick = Sick.query.filter_by(id=int(sick_id)).first()
                            comparison_sick = Sick(id=new_sick.id,
                                                   name=request.form["new_name"],
                                                   last_name=request.form["new_last_name"],
                                                   phone=new_phone,
                                                   NC=new_NC)
                            if not new_sick == comparison_sick:
                                new_sick.name = request.form["new_name"]
                                new_sick.last_name = request.form["new_last_name"]
                                new_sick.NC = new_NC
                                new_sick.phone = new_phone
                                db.session.commit()
                                is_search = False
                                flash('اطلاعات بیمار بروزرسانی شد', category='success')
                                return redirect(url_for("admin_login", input="reception"))
                        else:
                            flash(
                                'شماره تلفن وارد شده صحیح نیست. شماره را بدون +98 وارد کرده و شماره تلفن ثابت را نیز با 076 '
                                'وارد کنید', category='danger')
                            return redirect(url_for("admin_login", input="reception"))
                    else:
                        flash('کد ملی باید دقیقا 10 رقم عددی باشد', category='danger')
                        return redirect(url_for("admin_login", input="reception"))
                except:
                    flash(
                        'شماره تلفن وارد شده صحیح نیست. شماره را بدون +98 وارد کرده و شماره تلفن ثابت را نیز با 076 '
                        'وارد کنید', category='danger')
                    return redirect(url_for("admin_login", input="reception"))
            except:
                flash('کد ملی باید دقیقا 10 رقم عددی باشد', category='danger')
                return redirect(url_for("admin_login", input="reception"))
    return redirect(url_for("admin_login", input="reception"))


@app.route('/reporting', methods=['POST'])
@login_required
def reporting():
    if current_user.access_level == 1 or current_user.access_level == 2:
        access_level = current_user.access_level
        
        if request.method == "POST":
            error_message = ""
            if not request.form["start_date"] or not request.form["end_date"]:
                error_message = "انتخاب تاریخ شروع و پایان الزامی است"
                return {"message":error_message}
            else:
                data = []
                s_date = str(request.form["start_date"]).split('-')
                e_date = str(request.form["end_date"]).split('-')
                send_start_date = s_date[0] + '-' + s_date[1] + '-' + s_date[2]
                send_end_date = e_date[0] + '-' + e_date[1] + '-' + e_date[2]
                start_date = datetime.datetime(int(s_date[0]), int(s_date[1]), int(s_date[2]))
                end_date = datetime.datetime(int(e_date[0]), int(e_date[1]), int(e_date[2]))

                if start_date > end_date:
                    error_message = "تاریخ شروع باید کوچکتر از تاریخ پایان باشد"
                    return {"message":error_message}

                city_id = int(request.form["city"])
                medical_id = int(request.form["medical"])
                speciality_id = int(request.form["speciality"])
                doctor_id = int(request.form["doctor"])
                filter_by = {}
                filter_by = {"city": city_id, "medical": medical_id, "sp": speciality_id, "doctor": doctor_id}
                for i in filter_by.copy():
                    if not filter_by[i]:
                        del filter_by[i]
                select_sp = False
                result = Turn.query.filter(Turn.date >= start_date, Turn.date <= end_date)
                for k, v in filter_by.items():
                    if k == "city":
                        result = result.join(Medical).join(City).filter(City.id == city_id)
                        print("---city---")
                        print(result)
                    if k == "medical":
                        result = result.filter(Turn.medical == medical_id)
                        print("---medical---")
                        print(result)
                    if k == "doctor":
                        result = result.filter(Turn.doctor == doctor_id)
                        print("---doctor---")
                        print(result)
                    if k == "sp":
                        result = result.join(Doctor, Turn.doctor == Doctor.id).join(Specialty, Doctor.specialty == Specialty.id).filter(Specialty.id == speciality_id)
                        select_sp = True
                        print("---sp---")
                        print(result)


                for turn in result.all():
                    sick = Sick.query.filter_by(id=turn.sick).first()
                    if not sick.name:
                        sick.name = '-'
                        sick.last_name = ''
                    doctor = Doctor.query.filter_by(id=turn.doctor).first()
                    sp = Specialty.query.filter_by(id=doctor.specialty).first()
                    medical = Medical.query.filter_by(id=turn.medical).first()
                    city = City.query.filter_by(id=medical.city).first()
                    status = ''
                    if turn.status == 0:
                        status = 'لغو شده'
                    elif turn.status == 1:
                        status = 'انتظار'
                    elif turn.status == 2:
                        status = 'انجام شده'
                    elif turn.status == 3:
                        status = 'منقضی شده'
                    data.append({"sick_NC": sick.NC,
                                 "sick_name": sick.name + ' ' + sick.last_name,
                                 "doctor": doctor.name + ' ' + doctor.last_name + '-' + sp.name,
                                 "medical": medical.name + '-' + city.name,
                                 "date": turn.date.date(),
                                 "status": status})
            print(error_message)
            return {"data":data, "message":error_message}
        return redirect(url_for('admin_login', input='report'))
    else:
        return redirect(url_for('admin_login', input='panel'))



@app.route('/load-data-for-report', methods=['GET', 'POST'])
@login_required
def load_data_for_report():
    if current_user.access_level == 1 or current_user.access_level == 2:
        cities = []
        medicals = []
        specialties = []
        doctors = []
        for doctor in Doctor.query.all():
            doctors.append({"doctor_id": doctor.id,
                            "doctor_name": doctor.name,
                            "doctor_last_name": doctor.last_name,
                            "doctor_medical": doctor.medical,
                            "doctor_sp": doctor.specialty})

        for medical in Medical.query.all():
            city = City.query.filter_by(id=medical.city).first()
            medicals.append({"medical_id": medical.id,
                             "medical_name": medical.name + "-" + city.name,
                             "medical_city": medical.city})
        for sp in Specialty.query.all():
            specialties.append({"sp_name": sp.name,
                                "sp_id": sp.id})
        for city in City.query.all():
            cities.append({"city_name": city.name,
                           "city_id": city.id})
        return {"cities": cities, "medicals": medicals, "specialties": specialties, "doctors": doctors}
    else:
        return redirect(url_for('admin_login', input='panel'))


@app.route('/add-turn-user', methods=['POST'])
@login_required
def add_turn_user():
    if request.method == 'POST':
        if not request.form['NC'] \
                or not request.form['name'] \
                or not request.form['last_name'] \
                or not request.form['phone'] \
                or not request.form['city'] or request.form['city'] == '0' \
                or not request.form['medical'] or request.form['medical'] == '0' \
                or not request.form['speciality'] or request.form['speciality'] == '0' \
                or not request.form['doctor'] or request.form['doctor'] == '0':
            flash('پر کردن تمام فیلد ها ضروری است', category='danger')
            return redirect(url_for('user_turn_user'))
        else:
            try:
                NC = int(request.form['NC'])
                try:
                    phone = int(request.form['phone'])
                    if len(str(NC)) == 10:
                        if len(str(phone)) == 10:
                            doctor = Doctor.query.filter_by(id=int(request.form['doctor'])).first()
                            if doctor.daily_capacity > 0:
                                sick = Sick.query.filter_by(NC=NC).first()
                                if sick:
                                    turn = Turn(sick=sick.id,
                                                doctor=doctor.id,
                                                medical=int(request.form['medical']),
                                                date = datetime.date.today())

                                    sick.phone = phone
                                    db.session.add(turn)
                                    doctor.daily_capacity = doctor.daily_capacity - 1
                                    db.session.commit()
                                    flash('نوبت با موفقت ثبت شد', category='success')
                                else:
                                    el_sick = Sick(NC=NC,
                                                   name=request.form['name'],
                                                   last_name=request.form['last_name'],
                                                   phone=phone)
                                    db.session.add(el_sick)
                                    db.session.commit()
                                    get_sick = Sick.query.filter_by(NC=NC).first()
                                    turn = Turn(sick=get_sick.id,
                                                doctor=doctor.id,
                                                medical=int(request.form['medical']),
                                                date = datetime.date.today())
                                    db.session.add(turn)
                                    doctor.daily_capacity = doctor.daily_capacity - 1
                                    db.session.commit()
                                    flash('نوبت با موفقت ثبت شد', category='success')
                                return redirect(url_for('admin_login', input='turn'))
                            else:
                                flash('تعداد نوبت روزانه پزشک موردنظر به پایان رسیده است', category='danger')
                                return redirect(url_for('admin_login', input='turn'))
                        else:
                            flash(
                                'شماره تلفن وارد شده صحیح نیست. شماره را بدون +98 وارد کرده و شماره تلفن ثابت را نیز با 076 '
                                'وارد کنید', category='danger')
                            return redirect(url_for('admin_login', input='turn'))
                    else:
                        flash('کدملی وارد شده صحیح نیست. کدملی باید دقیقا 10 رقم عددی باشد', category='danger')
                        return redirect(url_for('admin_login', input='turn'))
                except:
                    flash('شماره تلفن وارد شده صحیح نیست. شماره را بدون +98 وارد کرده و شماره تلفن ثابت را نیز با 076 '
                          'وارد کنید', category='danger')
                    return redirect(url_for('admin_login', input='turn'))
            except:
                flash('کدملی وارد شده صحیح نیست. کدملی باید دقیقا 10 رقم عددی باشد', category='danger')
                return redirect(url_for('admin_login', input='turn'))

    return redirect(url_for('admin_login', input='turn'))


@app.route('/load-medicals-admin', methods=['POST'])
@login_required
def load_medicals_admin():
    if current_user.access_level == 1 or current_user.access_level == 2:
        medicals = []
        for medical in Medical.query.all():
            city = City.query.filter_by(id=medical.city).first()
            medicals.append({"medical_id": medical.id, "medical_name": medical.name + "-" + city.name})
        return {"medicals": medicals}
    else:
        return redirect(url_for('admin_login', input='panel'))


@app.route('/sick-logout', methods=['GET'])
def sick_logout():
    session.clear()
    return redirect(url_for('home'))
