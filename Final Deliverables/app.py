from flask import Flask, render_template, request, redirect, session

import ibm_db
import re

import os
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

app = Flask(__name__)

DB_URL = str(os.environ.get('DB_URL'))
SENDGRID_API_KEY = str(os.environ.get('SENDGRID_API_KEY'))

app.secret_key = "a"

conn = ibm_db.connect(
    DB_URL,
    "",
    "",
)


# HOME--PAGE
@app.route("/home")
def home():
    return render_template("homepage.html")


@app.route("/")
def add():
    return render_template("home.html")


# SIGN--UP--OR--REGISTER


@app.route("/signup")
def signup():
    return render_template("signup.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ""
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        sql = "SELECT * FROM REGISTER WHERE USERNAME =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)
        print(account)

        if account:
            msg = "Account already exists !"
        elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            msg = "Invalid email address !"
        elif not re.match(r"[A-Za-z0-9]+", username):
            msg = "name must contain only characters and numbers !"
        else:
            sql1 = "INSERT INTO REGISTER(USERNAME,PASSWORD,EMAIL) VALUES(?,?,?)"
            stmt1 = ibm_db.prepare(conn, sql1)

            ibm_db.bind_param(stmt1, 1, username)
            ibm_db.bind_param(stmt1, 2, password)
            ibm_db.bind_param(stmt1, 3, email)
            ibm_db.execute(stmt1)
            msg = "You have successfully registered !"
            return render_template("signup.html", msg=msg)


# LOGIN--PAGE


@app.route("/signin")
def signin():
    return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    global userid
    msg = ""

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        sql = "SELECT * FROM REGISTER WHERE USERNAME =? AND PASSWORD =?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, username)
        ibm_db.bind_param(stmt, 2, password)
        ibm_db.execute(stmt)
        account = ibm_db.fetch_assoc(stmt)

        if account:
            session["loggedin"] = True
            session["id"] = account["ID"]
            userid = account["ID"]
            session["username"] = account["USERNAME"]
            session["email"] = account["EMAIL"]

            return redirect("/home")
        else:
            msg = "Incorrect username / password !"
    return render_template("login.html", msg=msg)


# ADDING----DATA


@app.route("/add")
def adding():
    return render_template("add.html")


@app.route("/addexpense", methods=["GET", "POST"])
def addexpense():

    date = request.form["date"]
    expensename = request.form["expensename"]
    amount = request.form["amount"]
    paymode = request.form["paymode"]
    category = request.form["category"]
    time = request.form["time"]

    sql = "INSERT INTO EXPENSES(USERID,DATE,EXPENSENAME,AMOUNT,PAYMENTMODE,CATEGORY,TIME) VALUES(?,?,?,?,?,?,?)"
    creditpoint = (int(amount)/10000)*100
    # sql2 = "INSERT INTO CREDITS(USERID,CREDIT) VALUES(?,?)"
    # sql3 = "SELECT CREDIT FROM CREDITS WHERE USERID=?"
    stmt = ibm_db.prepare(conn, sql)
    # stmt2 = ibm_db.prepare(conn, sql2)
    # stmt3 = ibm_db.prepare(conn, sql3)
    # ibm_db.bind_param(stmt3,1,session["id"])
    # ibm_db.execute(stmt3)
    # fetchedamount = ibm_db.fetch_tuple(stmt3)
    # point = 0
    # for i in fetchedamount:
    #     point = point + i
    # creditpoint = point+creditpoint
    # print(creditpoint)
    ibm_db.bind_param(stmt, 1, session["id"])
    ibm_db.bind_param(stmt, 2, date)
    ibm_db.bind_param(stmt, 3, expensename)
    ibm_db.bind_param(stmt, 4, amount)
    ibm_db.bind_param(stmt, 5, paymode)
    ibm_db.bind_param(stmt, 6, category)
    ibm_db.bind_param(stmt, 7, time)
    # ibm_db.bind_param(stmt2,1,session["id"])
    # ibm_db.bind_param(stmt2,2,creditpoint)
    ibm_db.execute(stmt)
    # ibm_db.execute(stmt2)
    print(date + " " + expensename + " " +
          amount + " " + paymode + " " + category)
    sql1 = "SELECT * FROM EXPENSES WHERE USERID=? AND MONTH(date)=MONTH(DATE(NOW()))"
    stmt1 = ibm_db.prepare(conn, sql1)
    ibm_db.bind_param(stmt1, 1, session["id"])
    ibm_db.execute(stmt1)
    list2 = []
    expense1 = ibm_db.fetch_tuple(stmt1)
    while expense1:
        list2.append(expense1)
        expense1 = ibm_db.fetch_tuple(stmt1)
    total = 0
    for x in list2:
        total += x[4]

    sql2 = "SELECT EXPLIMIT FROM LIMITS ORDER BY LIMITS.ID DESC LIMIT 1"
    stmt2 = ibm_db.prepare(conn, sql2)
    ibm_db.execute(stmt2)
    limit = ibm_db.fetch_tuple(stmt2)

    if len(limit) > 0 and total < limit[0]:
        sendEmail(session["email"])
    return redirect("/display")


def sendEmail(reciver):

    sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)
    # Change to your verified sender
    from_email = Email("nishanths.19cse@kongu.edu")
    # to_email = To(session["email"])  # Change to your recipient
    to_email = To(reciver)  # Change to your recipient
    subject = "Expense Alert Limit"
    content = Content(
        "text/plain", "Dear User, You have exceeded the specified monthly expense Limit!!!!")
    mail = Mail(from_email, to_email, subject, content)

    # Get a JSON-ready representation of the Mail object
    mail_json = mail.get()

    # Send an HTTP POST request to /mail/send
    response = sg.client.mail.send.post(request_body=mail_json)
    print(response.status_code)
    print(response.headers)
