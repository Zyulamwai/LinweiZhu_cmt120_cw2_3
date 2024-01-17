from flask import Flask,redirect,url_for,render_template,request, session, flash, current_app, jsonify
from comUtils import db , require_login, require_admin
from models import User, Blog, Comment, Contact
from flask_migrate import Migrate
from weather import get_cardiff_weather
import os

import config

app = Flask(__name__)
app.config.from_object(config)

db.init_app(app)
migrate = Migrate(app, db) 
#migrate.add_command('db', MigrateCommand)

@app.context_processor
def inject_category():
    CATEGORYS = ['Sport','Music', 'News', 'Travel', 'Technical']
    return dict(CATEGORYS = CATEGORYS)

# home page
@app.route('/',methods=['GET','POST'])
def home():
    return render_template('home.html')

@app.route('/base',methods=['GET','POST'])
def base():
    return render_template('base.html')

# add commment
@app.route('/addcontact', methods=['GET','POST'])
def addcontact():
    try:
        contact = Contact(
            username = request.form.get('username'),
            email = request.form.get('email'),
            subject = request.form.get('subject'),
            message = request.form.get('message'),
        )
        db.session.add(contact)
        db.session.commit()
        flash('Your message has been sent. Thank you!','success')
        return redirect(url_for("home") + "#contact")
    except Exception as e:
        print(e)
        flash('Sorry, there is a problem!','danger')
        return redirect(url_for("home") + "#contact")


#blog pages
@app.route('/blogs', defaults={'page':1})
@app.route('/blogs/<int:page>')
def blogs(page):
    try:
        paginate = Blog.query.order_by(Blog.id).paginate(page=page, per_page=app.config["PER_PAGE"], error_out=False)
        # print('hi')
        return render_template('blogs.html', blogs = paginate.items, paginate=paginate)
    except Exception as e:
        print(e)
        flash('No blog to show, please wait...','danger')
        return render_template('blogs.html', blogs=[])


#show blog detail by id
@app.route('/blog/<int:id>')
def blog(id):
    blog = Blog.query.get_or_404(id)
    comments = Comment.query.filter(Comment.blog_id == id).all()
    return render_template('blog.html', blog = blog, comments=comments)

################################################ User ###############################################

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = User.query.filter_by(email = email).first()
            if user:
                if user.password == password:
                    session['id'] = user.id
                    session['username'] = user.username
                    session['admin'] = user.admin
                    flash('Welcome {} !'.format(user.username),'success')
                    return redirect(url_for('blogs'))
                else:
                    flash('Password is incorrect, please check!', 'danger')
                    return redirect(url_for('login'))
            else:
                flash('Username not exists, please check!', 'danger')
                return redirect(url_for('login'))
        except Exception as e:
            print(e)
            flash('Sorry, there is a problem!','danger')
            return redirect(url_for('login'))
    else:
        return render_template("login.html")

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        repeat_password = request.form['repeat_password']
        email = request.form['email']

        if password != repeat_password:
            flash('Passwords do not match. Please try again!','danger')
            return redirect(url_for('register'))
        try: 
            user = User.query.filter_by(username = username).first()
            if user:
                flash('The username exists already!','danger')
                return redirect(url_for('register'))

            user = User.query.filter_by(email = email).first()
            if user:
                flash('The email exists already!','danger')
                return redirect(url_for('register'))
            else:
                user = User(username=username,
                            password=password,
                            email=email)
                db.session.add(user)
                db.session.commit()
                session['id'] = user.id
                session['username'] = username
                session['admin'] = user.admin
                flash('Welcome, {}!'.format(username),'success')
                return redirect(url_for('blogs'))
        except Exception as e:
            print(e)
            flash('Sorry, there is a problem!','danger')
            return redirect(url_for('register'))
    else:
        return render_template("register.html")

@app.route('/logout')
@require_login
def logout():
    session.clear()
    return redirect(url_for('home'))


