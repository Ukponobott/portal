from flask import Flask, redirect, render_template, request, session, url_for, jsonify
from flask_pymongo import PyMongo
import os


app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb://localhost:27017/student_data'
mongo = PyMongo(app)


app.secret_key = os.urandom(24)


def get_reg_no():
    """Generating a a registration number for each student"""
    students = mongo.db.students
    no_of_students = students.find()
    print(no_of_students)
    current_no = list(no_of_students)
    print(current_no)
    total_number_students = len(current_no)
    print(total_number_students)
    new_reg = total_number_students + 1
    print(new_reg)
    department = request.form.get("department")
    year = request.form.get("admission_year")
    programme = request.form.get("programme")
    get_initials = department[:2].upper()
    get_year = year[2:]
    new_reg_1 = str(new_reg)

    # set the variable to an empty value
    programme_suffix = ""
    # test conditions to get the programme status and format the reg no
    if programme == "National Diploma - Regular":
        programme_suffix = ""
    if programme == "National Diploma - Part Time":
        programme_suffix = "E"
    if programme == "Higher National Diploma - Regular":
        programme_suffix = "H"
    if programme == "Higher National Diploma - Part Time":
        programme_suffix = "EH"

    number = get_year + str(programme_suffix) + "/000" + new_reg_1 + "/" + get_initials
    number_1 = get_year + str(programme_suffix) + "/00" + new_reg_1 + "/" + get_initials
    number_2 = get_year + str(programme_suffix) + "/0" + new_reg_1 + "/" + get_initials

    if len(new_reg_1) == 1:
        reg_no = number
        return reg_no
    elif len(new_reg_1) == 2:
        reg_no = number_1
        return reg_no
    elif len(new_reg_1) == 3:
        reg_no = number_2
        return reg_no


@app.route('/register', methods=["GET", "POST"])
def register():
    """The route to register students new to the platform"""
    if request.method == "POST":
        level = ""
        # get the programme to determine to student level
        if request.form.get("programme") == "National Diploma - Regular" or "National Diploma - Part Time":
            level = "ND 1"
        elif request.form.get("programme") == "Higher National Diploma - Regular" or \
                "Higher National Diploma - Part Time":
            level = "HND 1"
        students = mongo.db.students
        new_user = mongo.db.students.find_one(
            {"email": request.form.get("email")})
        if new_user is None:
            students.insert_one({
                             "first_name": request.form.get("first_name"),
                             "last_name": request.form.get("last_name"),
                             "email": request.form.get("email"),
                             "password": "12345",
                             "sex": request.form.get("sex"),
                             "programme": request.form.get("programme"),
                             "faculty": request.form.get("faculty"),
                             "reg_no": get_reg_no(),
                             "department": request.form.get("department"),
                             "level": level,
                             "admission_year": request.form.get("admission_year")
                             })
        else:
            error = "User already exists"
            return render_template("register.html", error=error)
        name = request.form.get("first_name") + " " + request.form.get("last_name")
        reg_no = get_reg_no()
        password = 12345
        return render_template("success.html", name=name, reg_no=reg_no, password=password)
    else:
        return render_template("register.html")


@app.route('/')
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session.pop("email", None)
        students = mongo.db.students
        existing_user = students.find_one({"email": request.form.get("email")})
        if existing_user:
            if request.form["password"] == existing_user["password"]:
                session["email"] = existing_user["email"]
                return redirect(url_for('dashboard'))
            else:
                error = "Invalid Password"
                return render_template("login.html", error=error)
        else:
            error = "User does not exist, Please register"
            return render_template("login.html", error=error)
    else:
        return render_template("login.html")


@app.route('/dashboard')
def dashboard():
    if "email" in session:
        current_user = mongo.db.students.find_one({"email": session["email"]})
        if current_user["password"] == "12345":
                return redirect("change_password")
        else:
            name = current_user["first_name"] + " " + current_user["last_name"]
            faculty = current_user["faculty"]
            dept = current_user["department"]
            reg_no = current_user["reg_no"]
            return render_template("dashboard.html", name=name, reg_no=reg_no, dept=dept, faculty=faculty)