@app.route("/reward")
def reward():
    sql = "SELECT AMOUNT FROM EXPENSES WHERE USERID=? AND MONTH(date)=MONTH(DATE(NOW()))"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, session["id"])
    ibm_db.execute(stmt)
    fetchedamount = ibm_db.fetch_tuple(stmt)
    point = 0
    for i in fetchedamount:
        point = point + i
    sql1 = "SELECT EXPLIMIT FROM LIMITS WHERE USERID=?"
    stmt1 = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt1, 1, session["id"])
    limit = ibm_db.fetch_tuple(stmt)
    for i in limit:
        print(i)
        limit = i
    creditpoint = (point/10000)*100
    creditpoint = 100-creditpoint
    return render_template("reward.html",point=creditpoint)
@app.route("/display")
def display():
    print(session["username"], session["id"])
    sql = "SELECT * FROM EXPENSES WHERE USERID=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, session["id"])
    ibm_db.execute(stmt)
    list1 = []
    row = ibm_db.fetch_tuple(stmt)
    while row:
        list1.append(row)
        row = ibm_db.fetch_tuple(stmt)
    print(*list1, sep="\n")
    total = 0
    t_food = 0
    t_entertainment = 0
    t_business = 0
    t_rent = 0
    t_EMI = 0
    t_other = 0

    for x in list1:
        total += x[4]
        if x[6] == "food":
            t_food += x[4]
        elif x[6] == "entertainment":
            t_entertainment += x[4]
        elif x[6] == "business":
            t_business += x[4]
        elif x[6] == "rent":
            t_rent += x[4]
        elif x[6] == "EMI":
            t_EMI += x[4]
        elif x[6] == "other":
            t_other += x[4]

    return render_template(
        "display.html",
        expense=list1,
        total=total,
        t_food=t_food,
        t_entertainment=t_entertainment,
        t_business=t_business,
        t_rent=t_rent,
        t_EMI=t_EMI,
        t_other=t_other,
    )


# delete---the--data


@app.route("/delete/<string:id>", methods=["POST", "GET"])
def delete(id):
    print(id)
    sql = "DELETE FROM expenses WHERE  id =?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, id)
    ibm_db.execute(stmt)

    return redirect("/display")


# UPDATE---DATA


@app.route("/edit/<id>", methods=["POST", "GET"])
def edit(id):

    sql = "SELECT * FROM expenses WHERE  id =?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, id)
    ibm_db.execute(stmt)
    row = ibm_db.fetch_tuple(stmt)

    print(row)
    return render_template("edit.html", expenses=row)


@app.route("/update/<id>", methods=["POST"])
def update(id):
    if request.method == "POST":

        date = request.form["date"]
        expensename = request.form["expensename"]
        amount = request.form["amount"]
        paymode = request.form["paymode"]
        category = request.form["category"]
        time = request.form["time"]

        sql = "UPDATE expenses SET date =? , expensename =? , amount =?, paymentmode =?, category =?, time=? WHERE expenses.id =? "
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, date)
        ibm_db.bind_param(stmt, 2, expensename)
        ibm_db.bind_param(stmt, 3, amount)
        ibm_db.bind_param(stmt, 4, paymode)
        ibm_db.bind_param(stmt, 5, category)
        ibm_db.bind_param(stmt, 6, time)
        ibm_db.bind_param(stmt, 7, id)
        ibm_db.execute(stmt)

        print("successfully updated")
        return redirect("/display")


# limit


@app.route("/limit")
def limit():
    return redirect("/limitn")


@app.route("/limitnum", methods=["POST"])
def limitnum():
    if request.method == "POST":
        number = request.form["number"]

        sql = "INSERT INTO LIMITS(USERID,EXPLIMIT) VALUES(?,?)"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, session["id"])
        ibm_db.bind_param(stmt, 2, number)
        ibm_db.execute(stmt)
        return redirect("/limitn")


@app.route("/limitn")
def limitn():

    sql = "SELECT EXPLIMIT FROM LIMITS ORDER BY LIMITS.ID DESC LIMIT 1"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.execute(stmt)
    row = ibm_db.fetch_tuple(stmt)

    return render_template("limit.html", y=row)


# REPORT


