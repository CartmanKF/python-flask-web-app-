from importlib.resources import Resource
from inspect import Parameter
from lib2to3.pgen2.token import DOUBLESTAR
from math import radians
from unicodedata import name
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy
import sqlite3
import time
import json
import plotly
import plotly.express as px
import datetime as dt
import matplotlib.animation as animation
import random
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import style
import os
import pandas as pd
import urllib
import re
import urllib.request
from datetime import date, datetime
import socket, time, requests
from bs4 import BeautifulSoup #html ve xml dosyalarını işlememizi sağlayan kütüphane


# importladığımız bazı kütüphanelerin özellikleri
#render_template html ile kodları yazabilmemizi sağlıyor
#redirect sayfalara yönlendirmemize yarıyor
#url_for örneğin eğer giriş yapıldıysa ana sayfaya gönder tarzında komutların bulunduğı bir kütüphane
#flash örneğin yanlış kullanıcı adı ve şifreyle giriş yaptığımızda çıkan uyarıların güzel gözükmesini sağlayan eklentilerin olduğu bir kütüphane
#session sayfayı yenilesek bile çıkış yapmadığımız sürece hala giriş yapılı kalmamızı sağlayan kodların olduğu kütüphane
print("merhaba")
app = Flask(__name__)
app.secret_key = "super secret key"
#secret key cookilerin yönetilmesinde işe yarıyor

DB_NAME = 'todolist.db'
#databasemizin ismini belirlediğimiz yer

app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{DB_NAME}"
db = SQLAlchemy(app)
#sqlacademyi eklediğimiz yer

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    surname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    tasks = db.relationship('Tasks', backref='görevli')

    def __repr__(self):
        return f"{self.name} - {self.surname} - {self.email} - {self.password}"
# tek tek ilk tablomuzdaki başlıkları girdiğimiz yer

    def __repr__(self):
        return self.name + " " + self.surname

class Tasks(db.Model):
     id = db.Column(db.Integer, primary_key=True)
     task = db.Column(db.String(300), nullable=False)
     detail = db.Column(db.Text)
     howmanydays = db.Column(db.Text, nullable=False)
     date_added = db.Column(db.DateTime, default=datetime.utcnow)
     gorevli_id = db.Column(db.Integer, db.ForeignKey('users.id'))
  #2. tabloyu oluşturduğumuz yer ayrıca foreign key olarak ilk tablodaki users idyide ekledik.
@app.route("/delete/<int:Tasks_id>",methods=["GET"])
def delete(Tasks_id):
    task = Tasks.query.filter_by(id=Tasks_id).first()
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("listelerim"))

#web api denemesi örneğin http://10.90.14.199/?isim=volkan yazdığımızda karşımıza data: volkan olarak direkt geliyor

""" @app.route("/") 
def baslangic_api():
    isim = request.args.get("isim")
    return jsonify(data= isim),200   """ 

@app.route("/")
def home():
    # home pagemizin ana kodlarının olduğu yer login yaptıktan sonra id ile eşleştirerek sadece kendi görevlerini görmelerini sağladık
    if 'email' in session:
        email = session['email']
        me = Users.query.filter_by(email=email).first()
        gid = Users.query.filter_by(email=email).first()
        tasks = Tasks.query.filter_by(gorevli_id=gid.id)
        return render_template('home.html', me=me, tasks=tasks)
    return redirect(url_for('login'))

