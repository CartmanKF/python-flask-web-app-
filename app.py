from unicodedata import name
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

# importladığımız bazı kütüphanelerin özellikleri
#render_template html ile kodları yazabilmemizi sağlıyor
#redirect sayfalara yönlendirmemize yarıyor
#url_for örneğin eğer giriş yapıldıysa ana sayfaya gönder tarzında komutların bulunduğı bir kütüphane
#flash örneğin yanlış kullanıcı adı ve şifreyle giriş yaptığımızda çıkan uyarıların güzel gözükmesini sağlayan eklentilerin olduğu bir kütüphane
#session sayfayı yenilesek bile çıkış yapmadığımız sürece hala giriş yapılı kalmamızı sağlayan kodların olduğu kütüphane

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

@app.errorhandler(404)
def error(e):
    return render_template('404.html')

if __name__ == "__main__":
    if not os.path.exists(DB_NAME):
        db.create_all(app=app)
        print("Database oluşturuldu!")
 #databasei ilk oluştururken bize mesaj yazsın istedik
    app.debug = True
    app.run()
