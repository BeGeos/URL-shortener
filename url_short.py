from flask import Flask, request, render_template, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
import requests
from requests import exceptions
import string
import random

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG'] = True

db = SQLAlchemy(app)


# Model Setup
class URLs(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original_url = db.Column(db.String(200))
    short_url = db.Column(db.String(24))

    def __repr__(self):
        return self.original_url


# Start routing
@app.route('/', methods=['GET', 'POST'])
def main():
    base_url = 'http://localhost:5000/'
    if request.method == 'GET':
        return render_template('main.html', name='main')
    if request.method == 'POST':
        url = request.form['url']
        if is_valid(url):
            check = URLs.query.filter_by(original_url=url).first()
            if check:
                new = check
            else:
                short = url_generate()
                new = URLs(original_url=url, short_url=short)
                db.session.add(new)
                db.session.commit()
            return render_template('main.html', URL=new, base_url=base_url)
        return render_template('main.html', name='main', message='URL not found')


@app.route('/<short>')
def redirect_to_original(short):
    url = URLs.query.filter_by(short_url=short).first_or_404()
    return redirect(url.original_url)


# API
@app.route('/api', methods=['POST'])
def shorten_api():
    """API accepts post requests with a URL. It returns the created object information"""

    base_url = 'http://localhost:5000/'
    url = request.get_json()['url']
    if is_valid(url):
        check = URLs.query.filter_by(original_url=url).first()
        if check:
            new = check
        else:
            short = url_generate()
            new = URLs(original_url=url, short_url=short)
            db.session.add(new)
            db.session.commit()
    return jsonify({'id': new.id, 'original url': new.original_url,
                    'short url': base_url + new.short_url, 'code': new.short_url})


# Static method
def is_valid(url):
    """Check if the URL is valid sending a request. If it isn't it returns False
    otherwise it returns True"""

    try:
        get_request = requests.get(url)
        if get_request.status_code == 404:
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
def url_generate(num=8):
    """Using letters and numbers, it generates a random set to attach to the root https://
    It returns a string with the new shorter version of the URL. It is set to 8 by default."""

    new_url = ''
    alphabet = string.ascii_letters + string.digits
    for _ in range(num):
        new_url += random.choice(alphabet)
    return new_url


if __name__ == '__main__':
    app.run()