@app.route("/today")
def today():

    sql = "SELECT * FROM expenses  WHERE userid =? AND date = DATE(NOW())"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, session["id"])
    ibm_db.execute(stmt)
    list2 = []
    texpense = ibm_db.fetch_tuple(stmt)
    print(texpense)

    sql = "SELECT * FROM EXPENSES WHERE USERID=? AND DATE(date) = DATE(NOW())"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, session["id"])
    ibm_db.execute(stmt)
    list1 = []
    expense = ibm_db.fetch_tuple(stmt)
    while expense:
        list1.append(expense)
        expense = ibm_db.fetch_tuple(stmt)

    total = 0
    t_food = 0
    t_entertainment = 0
    t_business = 0
    t_rent = 0
    t_EMI = 0
    t_other = 0

    for x in list1:
        total += x[4]
        if x[6] == "food":
            t_food += x[4]

        elif x[6] == "entertainment":
            t_entertainment += x[4]

        elif x[6] == "business":
            t_business += x[4]
        elif x[6] == "rent":
            t_rent += x[4]

        elif x[6] == "EMI":
            t_EMI += x[4]

        elif x[6] == "other":
            t_other += x[4]

    return render_template(
        "today.html",
        texpense=list1,
        expense=expense,
        total=total,
        t_food=t_food,
        t_entertainment=t_entertainment,
        t_business=t_business,
        t_rent=t_rent,
        t_EMI=t_EMI,
        t_other=t_other,
    )


@app.route("/month")
def month():

    sql = "SELECT MONTHNAME(DATE),SUM(AMOUNT) FROM EXPENSES WHERE USERID=? GROUP BY MONTHNAME(DATE)"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, session["id"])
    ibm_db.execute(stmt)
    list2 = []
    texpense = ibm_db.fetch_tuple(stmt)
    while texpense:
        list2.append(texpense)
        texpense = ibm_db.fetch_tuple(stmt)
    print(list2)

    sql = "SELECT * FROM EXPENSES WHERE USERID=? AND MONTH(date)=MONTH(DATE(NOW()))"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, session["id"])
    ibm_db.execute(stmt)
    list1 = []
    expense = ibm_db.fetch_tuple(stmt)
    while expense:
        list1.append(expense)
        expense = ibm_db.fetch_tuple(stmt)

    total = 0
    t_food = 0
    t_entertainment = 0
    t_business = 0
    t_rent = 0
    t_EMI = 0
    t_other = 0

    for x in list1:
        total += x[4]
        if x[6] == "food":
            t_food += x[4]

        elif x[6] == "entertainment":
            t_entertainment += x[4]

        elif x[6] == "business":
            t_business += x[4]
        elif x[6] == "rent":
            t_rent += x[4]

        elif x[6] == "EMI":
            t_EMI += x[4]

        elif x[6] == "other":
            t_other += x[4]

    print(total)

    print(t_food)
    print(t_entertainment)
    print(t_business)
    print(t_rent)
    print(t_EMI)
    print(t_other)

    return render_template(
        "month.html",
        texpense=list2,
        expense=expense,
        total=total,
        t_food=t_food,
        t_entertainment=t_entertainment,
        t_business=t_business,
        t_rent=t_rent,
        t_EMI=t_EMI,
        t_other=t_other,
    )

@app.route("/year")
def year():

    sql = (
        "SELECT YEAR(DATE),SUM(AMOUNT) FROM EXPENSES WHERE USERID=? GROUP BY YEAR(DATE)"
    )
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, session["id"])
    ibm_db.execute(stmt)
    list2 = []
    texpense = ibm_db.fetch_tuple(stmt)
    while texpense:
        list2.append(texpense)
        texpense = ibm_db.fetch_tuple(stmt)
    print(list2)

    sql = "SELECT * FROM EXPENSES WHERE USERID=? AND YEAR(date)=YEAR(DATE(NOW()))"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, session["id"])
    ibm_db.execute(stmt)
    list1 = []
    expense = ibm_db.fetch_tuple(stmt)
    while expense:
        list1.append(expense)
        expense = ibm_db.fetch_tuple(stmt)

    total = 0
    t_food = 0
    t_entertainment = 0
    t_business = 0
    t_rent = 0
    t_EMI = 0
    t_other = 0

    for x in list1:
        total += x[4]
        if x[6] == "food":
            t_food += x[4]

        elif x[6] == "entertainment":
            t_entertainment += x[4]

        elif x[6] == "business":
            t_business += x[4]
        elif x[6] == "rent":
            t_rent += x[4]

        elif x[6] == "EMI":
            t_EMI += x[4]

        elif x[6] == "other":
            t_other += x[4]

    print(total)

    print(t_food)
    print(t_entertainment)
    print(t_business)
    print(t_rent)
    print(t_EMI)
    print(t_other)

    return render_template(
        "year.html",
        texpense=list2,
        expense=expense,
        total=total,
        t_food=t_food,
        t_entertainment=t_entertainment,
        t_business=t_business,
        t_rent=t_rent,
        t_EMI=t_EMI,
        t_other=t_other,
    )


# log-out


@app.route("/logout")
def logout():
    session.pop("loggedin", None)
    session.pop("id", None)
    session.pop("username", None)
    session.pop("email", None)
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)
