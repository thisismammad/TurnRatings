from flask import render_template, request, flash, redirect, url_for
from app import app
from app.models import *
import datetime
from werkzeug.security import generate_password_hash, check_password_hash

curent_sick_NC = 0
searched = False


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/user-panel', methods=['POST', 'GET'])
def panel():
    global curent_sick_NC
    if request.method == "POST":
        if request.form['NC']:
            try:
                nc = int(request.form['NC'])
                if len(str(nc)) == 10:
                    curent_sick_NC = nc
                    if not Sick.query.filter_by(NC=curent_sick_NC).first():
                        sick = Sick(NC=curent_sick_NC)
                        db.session.add(sick)
                        db.session.commit()
                    return render_template('panel.html')
                else:
                    flash("کد ملی وارد شده صحیح نیست کد ملی باید دقیقا 10 رقم عددی باشد", category='danger')
            except:
                flash("کد ملی وارد شده صحیح نیست کد ملی باید دقیقا 10 رقم عددی باشد", category='danger')
        else:
            flash("کد ملی را وارد کنید", category='danger')
    elif request.method == "GET":
        return render_template('panel.html')
    return redirect(url_for('home'))


@app.route('/user-turn', methods=['GET'])
def user_turn():
    date = datetime.date.today()
    NC = curent_sick_NC
    cites = []
    for city in City.query.all():
        cites.append(city)
    render_template('turn.html', values=locals())
    return render_template('turn.html', values=locals())


@app.route('/user-report', methods=['GET'])
def user_report():
    turns = []
    sick = Sick.query.filter_by(NC=curent_sick_NC).first()
    for turn in Turn.query.filter_by(sick=sick.id):
        doctor = Doctor.query.filter_by(id=turn.doctor).first()
        medical = Medical.query.filter_by(id=turn.medical).first()
        specialty = Specialty.query.filter_by(id=doctor.specialty).first()
        city = City.query.filter_by(id=medical.city).first()
        turns.append({"id": turn.id,
                      "sick": curent_sick_NC,
                      "speciality": specialty.name,
                      "doctor": doctor.name + '-' + doctor.last_name,
                      "date": turn.date.date(),
                      "medical": city.name + '-' + medical.name,
                      "status": turn.status})
    return render_template('report.html', values=locals())


@app.route('/<input>', methods=['GET', 'POST'])
def admin_login(input):
    global searched
    data = []
    if input == 'city':
        data.clear()
        for city in City.query.all():
            if city.status == 1:
                data.append(city)
    elif input == 'speciality':
        data.clear()
        for speciality in Specialty.query.all():
            if speciality.status == 1:
                data.append(speciality)
    elif input == 'doctor':
        data.clear()
        for doctor in Doctor.query.all():
            if doctor.status == 1:
                medical = Medical.query.filter_by(id=doctor.medical).first()
                sp = Specialty.query.filter_by(id=doctor.specialty).first()
                data.append({"id": doctor.id,
                             "name": doctor.name,
                             "last_name": doctor.last_name,
                             "NC": doctor.NC,
                             "phone": '0' + str(doctor.phone),
                             "medical": medical.name,
                             "speciality": sp.name})
        specialties = []
        for speciality in Specialty.query.all():
            if speciality.status == 1:
                specialties.append(speciality)

        medicals = []
        for medical in Medical.query.all():
            if medical.status == 1:
                medicals.append(medical)
    elif input == 'user':
        data.clear()
        for employee in Employee.query.all():
            if employee.status == 1:
                medical = Medical.query.filter_by(id=employee.medical).first()
                data.append({"id": employee.id,
                             "NC": employee.NC,
                             "name": employee.name,
                             "last_name": employee.last_name,
                             "position": employee.position,
                             "phone": '0' + str(employee.phone),
                             "medical": medical.name,
                             })
        medicals = []
        for medical in Medical.query.all():
            if medical.status == 1:
                medicals.append(medical)

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
    elif input == 'reception':
        print(searched)
        data.clear()
        for turn in Turn.query.all():
            if turn.date.date() == datetime.date.today():
                if turn.status == 1:
                    sick = Sick.query.filter_by(id=turn.sick).first()
                    doctor = Doctor.query.filter_by(id=turn.doctor).first()
                    medical = Medical.query.filter_by(id=turn.medical).first()
                    specialty = Specialty.query.filter_by(id=doctor.specialty).first()
                    data.append({"id": turn.id,
                                 "sick": sick.NC,
                                 "speciality": specialty.name,
                                 "doctor": doctor.name,
                                 "date": turn.date.date(),
                                 "medical": medical.name,
                                 "status": turn.status})
            else:
                turn.status = 3
                db.session.commit()

    elif input == 'report':
        data.clear()
        specialties = []
        for speciality in Specialty.query.all():
            specialties.append(speciality)

        medicals = []
        for medical in Medical.query.all():
            medicals.append(medical)

        doctors = []
        for doctor in Doctor.query.all():
            doctors.append(doctor)

        cities = []
        for city in City.query.all():
            cities.append(city)
    searched = False
    is_search = searched
    return render_template('admin-' + input + '.html', values=locals())


