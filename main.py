from flask import Flask, render_template, request, flash, session, redirect, send_from_directory
from database.models import *
import os
from utils import model_converter


app = Flask(__name__)
app.config['SECRET_KEY'] = "45efsgdg5g45gf4de5gf"


@app.route('/home')
@app.route('/')
def home_page():
    logged = session.get('userLogged', False)
    admin = session.get('userAdmin', False)
    return render_template('home.html', logged=logged, admin=admin)


@app.route('/about')
def about_page():
    admin = session.get('userAdmin', False)
    logged = session.get('userLogged', False)
    data = About.select()
    about = model_converter(data)
    return render_template('about.html', logged=logged, admin=admin, about=about)


@app.route('/articles')
def article_page():
    admin = session.get('userAdmin', False)
    data = Articles.select()
    articles = model_converter(data)
    logged = session.get('userLogged', False)
    return render_template('articles.html', articles=articles, logged=logged, admin=admin)


@app.route('/contact')
def contact_page():
    admin = session.get('userAdmin', False)
    logged = session.get('userLogged', False)
    return render_template('contact.html', logged=logged, admin=admin)


@app.route("/registration", methods=['POST', 'GET'])
def registration_page():
    if request.method == "POST":
        name, username, password1, password2 = request.form.values()

        if password1 == password2:
            Users.create(
                name=name,
                username=username,
                password=password1
            )
            flash("You are registed!", category="success")
        else:
            flash("Passwords are not the same!", category="danger")

    return render_template('registration.html')


@app.route("/login", methods=['POST', 'GET'])
def login_page():
    if request.method == "POST":
        username, password = request.form.values()
        data = Users.select().where(Users.username == username)
        result = model_converter(data)
        if result[0]["status"] == True:
            session['userAdmin'] = username
        else:
            session['userAdmin'] = False

        if len(result) == 0:
            flash("Password or log-in wrong!", category="danger")
        else:
            if result[0]["password"] == password:
                session['userLogged'] = username
                return redirect('/')
            else:
                flash("Password or log-in wrong!", category="danger")

    return render_template('log-in.html')


@app.route("/logout")
def logout():
    session['userLogged'] = False
    return redirect('/login')


@app.route("/admin")
def admin():
    logged = session.get('userLogged', False)
    admin = session.get('userAdmin', False)

    return render_template('admin.html', logged=logged, admin=admin)


@app.route('/media/<filename>')
def get_image(filename):
    return send_from_directory('media', filename)


@app.route('/delete_post/<article_id>')
def delete_post(article_id):
    data = Articles.select().where(Articles.id == article_id)
    article = model_converter(data)
    img = article[0]['photo']
    os.remove(img)
    Articles.delete_by_id(article_id)
    return redirect('/articles')


@app.route('/article_detail/<article_id>')
def article_detail(article_id):
    logged = session.get('userLogged', False)
    admin = session.get('userAdmin', False)
    data = Articles.select().where(Articles.id == article_id)
    article = model_converter(data)
    # print(request.remote_addr)

    return render_template('article_detail.html', article=article[0], logged=logged, admin=admin)


@app.route('/admin/article', methods=['POST', 'GET'])
def article_admin():
    logged = session.get('userLogged', False)
    admin = session.get('userAdmin', False)
    article_title = "Article"

    if request.method == 'POST':
        title, description = request.form.values()

        image_file = request.files.get('img', None)

        if image_file:
            filename = image_file.filename
            image_file.save(f"media/{filename}")

        Articles.create(
            title=title,
            description=description,
            photo=(f"media/{filename}")
        )
        return redirect('/admin/article')

    return render_template('admin.html', article_title=article_title, logged=logged, admin=admin)


@app.route('/admin/about', methods=['POST', 'GET'])
def about_admin():
    logged = session.get('userLogged', False)
    admin = session.get('userAdmin', False)
    about_title = "About"

    if request.method == 'POST':
        title, description = request.form.values()

        image_file = request.files.get('img', None)

        if image_file:
            filename = image_file.filename
            image_file.save(f"media/{filename}")

        data = About.select().where(About.id == 1)
        about = model_converter(data)
        img = about[0]['photo']
        os.remove(img)
        About.delete_by_id(1)
        About.create(
            title=title,
            description=description,
            photo=(f"media/{filename}")
        )
        return redirect('/admin/about')

    return render_template('admin.html', about_title=about_title, logged=logged, admin=admin)


@app.route('/admin/admin_list', methods=['GET', 'POST'])
def admin_list():
    logged = session.get('userLogged', False)
    admin = session.get('userAdmin', False)

    if request.method == 'POST':
        Users.update(status=False).execute()

        for item in request.form.keys():
            user_id = item.split('_')[-1]
            Users.update(status=True).where(Users.id == user_id).execute()
        
        data = Users.select().where(Users.username == logged)
        result = model_converter(data)
        if result[0]['status'] == False:
            admin = session.pop('userAdmin', False)
            print(admin)
            return redirect('/home')

        return redirect('/admin/admin_list')

    admin_title = "Admins"
    data = Users.select()
    admin_dict = model_converter(data)

    return render_template('admin.html', admin_title=admin_title, logged=logged, admin=admin, admins=admin_dict)





if __name__ == '__main__':
    from database import models
    app.run(debug=True)