@app.route("/register", methods=["GET", "POST"])
def register():
    # register kısmının ana komutları burda request.form.get ile verileri database'e işledik
    if request.method == "POST":
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        password = request.form.get('password')
    
        search = Users.query.filter_by(email=email).first()

        if search != None:
            flash('Bu email ile bir hesap zaten var')
            return render_template('register.html')

        new_user = Users(name=name, surname=surname, 
                         email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if 'email' in session:
        return redirect(url_for('home'))

    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        search = Users.query.filter_by(email=email).first()

        if search is None:
            flash("Düzgün gir şunları!!") 
            return render_template('login.html')

        if password == search.password:
            session['email'] = email
            return redirect(url_for('home'))
    return render_template('login.html')


@app.route("/logout")
def logout():
    session.pop("email", None)
    return redirect(url_for('login'))

##############################  VERİ TABANINA DIŞARDAN VERİ GİRİLMESİNİ SAĞLADIĞIMIZ KISIM  ####################################



@app.route("/create", methods=["GET",  "POST"])
def create():
    if 'email' in session:
        email = session['email']
        me = Users.query.filter_by(email=email).first()
        if request.method == "POST":
            task = request.form.get("task")
            detail = request.form.get("detail")
            howmanydays = request.form.get("howmanydays")
            new_task = Tasks(task=task,detail=detail,howmanydays=howmanydays,gorevli_id=me.id)
            db.session.add(new_task)
            db
            db.session.commit()
            return redirect(url_for('home'))
    return render_template('create.html') 

@app.route("/listelerim")
def listelerim():
    if 'email' in session:
        email = session['email']
        me = Users.query.filter_by(email=email).first()
        gid = Users.query.filter_by(email=email).first()
        tasks = Tasks.query.filter_by(gorevli_id=gid.id)
        return render_template('listelerim.html', me=me, tasks=tasks)
    return redirect(url_for('login'))  


##############################  404 PAGE  ####################################


@app.errorhandler(404)
def error(e):
    return render_template('404.html')



if __name__ == "__main__":
    if not os.path.exists(DB_NAME):
        db.create_all(app=app)
        print("Database oluşturuldu!")
 #databasei ilk oluştururken bize mesaj yazsın istedik
    app.debug = True




##############################  DOLARIN VERİSİNİ BEAUTIFUL SOUP KULLANARAK SCRAPPLEDİĞİNMİZ VE EKRANDA GÖSTEDİĞİMİZ KISIM  ####################################

@app.route("/doviz")

def doviz():
    if 'email' in session:
        url = "https://www.doviz.com"
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        data1 = soup.find("span", {"data-socket-key":"USD"}).text
        return data1
    return redirect(url_for('login')) 




##############################  DOLARIN KURUNU VE ZAMANINI VERİ TABANINA İŞLEDİĞİMİZ KISIM  ####################################


con=sqlite3.connect('kur.db')
cur=con.cursor()
      
cur.execute('''CREATE TABLE IF NOT EXISTS dolar_kur (
            dolar float, time STR
            ) ''')

time = dt.datetime.now()
url = "https://www.doviz.com"
r = requests.get(url)
soup = BeautifulSoup(r.content, "html.parser")
data1 = soup.find("span", {"data-socket-key":"USD"}).text.replace(",", ".")
cur.execute("insert into dolar_kur values (?, ?)", [data1, str(time)])
con.commit()
con.close()
# import time as t
# t.sleep(60) metodunu veri tabanına hangi sıklıkla veri yazıcağını belirlemek için kullanabiliriz
print("\n\n------------------\nyenileme\n----------------\n\n")

##############################          PLOTLY KULLANARAK DOLAR GRAFİĞİ ÇİZDİRDİĞİMİZ KISIM           ####################################

@app.route("/index")
def index():
    if 'email' in session:
        email = session['email']
        me = Users.query.filter_by(email=email).first()
        gid = Users.query.filter_by(email=email).first()
        tasks = Tasks.query.filter_by(gorevli_id=gid.id)
        con=sqlite3.connect(r"C:\Users\CartmanKF\Documents\GitHub\flask web app 2. deneme\kur.db")
        sql = """SELECT * FROM dolar_kur WHERE dolar"""
        df = pd.read_sql(sql, con)
        
        fig = px.line(df, x='time', y='dolar',line_shape='spline')
        fig.update_traces(line=dict(color='blue', width=4), marker=dict(color='red', size=10))
        fig.update_layout(autotypenumbers='convert types')
        fig.update_yaxes(tickformat = ".3f", autorange='reversed')

        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return render_template('index.html', graphJSON=graphJSON, me=me, tasks=tasks, df=df,)
    return redirect(url_for('login'))  


##############################          UYGULAMA OLARAK GRAFİK ÇIKARTMA KISMI          ####################################


#con=sqlite3.connect(r"C:\Users\CartmanKF\Documents\GitHub\flask web app 2. deneme\kur.db")
 
#sql = """SELECT * FROM dolar_kur WHERE dolar"""
 
#data = pandas.read_sql(sql, con)

#plt.plot(data.time,data.dolar, label = "dolar")
#plt.legend()
#plt.title("DOLAR KUR DEGISIMI")
#plt.show()
#print("son")

##############################          WEB SERVİCE KISMI            ####################################

#for veritabanında ne var ne yok göstermek için yazdığım kod

class GetUsers(Resource):
    def get(self):
        users = Users.query.all()
        todolist_list = []
        for todolist in users:
            todolist_data = {'Id': todolist.id, 'Name': todolist.name, 
            'Surname': todolist.surname, 'Email': todolist.email, 'Password': todolist.password}
            todolist_list.append(todolist_data)
        return {"Users": todolist_list}, 200

#for veritabanında herhangi bir veri eklemek için yazdığım kod

class AddUsers(Resource):
    def post(self):
        if request.is_json:
            todolist = Users(name=request.json['Name'], surname=request.json['Surname'], email=request.json['Email'], password=request.json['Password'],)

            db.session.add(todolist)
            db.session.commit()
            return make_response(jsonify({'Id': todolist.id, 'Name': todolist.name, 'Surname': todolist.surname, 'Email': todolist.email, 'Password': todolist.password}))
        else:
            return{'error': 'Request must be JSON'}, 400

# veritabanındaki herhangi bir veriyi güncellemek için yazdığım kod http://localhost:5000/update/?
class UpdateEmployee(Resource):
    def put(self, id):
        if request.is_json:
            todolist = Users.query.get(id)
            if todolist is None:
                return {'error': 'not found'}, 404
            else:
                todolist.name = request.json['Name']
                todolist.surname = request.json['Surname']
                todolist.email = request.json['Email']
                todolist.password = request.json['Password']
                todolist.session.commit()
                return 'Updated', 200
        else:
            return {'error': 'Request must be JSON'}, 400

# veritabanındaki herhangi bir veriyi silmek için yazdığım kod http://localhost:5000/delete/?
class DeleteEmployee(Resource):
    def delete(self, id):
        todolist = Users.query.get(id)
        if todolist is None:
            return {'error': 'not found'}, 404
        db.session.delete(todolist)
        db.session.commit()
        return f'{id} is deleted', 200

# / tanımladığımız classların hangi text ile çağırılacaını belirlediğimiz yer
api = Api(app)
api.add_resource(GetUsers, '/get')
api.add_resource(AddUsers, '/add')
api.add_resource(UpdateEmployee, '/update/<int:id>')
api.add_resource(DeleteEmployee, '/delete/<int:id>')



#app.run(host='0.0.0.0', port=80)

app.run()