@app.route('/add-city', methods=['POST', 'GET'])
def add_city():
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


@app.route('/add-speciality', methods=['GET', 'POST'])
def add_speciality():
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


@app.route('/add-medical', methods=['GET', 'POST'])
def add_medical():
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
                    flash('شماره تلفن وارد شده صحیح نیست. شماره را بدون +98 وارد کرده و شماره تلفن ثابت را نیز با 076 '
                          'وارد کنید', category='danger')
                    return redirect(url_for('admin_login', input='medical'))
            except:
                flash('شماره تلفن وارد شده صحیح نیست. شماره را بدون +98 وارد کرده و شماره تلفن ثابت را نیز با 076'
                      'وارد کنید', category='danger')
                return redirect(url_for('admin_login', input='medical'))
    return redirect(url_for('admin_login', input='medical'))


@app.route('/add-doctor', methods=['GET', 'POST'])
def add_doctor():
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
                    flash('شماره تلفن وارد شده صحیح نیست. شماره را بدون +98 وارد کرده و شماره تلفن ثابت را نیز با 076 '
                          'وارد کنید', category='danger')
                    return redirect(url_for('admin_login', input='doctor'))

            except:
                flash('کدملی وارد شده صحیح نیست . کدملی باید دقیقا 10 رقم عددی باشد', category='danger')
                return redirect(url_for('admin_login', input='doctor'))
    return redirect(url_for('admin_login', input='doctor'))


