from flask import render_template, request, flash, redirect, url_for
from app import app
from app.models import *
import datetime
import json

curent_sick_NC = 0
searched = False


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/user-panel', methods=['POST', 'GET'])
def panel():
    print("------------------------------")
    global curent_sick_NC
    if request.method == "POST":
        if request.form['NC']:
            curent_sick_NC = int(request.form['NC'])
        if not Sick.query.filter_by(NC=curent_sick_NC).first():
            sick = Sick(NC=curent_sick_NC)
            db.session.add(sick)
            db.session.commit()
    return render_template('panel.html')


@app.route('/user-turn', methods=['GET', 'POST'])
def user_turn():
    date = datetime.date.today()
    NC = curent_sick_NC
    cites = []
    medicals = []
    specialties = []
    doctors = []
    for city in City.query.all():
        cites.append(city)
    for medical in Medical.query.all():
        medicals.append(medical)
    for sp in Specialty.query.all():
        specialties.append(sp)
    for doctor in Doctor.query.all():
        doctors.append(doctor)
    render_template('turn.html', values=locals())
    return render_template('turn.html', values=locals())


@app.route('/user-report', methods=['GET', 'POST'])
def user_report():
    turns = []
    sick = Sick.query.filter_by(NC=curent_sick_NC).first()
    print(sick)
    for turn in Turn.query.filter_by(sick=sick.id):
        doctor = Doctor.query.filter_by(id=turn.doctor).first()
        medical = Medical.query.filter_by(id=turn.medical).first()
        specialty = Specialty.query.filter_by(id=doctor.specialty).first()
        turns.append({"id": turn.id,
                      "sick": curent_sick_NC,
                      "speciality": specialty.name,
                      "doctor": doctor.name,
                      "date": turn.date.date(),
                      "medical": medical.name,
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

    searched = False
    is_search = searched
    return render_template('admin-' + input + '.html', values=locals())


@app.route('/add-city', methods=['GET', 'POST'])
def add_city():
    if request.method == 'POST':
        if not request.form['name']:
            flash('نام شهر را وارد کنید', category='danger')
        else:
            city = City(name=request.form['name'])
            db.session.add(city)
            db.session.commit()
            flash('شهر با موفقت اضافه شد', 'success')
            return redirect(url_for('admin_login', input='city'))
    return redirect(url_for('admin_login', input='city'))


@app.route('/add-speciality', methods=['GET', 'POST'])
def add_speciality():
    if request.method == 'POST':
        if not request.form['name']:
            flash('نام تخصص را وارد کنید', category='danger')
        else:
            speciality = Specialty(name=request.form['name'])
            db.session.add(speciality)
            db.session.commit()
            flash('تخصص با موفقت اضافه شد', 'success')
            return redirect(url_for('admin_login', input='speciality'))
    return redirect(url_for('admin_login', input='speciality'))


@app.route('/add-medical', methods=['GET', 'POST'])
def add_medical():
    if request.method == 'POST':
        if not request.form['name'] \
                and not request.form['address'] \
                and not request.form['phone'] \
                and not request.form['city']:
            flash('پر کردن تمام فیلد ها ضروری است', category='danger')
        else:
            medical = Medical(name=request.form['name'],
                              address=request.form['address'],
                              phone=int(request.form['phone']),
                              city=request.form['city'])
            db.session.add(medical)
            db.session.commit()
            flash('مرکز درمانی با موفقت اضافه شد', 'success')
            return redirect(url_for('admin_login', input='medical'))
    return redirect(url_for('admin_login', input='medical'))


@app.route('/add-doctor', methods=['GET', 'POST'])
def add_doctor():
    if request.method == 'POST':
        if not request.form['name'] \
                and not request.form['last_name'] \
                and not request.form['NC'] \
                and not request.form['phone'] \
                and not request.form['speciality'] \
                and not request.form['medical']:
            flash('پر کردن تمام فیلد ها ضروری است', category='danger')
        else:

            doctor = Doctor(name=request.form['name'],
                            last_name=request.form['last_name'],
                            NC=request.form['NC'],
                            phone=int(request.form['phone']),
                            specialty=request.form['speciality'],
                            medical=request.form['medical'])
            db.session.add(doctor)
            db.session.commit()
            flash('پزشک با موفقت اضافه شد', 'success')
            return redirect(url_for('admin_login', input='doctor'))
    return redirect(url_for('admin_login', input='doctor'))


@app.route('/add-user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        if not request.form['id'] \
                and not request.form['name'] \
                and not request.form['last_name'] \
                and not request.form['NC'] \
                and not request.form['phone'] \
                and not request.form['position'] \
                and not request.form['medical']:
            flash('پر کردن تمام فیلد ها ضروری است', category='danger')
        else:
            employee = Employee(id=int(request.form['id']),
                                NC=request.form['NC'],
                                name=request.form['name'],
                                last_name=request.form['last_name'],
                                phone=int(request.form['phone']),
                                medical=request.form['medical'],
                                position=int(request.form['position']))
            user = User(id=employee.id, password=str(employee.NC))
            db.session.add(employee)
            db.session.add(user)
            db.session.commit()
            flash('کارمند با موفقت اضافه شد', 'success')
            return redirect(url_for('admin_login', input='user'))
    return redirect(url_for('admin_login', input='user'))


@app.route('/add-turn', methods=['GET', 'POST'])
def add_turn():
    if request.method == 'POST':
        if not request.form['phone'] \
                and not request.form['city'] \
                and not request.form['medical'] \
                and not request.form['speciality'] \
                and not request.form['doctor']:
            flash('پر کردن تمام فیلد ها ضروری است', category='danger')

        else:
            sick = Sick.query.filter_by(NC=curent_sick_NC).first()
            turn = Turn(sick=sick.id,
                        doctor=int(request.form['doctor']),
                        medical=int(request.form['medical']))

            sick.phone = request.form['phone']
            db.session.add(turn)
            db.session.commit()
            flash('نوبت با موفقت ثبت شد', 'success')
            return redirect(url_for('panel'))
    return redirect(url_for('panel'))


@app.route('/load-medicals', methods=['POST'])
def load_medicals():
    city = request.form.get('city_id')
    medicals = []
    for medical in Medical.query.filter_by(city=int(city)):
        medicals.append(medical)
    print(medicals)
    name = medicals[0].name
    print(name)
    return json.dumps({"medicals": "mammmaddddddd", "name": "محمد"}).encode()


@app.route('/load-sp-doctors<medical>', methods=['GET', 'POST'])
def load_sp_doctors(medical):
    if request.method == 'POST':
        specialties = []
        doctors = []
        if medical:
            for doctor in Doctor.query.filter_by(medical=int(medical)):
                doctors.append(doctor)
                specialty = Specialty.query.filter_by(id=doctor.specialty)
                if specialty.name not in specialties:
                    specialties.append(specialty.name)
            return redirect(url_for('user_turn', values=locals()))
    return redirect(url_for('user_turn', values=locals()))


@app.route('/delete-medical/<medical_id>', methods=['POST'])
def delete_medical(medical_id):
    if request.method == "POST":
        medical = Medical.query.filter_by(id=int(medical_id)).first()
        medical.status = 0
        db.session.commit()
        return redirect(url_for("admin_login", input="medical"))
    return redirect(url_for("admin_login", input="medical"))


@app.route('/edit-medical/<medical_id>', methods=['POST'])
def edit_medical(medical_id):
    if request.method == "POST":
        new_medical = Medical.query.filter_by(id=int(medical_id)).first()
        new_medical.name = request.form["new_name"]
        new_medical.phone = request.form["new_phone"]
        new_medical.city = int(request.form["new_city"])
        new_medical.address = request.form["new_address"]
        db.session.commit()
        return redirect(url_for("admin_login", input="medical"))
    return redirect(url_for("admin_login", input="medical"))


@app.route('/delete-city/<city_id>', methods=['POST'])
def delete_city(city_id):
    if request.method == "POST":
        city = City.query.filter_by(id=int(city_id)).first()
        city.status = 0
        db.session.commit()
        return redirect(url_for("admin_login", input="city"))
    return redirect(url_for("admin_login", input="city"))


@app.route('/edit-city/<city_id>', methods=['POST'])
def edit_city(city_id):
    if request.method == "POST":
        new_city = City.query.filter_by(id=int(city_id)).first()
        new_city.name = request.form["new_name"]
        db.session.commit()
        return redirect(url_for("admin_login", input="city"))
    return redirect(url_for("admin_login", input="city"))


@app.route('/delete-speciality/<speciality_id>', methods=['POST'])
def delete_speciality(speciality_id):
    if request.method == "POST":
        speciality = Specialty.query.filter_by(id=int(speciality_id)).first()
        speciality.status = 0
        db.session.commit()
        return redirect(url_for("admin_login", input="speciality"))
    return redirect(url_for("admin_login", input="speciality"))


@app.route('/edit-speciality/<speciality_id>', methods=['POST'])
def edit_speciality(speciality_id):
    if request.method == "POST":
        new_speciality = Specialty.query.filter_by(id=int(speciality_id)).first()
        new_speciality.name = request.form["new_name"]
        db.session.commit()
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
    if request.method == "POST":
        new_doctor = Doctor.query.filter_by(id=int(doctor_id)).first()
        new_doctor.name = request.form["new_name"]
        new_doctor.last_name = request.form["new_last_name"]
        new_doctor.NC = int(request.form["new_NC"])
        new_doctor.phone = int(request.form["new_phone"])
        new_doctor.medical = int(request.form["new_medical"])
        new_doctor.specialty = int(request.form["new_specialty"])
        db.session.commit()
        return redirect(url_for("admin_login", input="doctor"))
    return redirect(url_for("admin_login", input="doctor"))


@app.route('/delete-user/<user_id>', methods=['POST'])
def delete_user(user_id):
    if request.method == "POST":
        employee = Employee.query.filter_by(id=int(user_id)).first()
        employee.status = 0
        user = User.query.filter_by(id).delete()
        db.session.commit()
        return redirect(url_for("admin_login", input="user"))
    return redirect(url_for("admin_login", input="user"))


@app.route('/edit-user/<user_id>', methods=['POST'])
def edit_user(user_id):
    if request.method == "POST":
        new_employee = Employee.query.filter_by(id=int(user_id)).first()
        new_employee.name = request.form["new_name"]
        new_employee.last_name = request.form["new_last_name"]
        new_employee.NC = int(request.form["new_NC"])
        new_employee.phone = int(request.form["new_phone"])
        new_employee.medical = int(request.form["new_medical"])
        new_employee.position = int(request.form["new_position"])
        db.session.commit()
        return redirect(url_for("admin_login", input="user"))
    return redirect(url_for("admin_login", input="user"))


@app.route('/change-password/<user_id>', methods=['POST'])
def change_password(user_id):
    if request.method == "POST":
        user = User.query.filter_by(id=int(user_id)).first()
        user.password = request.form["new_password"]
        db.session.commit()
        return redirect(url_for("admin_login", input="changepassword"))
    return redirect(url_for("admin_login", input="changepassword"))


@app.route('/reception/<turn_id>', methods=['POST', 'GET'])
def reception(turn_id):
    turn = Turn.query.filter_by(id=int(turn_id)).first()
    turn.status = 2
    db.session.commit()
    return redirect(url_for("admin_login", input="reception"))


@app.route('/cancel-turn', methods=['POST', 'GET'])
def cancel_turn():
    turn = Turn.query.filter_by(id=int(request.form["turn_id"])).first()
    turn.status = 0
    db.session.commit()
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
                         "doctor": doctor.name,
                         "date": turn.date.date(),
                         "medical": medical.name,
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
        new_sick = Sick.query.filter_by(id=int(sick_id)).first()
        new_sick.name = request.form["new_name"]
        new_sick.last_name = request.form["new_last_name"]
        new_sick.NC = int(request.form["new_NC"])
        new_sick.phone = int(request.form["new_phone"])
        db.session.commit()
        global searched
        searched = False
        flash('اطلاعات بیمار بروزرسانی شد', category='success')
        return redirect(url_for("admin_login", input="reception"))
    return redirect(url_for("admin_login", input="reception"))