# def courses():
course_list = {
        "accountancy": {
            "nd_1":
                [
                    {
                        "GNS101": ["Use of English 1", 2],
                        "GNS102": ["Citizenship Education 1", 2],
                        "ACC111": ["Accounting Terms 1", 3],
                        "MTH101": ["Business Mathematics", 2]
                    },
                    {
                        "GNS121": ["Use of English 2", 2],
                        "GNS122": ["Citizenship Education 2", 2],
                        "ACC121": ["Accounting Terms 2", 3],
                        "MTH121": ["Business Mathematics 2", 2]
                    }
                ],

            "nd_2":
                [
                    {
                        "GNS201": ["Communication in English", 2],
                        "MTH201": ["Logic", 2],
                        "ACC211": ["Accounting Law", 3],
                        "ICT201": ["Introduction to Computer", 2]
                    },
                    {
                        "GNS202": ["Communication in English 2", 2],
                        "MTH202": ["Logic 2", 2],
                        "ACC221": ["Accounting Law 2", 3],
                        "ICT202": ["Computer Packages", 3]
                    }
                ],
            "hnd_1":
                [
                    {
                        "GNS301": ["Letter Writing", 2],
                        "EED302": ["Entrepreneurship Education 1", 3],
                        "ACC311": ["Accounting Process 1", 3],
                        "ICT302": ["Advanced Computer Packages", 2]
                    },
                    {
                        "GNS302": ["Letter Writing 2", 2],
                        "EED322": ["Entrepreneurship Education 2", 3],
                        "ACC321": ["Accounting Process 2", 3],
                        "ICT322": ["Advanced Computer Packages 2", 2]
                    }
                ],
            "hnd_2":
                [
                    {
                        "GNS401": ["Report Writing", 2],
                        "ACC411": ["Banking Process", 3],
                        "ACC412": ["Record Techniques 1", 3],
                        "ACC413": ["SME Management", 2]
                    },
                    {
                        "GNS421": ["Report Writing 2", 2],
                        "ACC421": ["Banking Process", 3],
                        "ACC422": ["Record Techniques 1", 3],
                        "ACC423": ["SME Management", 2]
                    }
                ]
        }

    }


# def credit_units(dept, level, semester):
units = []
course_code = []
course_title = []
current = course_list["accountancy"]["nd_1"]
i = current[0]
print(i)
for key, values in current[0].items():
    units.append(values[1])
    course_code.append(key)
    course_title.append(values[0])
# return total_units

print(course_code)
print(course_title)
print(units)


@app.route('/register courses')
def register_courses():
    # def credit_units(dept, level, semester):
    units = []
    course_code = []
    course_title = []
    current = course_list["accountancy"]["nd_1"]
    for key, values in current[0].items():
        units.append(values[1])
        course_code.append(key)
        course_title.append(values[0])
    # return total_units

    print(course_code)
    print(course_title)
    print(units)

    # total_units = []
    # current = course_list["accountancy"]["nd_1"]
    # i = current[0]
    # for key, values in current[0].items():
    #     total_units.append(values[1])
    # if "email" in session:
    #     current_user = mongo.db.students.find_one({"email": session["email"]})
    if request.method == "POST":
        pass
    else:
        return render_template("register_courses.html", courses=course_title)


@app.route('/change_password', methods=["GET", "POST"])
def change_password():
    if "email" in session:
        students = mongo.db.students
        find_user = mongo.db.students.find_one({"email": session["email"]})
    # if "email" in session:
    if request.method == "POST":
        # get the new password from form
        new_password = request.form.get("new_password")
        # get the password confirmation from form
        confirm_password = request.form.get("confirm_password")
        # find the user details to update
        # test if new password and confirm password matches
        if new_password == confirm_password:
            # old_password = find_user["password"]
            password = {"$set": {"password": new_password}}
            students.update_one(find_user, password)
            return redirect(url_for("dashboard"))
        else:
            error = "Passwords do not match"
            return render_template("change_password.html", error=error)
    else:
        error = ""
        return render_template("change_password.html", error=error)


@app.route("/logout")
def logout():
    session.pop("email", None)
    return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(debug=True)