# add commment
@app.route('/addcomment/<int:blog_id>', methods=['GET','POST'])
@require_login
def addcomment(blog_id):
    try:
        comment = Comment(
            comment = request.form.get('comment'),
            username = session.get('username'),
            blog_id = blog_id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Comment is posted','success')
        return redirect(url_for("blog", id=blog_id))
    except Exception as e:
        print(e)
        flash('Sorry, there is a problem!','danger')
        return redirect(url_for("blog", id=blog_id))


# ################################################ Admin part ###############################################
# blog full list
@app.route('/admin_blogs', defaults={'page':1})
@app.route('/admin_blogs/<int:page>')
@require_login
@require_admin
def admin_blogs(page):
    try:
        category = request.args.get('category')
        keyword = request.args.get('keyword')

        allquery = Blog.query
        if category:
            allquery = allquery.filter_by(category = category)
        if keyword:
            allquery = allquery.filter(User.name.ilike(f"%{keyword}%"))

        paginate = allquery.order_by(Blog.id).paginate(page=page, per_page=app.config["PER_PAGE"], error_out=False)
        return render_template('admin_blogs.html', blogs = paginate.items, paginate=paginate)
    except Exception as e:
        print(e)
        flash('No blog to show, please wait...')
        return render_template('admin_blogs.html', blogs=[])

#add blog
@app.route('/admin_addblog', methods=['GET','POST'])
@require_login
@require_admin
def admin_addblog():
    if request.method == 'POST':
        try:
            image_path = '/static/uploads/default.png'
            f = request.files['image']
            if f:
                fname = f.filename
                f.save(os.path.join(current_app.config['UPLOAD_PATH'], fname))
                image_path = '/static/assets/blog/{}'.format(fname)
            blog = Blog(
                title = request.form.get('title'),
                imagepath = image_path,
                category = request.form.get('category'),
                desc = request.form.get('desc'),
                detail = request.form.get('detail')
            )
            db.session.add(blog)
            db.session.commit()
            flash('Submit new post succcessfully','success')
            return redirect(url_for("admin_blogs"))
        except Exception as e:
            print(e)
            flash('Sorry, there is a problem','danger')
            return redirect(url_for("admin_addblog"))
    else:
        return render_template("admin_addblog.html")

#edit blog
@app.route('/admin_editblog/<int:id>', methods=['GET','POST'])
@require_login
@require_admin
def admin_editblog(id):
    blog = Blog.query.get_or_404(id)
    if request.method == 'POST':
        try:
            if request.files.get('image'):
                f = request.files['image']
                fname = f.filename
                print('save image')
                f.save(os.path.join(current_app.config['UPLOAD_PATH'], fname))
                image_path = '/static/assets/blog/{}'.format(fname)
                blog.imagepath = image_path

            blog.title = request.form.get('title')
            blog.desc = request.form.get('desc')
            blog.detail = request.form.get('detail')
            blog.category = request.form.get('category')
            db.session.commit()
            flash('The blog is updated successfully','success')
            return redirect(url_for("admin_blogs"))
        except Exception as e:
            print(e)
            flash('Sorry, there is a problem!','danger')
            return redirect(url_for("admin_editblog", id=id))
    else:
        return render_template("admin_editblog.html", blog = blog)

#delete blog
@app.route('/admin_delblog/<int:id>', methods=['GET','POST'])
@require_login
@require_admin
def admin_delblog(id):
    Blog.query.filter(Blog.id == id).delete()
    #delete the comment also
    Comment.query.filter(Comment.blog_id == id).delete()
    db.session.commit()
    flash('The blog is deleted successfully','success')
    return redirect(url_for("admin_blogs"))

# ############################## manage user part ########################################
# users full list
@app.route('/admin_users', defaults={'page':1})
@app.route('/admin_users/<int:page>')
@require_login
@require_admin
def admin_users(page):
    try:
        username = request.args.get('username')
        email = request.args.get('email')

        allquery = Blog.query
        if username:
            allquery = allquery.filter(User.username.ilike(f"%{username}%"))
        if email:
            allquery = allquery.filter(User.email.ilike(f"%{email}%"))
        allquery = User.query
        paginate = allquery.order_by(User.id).paginate(page=page, per_page=app.config["PER_PAGE"], error_out=False)
        return render_template('admin_users.html', users = paginate.items, paginate=paginate)
    except Exception as e:
        print(e)
        flash('No user to show, please wait...')
        return render_template('admin_users.html', users=[])

#edit user
@app.route('/admin_edituser/<int:id>', methods=['GET','POST'])
@require_login
@require_admin
def admin_edituser(id):
    user = User.query.get_or_404(id)
    if request.method == 'POST':
        try:
            # print(request.form.get('admin'))
            admin = True if request.form.get('admin') == 'on' else False
            user.username = request.form.get('username')
            user.password = request.form.get('password')
            user.admin = admin
            db.session.commit()
            flash('Edit user successfully','success')
            return redirect(url_for("admin_users"))
        except Exception as e:
            print(e)
            flash('Sorry, there is a problem!','danger')
            return redirect(url_for("admin_edituser", id=id))
    else:
        return render_template("admin_edituser.html", user = user)

#delete user
@app.route('/admin_deluser/<int:id>', methods=['GET','POST'])
@require_login
@require_admin
def admin_deluser(id):
    User.query.filter(User.id == id).delete()
    db.session.commit()
    flash('Delete user successfully','success')
    return redirect(url_for("admin_users"))

# ############################## manage comment part ########################################

@app.route('/admin_comments', defaults={'page':1})
@app.route('/admin_comments/<int:page>')
@require_login
@require_admin
def admin_comments(page):
    try:
        keyword = request.args.get('keyword')
        username = request.args.get('username')

        allquery = Comment.query
        if keyword:
            allquery = allquery.filter(Comment.comment.ilike(f"%{keyword}%"))
        if username:
            allquery = allquery.filter(Comment.username.ilike(f"%{username}%"))

        paginate = allquery.order_by(Comment.id).paginate(page=page, per_page=app.config["PER_PAGE"], error_out=False)
        return render_template('admin_comments.html', comments = paginate.items, paginate=paginate)
    except Exception as e:
        print(e)
        flash('No comment to show, please wait...')
        return render_template('admin_comments.html', comments=[])



#delete comment
@app.route('/admin_delcomment/<int:id>', methods=['GET','POST'])
@require_login
@require_admin
def admin_delcomment(id):
    Comment.query.filter(Comment.id == id).delete()
    db.session.commit()
    flash('Delete comment successfully','success')
    return redirect(url_for("admin_comments"))

@app.route('/admin_contacts', defaults={'page':1})
@app.route('/admin_contacts/<int:page>')
@require_login
@require_admin
def admin_contacts(page):
    try:
        keyword = request.args.get('keyword')
        username = request.args.get('username')

        allquery = Contact.query
        if keyword:
            allquery = allquery.filter(Contact.message.ilike(f"%{keyword}%"))
        if username:
            allquery = allquery.filter(Contact.username.ilike(f"%{username}%"))

        paginate = allquery.order_by(Contact.id).paginate(page=page, per_page=app.config["PER_PAGE"], error_out=False)
        return render_template('admin_contacts.html', contacts = paginate.items, paginate=paginate)
    except Exception as e:
        print(e)
        flash('No contact to show, please wait...')
        return render_template('admin_contacts.html', contacts=[])


#delete contact
@app.route('/admin_delcontact/<int:id>', methods=['GET','POST'])
@require_login
@require_admin
def admin_delcontact(id):
    Contact.query.filter(Contact.id == id).delete()
    db.session.commit()
    flash('Delete contact successfully','success')
    return redirect(url_for("admin_contacts"))

############################# Weather ################################
@app.route('/weather')
def weather():
    api_key = "2e08607733b93dc21cb624c61b75aad8"
    try:
        weather_data = get_cardiff_weather(api_key)
        return jsonify({'msg':'success', 'data':weather_data})
    except Exception as e:
        print(e)
        return jsonify({'msg':'failed', 'data':[]})

if __name__ == '__main__':
    app.run(port=5000,debug=True,host="0.0.0.0")