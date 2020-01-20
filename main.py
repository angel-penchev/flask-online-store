from functools import wraps
import flask
import json

from users import User
from ads import Ads

app = flask.Flask(__name__)


def require_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = flask.request.cookies.get('token')
        if not token or not User.verify_token(token):
            return flask.redirect('/login')
        return func(*args, **kwargs)
    return wrapper


@app.route('/users', methods=['GET', 'POST'])
def users():

    if flask.request.method == 'GET':
        return flask.jsonify([{
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'address': user.address,
            'telephone': user.telephone
        } for user in User.all()])

    if flask.request.method == 'POST':
        values = (None,
                  flask.request.form['email'],
                  User.hash_password(flask.request.form['password']),
                  flask.request.form['name'],
                  flask.request.form['address'],
                  flask.request.form['telephone'])
        User(*values).create()

        user = User.find_by('email', flask.request.form['email'])
        token = user.generate_token()
        return flask.jsonify({'token': token.decode('utf8')})


@app.route('/login', methods=['POST'])
def login():
    if flask.request.method == 'POST':
        data = flask.request.form
        user = User.find_by('email', data['email'])

        if not user or not user.verify_password(data['password']):
            return flask.jsonify({'token': None})

        token = user.generate_token()
        return flask.jsonify({'token': token.decode('utf8')})


@app.route('/users/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def users_id(id):
    user = User.find_by('id', id)
    if not user:
        return flask.jsonify("User not found!")

    if flask.request.method == 'POST':
        return flask.jsonify({
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'address': user.address,
            'telephone': user.telephone
        })
    
    if flask.request.method == 'PATCH':
        for value in flask.request.form:
            if value in ['email', 'password']:
                continue

            User.update(user.id, value, flask.request.form[value])
        return "Success!"
    
    if flask.request.method == 'DELETE':
        User.delete(user.id)
        return "Success!"

@app.route('/ads', methods=['POST'])
def ads():
    if flask.request.method == 'POST':
        data = flask.request.form
        Ads(*(
            None,
            data['title'],
            data['description'],
            data['price'],
            data['date_created'],
            1,
            None
        )).create()

        return 'Success'
        

if __name__ == '__main__':
    app.run()
