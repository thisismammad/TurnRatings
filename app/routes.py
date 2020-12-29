from flask import render_template, request, flash, redirect, url_for
from app import app
from app.models import *


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/user-panel', methods=['GET', 'POST'])
def panel():
    NC = 0
    if request.method == "POST":
        if Sick.query.filter_by(NC=int(request.form["NC"])).first():
            NC = request.form["NC"]
        elif not Sick.query.filter_by(NC=int(request.form["NC"])).first():
            sick = Sick(NC=int(request.form["NC"]))
            NC = sick.NC
            db.session.add(sick)
            db.session.commit()
    return render_template('panel.html', values=locals())


@app.route('/user-turn<user_NC>', methods=['GET', 'POST'])
def user_turn(user_NC):
    date = datetime.now().strftime("%Y/%m/%d")
    NC = user_NC
    specialties = []
    for speciality in Specialty.query.all():
        specialties.append(speciality)

    medicals = []
    for medial in Medical.query.all():
        medicals.append(medial)

    doctors = []
    for doctor in Doctor.query.all():
        doctors.append(doctor)

    cites = []
    for city in City.query.all():
        cites.append(city)
    return render_template('turn.html', values=locals())


@app.route('/user-report', methods=['GET', 'POST'])
def user_report():
    return render_template('report.html')


@app.route('/<input>', methods=['GET', 'POST'])
def admin_login(input):
    data = []
    if input == 'city':
        data.clear()
        for city in City.query.all():
            data.append(city)
    elif input == 'speciality':
        data.clear()
        for speciality in Specialty.query.all():
            data.append(speciality)
    elif input == 'doctor':
        data.clear()
        for doctor in Doctor.query.all():
            medical = Medical.query.filter_by(id=doctor.medical).first()
            sp = Specialty.query.filter_by(id=doctor.specialty).first()
            data.append({"name": doctor.name,
                         "last_name": doctor.last_name,
                         "NC": doctor.NC,
                         "phone": '0' + str(doctor.phone),
                         "medical": medical.name,
                         "speciality": sp.name})

        specialties = []
        for speciality in Specialty.query.all():
            specialties.append(speciality)

        medicals = []
        for medial in Medical.query.all():
            medicals.append(medial)
    elif input == 'user':
        data.clear()
        for employee in Employee.query.all():
            medical = Medical.query.filter_by(id=employee.medical).first()
            position = ''
            if '1' == str(employee.id)[0]:
                position = 'مدیر مرکز'
            elif '2' == str(employee.id)[0]:
                position = 'کارمند مرکز'

            data.append({"id": employee.id,
                         "NC": employee.NC,
                         "name": employee.name,
                         "last_name": employee.last_name,
                         "position": position,
                         "phone": '0' + str(employee.phone),
                         "medical": medical.name,
                         })
        medicals = []
        for medial in Medical.query.all():
            medicals.append(medial)

    elif input == 'medical':
        data.clear()
        for medical in Medical.query.all():
            city = City.query.filter_by(id=medical.city).first()
            data.append({"name": medical.name,
                         "address": medical.address,
                         "phone": '0' + str(medical.phone),
                         "city": city.name})
        cites = []
        for city in City.query.all():
            cites.append(city)

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
            position = ''
            if request.form['position'] == "1":
                position = '1'
            elif request.form['position'] == "2":
                position = '2'
            employee = Employee(id=int(position + request.form['id']),
                                NC=request.form['NC'],
                                name=request.form['name'],
                                last_name=request.form['last_name'],
                                phone=int(request.form['phone']),
                                medical=request.form['medical'])
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
        if not request.form['NC'] \
                and not request.form['phone'] \
                and not request.form['city'] \
                and not request.form['medical'] \
                and not request.form['speciality'] \
                and not request.form['doctor']:
            flash('پر کردن تمام فیلد ها ضروری است', category='danger')
        else:
            sick = Sick.query.filter_by(NC=int(request.form['NC'])).first
            turn = Turn(sick=sick.id,
                        doctor=int(request.form['doctor']),
                        medical=int(request.form['medical']))

            sick.phone = request.form['phone']
            db.session.add(turn)
            db.session.commit()
            flash('نوبت با موفقت ثبت شد', 'success')
            return redirect(url_for('panel'))
    return redirect(url_for('panel'))