@app.route('/add-user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        if not request.form['id'] \
                or not request.form['name'] or any(char.isdigit() for char in request.form['name']) \
                or not request.form['last_name'] or any(char.isdigit() for char in request.form['last_name']) \
                or not request.form['NC'] \
                or not request.form['phone'] \
                or not request.form['position'] or request.form['position'] == '0' \
                or not request.form['medical'] or request.form['medical'] == '0':
            flash('پر کردن تمام فیلد ها ضروری است.', category='danger')
            flash(' نام و نام خانوادگی نباید شامل عدد باشد', category='danger')
            return redirect(url_for('admin_login', input='user'))
        else:
            try:
                user_id = int(request.form['id'])
                try:
                    NC = int(request.form['NC'])
                    try:
                        phone = int(request.form['phone'])
                        if len(str(user_id)) == 10:
                            if len(str(NC)) == 10:
                                if len(str(phone)) == 10:
                                    employee = Employee(id=user_id,
                                                        NC=NC,
                                                        name=request.form['name'],
                                                        last_name=request.form['last_name'],
                                                        phone=phone,
                                                        position=int(request.form['position']),
                                                        medical=request.form['medical'])
                                    user = User(id=employee.id,
                                                password=generate_password_hash(str(employee.NC)),
                                                access_level=employee.position)
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
                                flash('کدملی وارد شده صحیح نیست . کدملی باید دقیقا 10 رقم عددی باشد', category='danger')
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


@app.route('/add-turn', methods=['POST'])
def add_turn():
    print(request.form['city'])
    if request.method == 'POST':
        if not request.form['phone'] \
                or not request.form['city'] or request.form['city'] == '0' \
                or not request.form['medical'] or request.form['medical'] == '0' \
                or not request.form['speciality'] or request.form['speciality'] == '0' \
                or not request.form['doctor'] or request.form['doctor'] == '0':
            flash('پر کردن تمام فیلد ها ضروری است', category='danger')
            redirect(url_for('user_turn'))
        else:
            try:
                phone = int(request.form['phone'])
                if len(str(phone)) == 10:
                    doctor = Doctor.query.filter_by(id=int(request.form['doctor'])).first()
                    if doctor.daily_capacity > 0:
                        sick = Sick.query.filter_by(NC=curent_sick_NC).first()
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
                    flash('شماره تلفن وارد شده صحیح نیست. شماره را بدون +98 وارد کرده و شماره تلفن ثابت را نیز با 076 '
                          'وارد کنید', category='danger')
                    return redirect(url_for('user_turn'))
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
def delete_medical(medical_id):
    if request.method == "POST":
        medical = Medical.query.filter_by(id=int(medical_id)).first()
        medical.status = 0
        db.session.commit()
        flash('مرکز درمانی با موفقیت حذف شد', category='success')
        return redirect(url_for("admin_login", input="medical"))
    return redirect(url_for("admin_login", input="medical"))


@app.route('/edit-medical/<medical_id>', methods=['POST'])
def edit_medical(medical_id):
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
                    print(request.form['new_name'])
                    print(new_medical)
                    print(comparison_medical)
                    print(new_medical == comparison_medical)
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


@app.route('/delete-city/<city_id>', methods=['POST'])
def delete_city(city_id):
    if request.method == "POST":
        city = City.query.filter_by(id=int(city_id)).first()
        city.status = 0
        db.session.commit()
        flash('شهر با موفقیت حذف شد', category='success')
        return redirect(url_for("admin_login", input="city"))
    return redirect(url_for("admin_login", input="city"))


@app.route('/edit-city/<city_id>', methods=['POST'])
def edit_city(city_id):
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


@app.route('/delete-speciality/<speciality_id>', methods=['POST'])
def delete_speciality(speciality_id):
    if request.method == "POST":
        speciality = Specialty.query.filter_by(id=int(speciality_id)).first()
        speciality.status = 0
        db.session.commit()
        flash('تخصص با موفقیت حذف شد', category='success')
        return redirect(url_for("admin_login", input="speciality"))
    return redirect(url_for("admin_login", input="speciality"))


@app.route('/edit-speciality/<speciality_id>', methods=['POST'])
def edit_speciality(speciality_id):
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


@app.route('/delete-doctor/<doctor_id>', methods=['POST'])
def delete_doctor(doctor_id):
    if request.method == "POST":
        doctor = Doctor.query.filter_by(id=int(doctor_id)).first()
        doctor.status = 0
        db.session.commit()
        return redirect(url_for("admin_login", input="doctor"))
    return redirect(url_for("admin_login", input="doctor"))


@app.route('/edit-doctor/<doctor_id>', methods=['POST'])
def edit_doctor(doctor_id):
    if request.method == 'POST':
        if not request.form['new_name'] or any(char.isdigit() for char in request.form['new_name']) \
                or not request.form['new_last_name'] or any(char.isdigit() for char in request.form['new_last_name']) \
                or not request.form['new_NC'] \
                or not request.form['new_phone'] \
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
                            new_doctor = Doctor.query.filter_by(id=int(doctor_id)).first()
                            comparison_doctor = Doctor(id=int(doctor_id),
                                                       name=request.form['new_name'],
                                                       last_name=request.form['new_last_name'],
                                                       NC=NC,
                                                       phone=phone,
                                                       specialty=request.form['new_medical'],
                                                       medical=request.form['new_specialty'])
                            print(new_doctor)
                            print(comparison_doctor)
                            print(new_doctor == comparison_doctor)
                            if not new_doctor == comparison_doctor:
                                new_doctor.name = request.form["new_name"]
                                new_doctor.last_name = request.form["new_last_name"]
                                new_doctor.NC = NC
                                new_doctor.phone = phone
                                new_doctor.medical = int(request.form["new_medical"])
                                new_doctor.specialty = int(request.form["new_specialty"])
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
                    flash('شماره تلفن وارد شده صحیح نیست. شماره را بدون +98 وارد کرده و شماره تلفن ثابت را نیز با 076 '
                          'وارد کنید', category='danger')
                    return redirect(url_for('admin_login', input='doctor'))
            except:
                flash('کدملی وارد شده صحیح نیست . کدملی باید دقیقا 10 رقم عددی باشد', category='danger')
                return redirect(url_for('admin_login', input='doctor'))
    return redirect(url_for('admin_login', input='doctor'))


@app.route('/delete-user/<user_id>', methods=['POST'])
def delete_user(user_id):
    if request.method == "POST":
        employee = Employee.query.filter_by(id=int(user_id)).first()
        employee.status = 0
        user = User.query.filter_by(id).delete()
        db.session.commit()
        flash('کارمند با موفقیت حذف شد', category='success')
        return redirect(url_for("admin_login", input="user"))
    return redirect(url_for("admin_login", input="user"))


@app.route('/edit-user/<user_id>', methods=['POST'])
def edit_user(user_id):
    if request.method == 'POST':
        if not request.form['new_name'] or any(char.isdigit() for char in request.form['new_name']) \
                or not request.form['new_last_name'] or any(char.isdigit() for char in request.form['new_last_name']) \
                or not request.form['new_NC'] \
                or not request.form['new_phone'] \
                or not request.form['new_position'] \
                or not request.form['new_medical']:
            flash('پر کردن تمام فیلد ها ضروری است.', category='danger')
            flash(' نام و نام خانوادگی نباید شامل عدد باشد', category='danger')
            return redirect(url_for('admin_login', input='user'))
        else:
            try:
                NC = int(request.form['new_NC'])
                try:
                    phone = int(request.form['new_phone'])
                    if len(str(NC)) == 10:
                        if len(str(phone)) == 10:
                            new_employee = Employee.query.filter_by(id=int(user_id)).first()
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


@app.route('/change-password/', methods=['POST'])
def change_password():
    if request.method == "POST":
        user = User.query.filter_by(id=int('current user id')).first()
        if request.form["old_password"] \
                and request.form["new_password"] \
                and request.form["confirm_password"]:
            if check_password_hash(user.password, request.form["old_password"]):
                if request.form["new_password"] == request.form["confirm_password"]:
                    if len(request.form["new_password"]) > 8:
                        user.password = generate_password_hash(request.form["new_password"])
                        db.session.commit()
                        flash('رمز عبور با موفقیت تغییر کرد', category='success')
                        return redirect(url_for("admin_login", input="changepassword"))
                    else:
                        flash('رمز عبور باید حداقل 8 کاراکتر باشد ', category='danger')
                        return redirect(url_for("admin_login", input="changepassword"))
                else:
                    flash('رمز عبور جدید و تکرار آن یکی نیست', category='danger')
                    return redirect(url_for("admin_login", input="changepassword"))
            else:
                flash('رمز عبور قدیمی وارد شده صحیح نیست', category='danger')
                return redirect(url_for("admin_login", input="changepassword"))
    return redirect(url_for("admin_login", input="changepassword"))


@app.route('/reset-password/<user_id>', methods=['POST'])
def reset_password(user_id):
    if request.method == "POST":
        employee = Employee.query.filter_by(id=int(user_id)).first()
        user = User.query.filter_by(id=employee.id)
        user.password = generate_password_hash(str(employee.NC))
        db.session.commit()
        return redirect(url_for("admin_login", input="user"))
    return redirect(url_for("admin_login", input="user"))


@app.route('/reception/<turn_id>', methods=['POST', 'GET'])
def reception(turn_id):
    turn = Turn.query.filter_by(id=int(turn_id)).first()
    turn.status = 2
    db.session.commit()
    flash('پذیرش بیمار انجام شد', category='success')
    return redirect(url_for("admin_login", input="reception"))


@app.route('/cancel-turn', methods=['POST', 'GET'])
def cancel_turn():
    turn = Turn.query.filter_by(id=int(request.form["turn_id"])).first()
    turn.status = 0
    db.session.commit()
    flash('نوبت باموفقت لغو شد', category='success')
    return redirect(url_for("user_report"))


@app.route('/search-sick', methods=['POST', 'GET'])
def search_sick():
    data = []
    global searched
    sick = Sick.query.filter_by(NC=int(request.form["sick_NC"])).first()
    if sick:
        searched = True
        is_search = searched
        for turn in Turn.query.filter_by(sick=sick.id):
            doctor = Doctor.query.filter_by(id=turn.doctor).first()
            medical = Medical.query.filter_by(id=turn.medical).first()
            specialty = Specialty.query.filter_by(id=doctor.specialty).first()
            data.append({"id": turn.id,
                         "sick": sick.NC,
                         "speciality": specialty.name,
                         "doctor": doctor.name + '-' + doctor.last_name,
                         "date": turn.date.date(),
                         "status": turn.status})
    else:
        flash('بیمار با این کد ملی در سیستم وجود ندارد', category='danger')
        searched = False
        is_search = searched
        redirect(url_for('admin_login', input="reception"))
    return render_template('admin-reception.html', values=locals())


@app.route('/edit-sick/<sick_id>', methods=['POST'])
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
                                global searched
                                searched = False
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
def reporting():
    if request.method == "POST":
        if not request.form["start_date"] or not request.form["end_date"]:
            flash('انتخاب تاریخ شروع و پایان الزامی است', category='danger')
            return redirect(url_for('admin_login', input='report'))
        else:
            data = []
            s_date = str(request.form["start_date"]).split('-')
            e_date = str(request.form["end_date"]).split('-')
            send_start_date = s_date[0] + '-' + s_date[1] + '-' + s_date[2]
            send_end_date = e_date[0] + '-' + e_date[1] + '-' + e_date[2]
            start_date = datetime.datetime(int(s_date[0]), int(s_date[1]), int(s_date[2]))
            end_date = datetime.datetime(int(e_date[0]), int(e_date[1]), int(e_date[2]))

            if start_date > end_date:
                flash('تاریخ شروع باید کوچکتر از تاریخ پایان باشد', category='danger')
                return redirect(url_for('admin_login', input='report'))
            turn = Turn.query.first()
            for turn in Turn.query.filter(Turn.date >= start_date, Turn.date <= end_date):
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

            city_id = int(request.form["city"])
            medical_id = int(request.form["medical"])
            speciality_id = int(request.form["speciality"])
            doctor_id = int(request.form["doctor"])
            filter_by = {}
            filter_by = {"city": city_id, "medical": medical_id, "sp": speciality_id, "doctor": doctor_id}
            for i in filter_by.copy():
                if not filter_by[i]:
                    del filter_by[i]

            print(filter_by)
            for item in data.copy():
                for k, v in filter_by.items():
                    if k == "city":
                        t_city = City.query.filter_by(id=v).first()
                        md = Medical.query.filter_by(city=v).first()
                        if md:
                            for t_medical in Medical.query.filter_by(city=v):
                                if item in data:
                                    if not item["medical"] == t_medical.name + '-' + t_city.name:
                                        data.remove(item)
                        else:
                            data.clear()
                            return render_template('admin-report.html', values=locals())
                    if k == "medical":
                        t_t_medical = Medical.query.filter_by(id=v).first()
                        t_t_city = City.query.filter_by(id=t_t_medical.city).first()

                        if not item["medical"] == t_t_medical.name + '-' + t_t_city.name:
                            data.remove(item)

                    if k == "sp":
                        dc = Doctor.query.filter_by(specialty=v).first()
                        if dc:
                            for t_doctor in Doctor.query.filter_by(specialty=v):
                                t_specialty = Specialty.query.filter_by(id=t_doctor.specialty).first()
                                if item in data:
                                    if not item[
                                               "doctor"] == t_doctor.name + ' ' + t_doctor.last_name + '-' + t_specialty.name:
                                        data.remove(item)
                        else:
                            data.clear()
                            return render_template('admin-report.html', values=locals())
                    if k == "doctor":
                        t_t_doctor = Doctor.query.filter_by(id=v).first()
                        t_t_specialty = Specialty.query.filter_by(id=t_t_doctor.id).first()
                        if item in data:
                            if not item[
                                       "doctor"] == t_t_doctor.name + ' ' + t_t_doctor.last_name + '-' + t_t_specialty.name:
                                data.remove(item)
        print(locals())
        return render_template('admin-report.html', values=locals())
    return redirect(url_for('admin_login', input='report'))


@app.route('/load-data-for-report', methods=['GET', 'POST'])
def load_data_for_report():
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
        medicals.append({"medical_id": medical.id,
                         "medical_name": medical.name,
                         "medical_city": medical.city})
    for sp in Specialty.query.all():
        specialties.append({"sp_name": sp.name,
                            "sp_id": sp.id})
    for city in City.query.all():
        cities.append({"city_name": city.name,
                       "city_id": city.id})
    return {"cities": cities, "medicals": medicals, "specialties": specialties, "doctors": doctors}
