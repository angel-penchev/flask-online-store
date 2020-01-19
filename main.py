from functools import wraps
import flask
import json

from users import User

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


@app.route('/users/<int:id>', methods=['GET'])
def users_id(id):
    user = User.find_by('id', id)
    return flask.jsonify({
        'id': user.id,
        'email': user.email,
        'name': user.name,
        'address': user.address,
        'telephone': user.telephone
    })


if __name__ == '__main__':
    app.run()
