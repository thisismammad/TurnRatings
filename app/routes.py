from flask import render_template
from app import app


@app.route('/')
def login():
    return render_template('login.html')


@app.route('/user-panel')
def panel():
    return render_template('panel.html')


@app.route('/user-turn')
def user_turn():
    return render_template('turn.html')


@app.route('/user-report')
def user_report():
    return render_template('report.html')


@app.route('/<input>')
def admin_login(input):
    return render_template('admin-'+input+'.html')


a = """
@app.route('/panel', methods=["GET", "POST"])
def admin_panel():
    return render_template('admin-panel.html')


@app.route('/change-password', methods=["GET", "POST"])
def change_password():
    return render_template('admin-changepassword.html')


@app.route('/cities', methods=["GET", "POST"])
def cities():
    return render_template('admin-city.html')


@app.route('/doctors', methods=["GET", "POST"])
def doctors():
    return render_template('admin-doctor.html')


@app.route('/medicals', methods=["GET", "POST"])
def medicals():
    return render_template('admin-medical.html')


@app.route('/reception', methods=["GET", "POST"])
def reception():
    return render_template('admin-reception.html')


@app.route('/report', methods=["GET", "POST"])
def report():
    return render_template('admin-report.html')


@app.route('/specialties', methods=["GET", "POST"])
def specialties():
    return render_template('admin-specialty.html')


@app.route('/turn', methods=["GET", "POST"])
def turn():
    return render_template('admin-turn.html')


@app.route('/users', methods=["GET", "POST"])
def users():
    return render_template('admin-user.html')
    
"""