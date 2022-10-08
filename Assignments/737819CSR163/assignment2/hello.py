from multiprocessing.dummy import connection
from flask import Flask, url_for,redirect,request,render_template
import sqlite3 as sql
app = Flask(__name__)
@app.route("/")
def main():
    return render_template("index.html")
@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/signup",methods=['GET', 'POST'])
def singup():
    if request.method=='POST':
        try:
            name=request.form['name']
            email=request.form['email']
            password=request.form['password']
            with sql.connect("database.db") as con:
                cur=con.cursor()
                cur.execute("INSERT INTO register(name,email,password) values(?,?,?)",(name,email,password))
                print("successfully")
                print(cur.execute("SELECT * from register").fetchall())
                con.commit()
            return render_template("signin.html")
        except sql.Error as error:
            print(error)
            con.rollback()
        finally:
            con.close()
    return render_template('signup.html')
@app.route("/signin",methods=['POST','GET'])
def sign_in():
    error=[]
    if request.method=='POST':
        try:
            email=request.form['email']
            password=request.form['password']
            with sql.connect("database.db") as con:
                cur=con.cursor()
                print(cur.execute("SELECT * from register").fetchall())
                p=cur.execute("SELECT * from register where email=? and password=?",(email,password)).fetchall()
                if len(p)!=0:
                    return render_template('index.html')
                else:
                    error.append("enter the correct name and email")
                    return render_template('signin.html',error=error) 
        except sql.Error as error:
            print(error)
            con.rollback()
        finally:
            con.close()
    return render_template('signin.html')
if __name__ == '__main__':
    app.run(debug=True)