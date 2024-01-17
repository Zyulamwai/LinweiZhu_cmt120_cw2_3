from comUtils import db
from datetime import datetime

### model part  ###
class User(db.Model):
    """
    User info Table
    """
    __tablename__='user'
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    email = db.Column(db.String(60), unique=True)
    username = db.Column(db.String(20), index=True, unique=True)
    password = db.Column(db.String(20))
    admin = db.Column(db.Boolean, default=False)

    def is_admin(self):
        return "Yes" if self.admin else "No"


class Blog(db.Model):
    """
    Blog Table
    """
    __tablename__ = 'blog'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500))
    desc = db.Column(db.Text())
    detail = db.Column(db.Text())
    category = db.Column(db.String(50))
    imagepath = db.Column(db.String(200))
    post_dt = db.Column(db.DateTime, default=datetime.now)

    def get_comment(self):
        count = Comment.query.filter(Comment.blog_id == self.id).count()
        return count

class Comment(db.Model):
    """
    Comment Table
    """
    __tablename__ = 'comment'
    id = db.Column(db.Integer, primary_key=True)
    blog_id = db.Column(db.Integer)
    comment = db.Column(db.Text())
    username = db.Column(db.String(100))
    post_dt = db.Column(db.DateTime, default=datetime.now)

    def get_blog_subject(self):
        try:
            blog = Blog.query.get_or_404(self.blog_id)
            title = blog.title
        except Exception as e:
            title = 'No title'
        return title

class Contact(db.Model):
    """
    Contact Table
    """
    __tablename__ = 'contact'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(60), unique=True)
    subject = db.Column(db.String(300))
    message = db.Column(db.String(1000))
    post_dt = db.Column(db.DateTime, default=datetime.now)
