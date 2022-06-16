from flask import Flask, render_template, url_for, redirect, request, session
import pyrebase as fire
from datetime import timedelta, time, datetime


firebaseConfig = {
  'apiKey': "AIzaSyC1eB-OAHVH9XDQtM3dXPsLjfdSvaljf-Y",
  'authDomain': "webapp-90203.firebaseapp.com",
  'projectId': "webapp-90203",
  'storageBucket': "webapp-90203.appspot.com",
  'messagingSenderId': "546692304106",
  'appId': "1:546692304106:web:3a78427ad44d680578db93",
  'measurementId': "G-GDN6T6KBJE",
  'databaseURL': "https://webapp-90203-default-rtdb.asia-southeast1.firebasedatabase.app"
}

firebase = fire.initialize_app(firebaseConfig)

db = firebase.database()
auth = firebase.auth()



app = Flask(__name__)
app.secret_key = "aman"
app.permanent_session_lifetime = timedelta(days=30)


# +++++++++++FUNCTIONS++++++++++++++
def add_user(user,name,email,passwd):
  data = {'id':user['userId'],'name':name,'email':email,'passwd':passwd}
  db.child("user").child(user['userId']).set(data)

def add_blog(userId,title,url,body):
  now = datetime.now()
  status = now.strftime("%H:%M:%S")
  data = {'title':title, 'body':body, 'status':status, 'userId':userId, 'url':url }
  db.child('blog').push(data)



@app.route("/")
def home():
  if "email" in session:
    return render_template("home.html", login = "false", logout = "true", home_mode = "active" ,)
  else:
    return render_template("home.html", login = "true", logout = "false", home_mode = "active" )

@app.route("/sahid")
def sahid():
  if "email" in session:
    return render_template("sahid.html", login = "false", logout = "true", home_mode = "active" ,)
  else:
    return render_template("sahid.html", login = "true", logout = "false", home_mode = "active" )


@app.route("/login", methods=["GET","POST"])
def login():
  user = dict()
  user['userId'] = None
  if request.method == "POST":
    try:
      session.permanent = True
      email = request.form["email"]
      passwd = request.form["passwd"]
      user = auth.sign_in_with_email_and_password(email,passwd)
      user = auth.refresh(user['refreshToken'])
      if user['userId'] != None:
        session['email'] = email
        session['user'] = user
        session['userId'] = user['userId']
        if 'name' in session:
          add_user(user,session['name'],email,passwd)
        # true mean visible false mean in visible
        return redirect(url_for("home"))
    
      else:
        return render_template('login.html',login = "true", logout="false", auth = 'true')
    except Exception as e:
      # returing the reason for login fialed
      print(e)
      return render_template("login.html", login = 'true', logout ='false', f_message="invalid username or password", auth = "true")

  else:
    return render_template("login.html", login = "true", logout="false", auth = 'false')

@app.route("/tool")
def tool():
  if 'email' in session:
    return render_template("tool.html", blog_mode='', home_mode ="", tool_mode = "active", login='false', logout='true')
  else:
    return render_template("tool.html",login = 'true', logout = 'false', tool_mode = "active")

@app.route("/logout")
def logout():
  session.pop('email',None)
  return redirect(url_for("home"))


@app.route("/sign-in", methods=['GET', 'POST'])
def signin():
  try:
    if request.method == 'POST':
      email = request.form['email']
      name = request.form['name']
      
      passwd = request.form['passwd']
      con_passwd = request.form['con_passwd']
      if passwd == con_passwd:
        user = auth.create_user_with_email_and_password(email, passwd)
        session['name'] = name
        return redirect(url_for("login")) 

      else:
        return render_template("signin.html",login = "true", f_message = "password not match....", logout="false", auth = 'true' )
  except Exception as e:
    
    return render_template("signin.html",login = "true", f_message = "signin error ...", logout="false", auth = 'true' )

  return render_template("signin.html",login = "true", logout="false", auth = 'false')

@app.route("/profile")
def profile():
  data = db.child('user').child(session['userId']).get().val()
  session['name'] = data['name']
  session['email'] = data['email']
  session['passwd']=data['passwd']
  return render_template("profile.html" , edit = "false", login = 'false', logout = 'true', edit_cancel = "true", name = session['name'], email = session['email'])


@app.route("/edit", methods=['GET', 'POST'])
def edit():
  if request.method == 'POST':
    session['name'] = request.form['edit_name']
    add_user(session['user'],session['name'],session['email'],session['passwd'])

    return render_template("profile.html" , edit = "false", login = 'false', logout = 'true', edit_cancel = "true", name = session['name'], email = session['email'])

  return render_template("profile.html", login = 'false', logout = 'true', edit = "true", edit_cancel = "false", name = session['name'], email = session['email'])

@app.route("/addblog" , methods=['GET', 'POST'])
def addblog():
  if 'email' in session:
    if request.method == 'POST' :
      title = request.form['title']
      body = request.form['body']
      url = ""

      add_blog(session['userId'],title,url,body)
      return render_template("addblog.html", login = "false", logout = "true", addblog_mode = "active"  )
    else:
      return render_template("addblog.html", login = "false", logout = "true", addblog_mode = "active")
  else:
    return "<h1>NOT AUTHORIESD ! </h1>"

@app.route("/blog")
def blog():
  data = db.child("blog").get().val()
  data = dict(data)
  if "email" in session:
    return render_template("blog.html", login = "false", logout = "true", blog_mode = "active" , blog_list = data )
  else:
    return render_template("blog.html", login = "true", logout = "false", blog_mode = "active", blog_list = data )



@app.route("/forget", methods = ["GET", "POST"] )
def forget():
  if request.method == "POST":
    try:
      email = request.form["email"]
      auth.send_password_reset_email(email)
      return render_template("forget.html", login = 'false', logout = 'true', f_message="email send")
    except:
      return render_template("forget.html", login = 'false', logout = 'true', f_message="email not found")

  return render_template("forget.html", login = 'false', logout = 'true')





if __name__ == "__main__":
  pass
'''
@app.route("/form", methods=['GET','POST'])

def form():
  if request.method == 'POST':
    usr = request.form["usr"]
    return redirect(url_for("result" , usr = usr))
  
  else:
    return render_template("form.html")

@app.route("/genpdf/<usr>")
def result(usr):
  return f"{usr} form submited"
'''

app.run(host="0.0.0.0", debug=False)