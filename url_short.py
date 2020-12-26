from flask import Flask, request, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
from requests import exceptions
import string
import random

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True

db = SQLAlchemy(app)


class URLs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(200))
    short_url = db.Column(db.String(24))

    def __repr__(self):
        return self.original_url


# Start routing
@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return render_template('main.html', name='main')
    if request.method == 'POST':
        url = request.form['url']
        if is_valid(url):
            short = url_generate(url)
            new = URLs(original_url=url, short_url=short)
            db.session.add(new)
            db.session.commit()
            return render_template('main.html', URL=new)
        return render_template('main.html', name='main', message='URL not found')


# Static method
def is_valid(url):
    """Check if the URL is valid sending a request. If it isn't it returns False
    otherwise it returns True"""

    try:
        get_request = requests.get(url)
        if get_request.status_code != 200:
            return False
    except exceptions.ConnectionError:
        return False
    except exceptions.InvalidSchema:
        return False
    except exceptions.InvalidURL:
        return False
    except exceptions.MissingSchema:
        return False
    return True


# Static method
def url_generate(url, num=8):
    """Using letters only, it generates a random set to attach to the root https://
    It returns a string with the new shorter version of the URL. It is set to 8 by default."""

    new_url = 'https://'
    alphabet = string.ascii_letters
    for _ in range(num):
        new_url += random.choice(alphabet)
    return new_url


if __name__ == '__main__':
    app.run()
