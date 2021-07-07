from os import error
import re
from flask import Flask, render_template, request,redirect,url_for,session
import pyodbc


server = 'tcp:adbsaahilserver.database.windows.net'
database = 'sqldatabase1'
username = 'serveradmin'
password = 'Spa12345'

cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)


app = Flask(__name__)
app.secret_key = 'any random string'

@app.route('/', methods=["POST", "GET"])
def login():
    if request.method == "POST":
            if request.form.get("lbutton"):
                uname = request.form["uname"]
                session['username'] = uname
                return redirect('/main')
                
    else: 
        return render_template('login.html')

@app.route('/main', methods=["POST", "GET"])
def student():

        if 'username' in session:
            user = session['username']

            cursor = cnxn.cursor()
            cursor.execute("select * from qna where answers is null")
            search = cursor.fetchall()

            return render_template('main.html', rows=search ,item1='Questions',item2='Click',user=user)
        else:
            return render_template('login.html')

@app.route('/answers/<string:id_data>', methods = ['GET','POST'])

def answser(id_data):

    if request.method == "POST":
        if request.form.get("ansbutton"):
            user = session['username']
            ans = request.form["anstxt"]

            cursor = cnxn.cursor()
            cursor.execute("select teacher, questions from qna where id = '"+id_data+"'")
            one = cursor.fetchone()

            cursor = cnxn.cursor()
            cursor.execute("insert into qna (teacher, questions, answers,student) values ('"+one[0]+"','"+one[1]+"','"+ans+"','"+user+"')")
            cnxn.commit()
            return redirect('/main')
        else:
            return render_template('answers.html')

    else:
        if 'username' in session:
            user = session['username']

            cursor = cnxn.cursor()
            cursor.execute("select questions from qna where id = '"+id_data+"'")
            one = cursor.fetchone()

            cursor = cnxn.cursor()
            cursor.execute("select questions from qna where questions = '"+one[0]+"' and student = '"+user+"'")
            search = cursor.fetchone()
            
            if str(search) != 'None':
                return render_template("already.html")

            else:
                return render_template('answers.html',ques=one[0],user=user,id=id_data)
        else:
            return render_template('login.html')


@app.route('/check', methods=["POST", "GET"])
def check():

        if 'username' in session:
            user = session['username']

            cursor = cnxn.cursor()
            cursor.execute("select teacher, questions, answers, grades from qna where grades is not null and student = '"+user+"'")
            search = cursor.fetchall()

            cursor = cnxn.cursor()
            cursor.execute("select sum(grades) from qna where grades is not null and student = '"+user+"'")
            total = cursor.fetchone()

            cursor = cnxn.cursor()
            cursor.execute("select count(*) from qna where grades is not null and student = '"+user+"'")
            count = cursor.fetchone()

            if str(total[0]) != 'None' and str(count[0]) != 'None':
                avggrd = int(total[0])/int(count[0])
            
            else:
                avggrd='WAIT FOR TEACHER TO GRADE'

            return render_template('checkgrade.html', rows=search ,item1='teacher',item2='questions',item3='answers',item4='grades',user=user,avggrd=str(avggrd))
        else:
            return render_template('login.html')


@app.route('/logout', methods=["POST", "GET"])
def logout():

    session.pop('username', None)

    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug =True, host='0.0.0.0')