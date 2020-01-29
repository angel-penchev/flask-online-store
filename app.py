from functools import wraps
import flask
import json
import sqlite3

from users import User
from ads import Ad

app = flask.Flask(__name__)


def require_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = flask.request.headers.get('token')
        user = User.verify_token(token)

        if not token or not user:
            return 'No user login'
        return func(user, *args, **kwargs)

    return wrapper


@app.route('/users', methods=['GET', 'POST'])
def users():

    if flask.request.method == 'GET':
        return flask.jsonify([User.to_dict(user) for user in User.all()])

    if flask.request.method == 'POST':
        values = (None,
                  flask.request.json['email'],
                  User.hash_password(flask.request.json['password']),
                  flask.request.json['name'],
                  flask.request.json['address'],
                  flask.request.json['telephone'])
        User(*values).create()

        user = User.find_by('email', flask.request.json['email'])
        token = user.generate_token()
        return flask.jsonify({'token': token.decode('utf8')})


@app.route('/login', methods=['POST'])
def login():
    if flask.request.method == 'POST':
        data = flask.request.json
        user = User.find_by('email', data['email'])

        if not user or not user.verify_password(data['password']):
            return flask.jsonify({'token': None})

        token = user.generate_token()
        return flask.jsonify({'token': token.decode('utf8')})


@app.route('/users/<int:id>', methods=['GET', 'PATCH', 'DELETE'])
def users_id(id):
    user = User.find_by('id', id)
    if not user:
        return flask.jsonify('Nor is the user found, nor is he a coffie machine!'), 418

    if flask.request.method == 'GET':
        return flask.jsonify(User.to_dict(user))

    if flask.request.method == 'PATCH':
        for value in flask.request.json:
            if value in ['email', 'password']:
                continue

            User.update(user.id, value, flask.request.json[value])
        return 'Success'

    if flask.request.method == 'DELETE':
        for ad in Ad.all():
            if ad.owner_id == user.id:
                Ad.delete(ad.id)

        User.delete(user.id)
        return 'Success'


@app.route('/ads', methods=['GET'])
def get_ads():
    if flask.request.method == 'GET':
        return flask.jsonify([Ad.to_dict(ad) for ad in Ad.all()])


@app.route('/ads', methods=['POST'])
@require_login
def post_ads(user):
    if flask.request.method == 'POST':
        data = flask.request.json
        Ad(*(
            None,
            data['title'],
            data['description'],
            data['price'],
            data['date_created'],
            1,
            user.id,
            None
        )).create()

        return 'Success'


@app.route('/ads/<int:id>', methods=['GET'])
def get_ads_id(id):
    ad = Ad.find_by('id', id)
    if flask.request.method == 'GET':
        return Ad.to_dict(ad)


@app.route('/ads/<int:id>', methods=['PATCH', 'DELETE'])
@require_login
def ads_id(user, id):
    ad = Ad.find_by('id', id)
    if ad.owner_id != user.id:
        return 'Unauthorized', 401

    if flask.request.method == 'PATCH':
        for value in flask.request.json:
            Ad.update(ad.id, value, flask.request.json[value])
        return 'Success'

    if flask.request.method == 'DELETE':
        Ad.delete(ad.id)
        return 'Success'


@app.route('/ads/<int:id>/buy', methods=['POST'])
@require_login
def ads_id_buy(user, id):
    ad = Ad.find_by('id', id)

    if ad.owner_id == user.id:
        return 'You cannot buy your own ad'

    Ad.update(ad.id, 'is_active', 0)
    Ad.update(ad.id, 'buyer_id', user.id)

    return 'Success '


@app.route('/bought_ads', methods=['GET'])
@require_login
def bought_ads(user):
    if flask.request.method == 'GET':
        keys = ['id', 'title', 'description', 'price',
                'date_created', 'is_active', 'owner_id', 'buyer_id']
        ads = [{keys[i]: ad[i]
                for i in range(len(keys))} for ad in User.get_bought_ads(user.id)]
        return flask.jsonify(ads)


@app.route('/ads/search', methods=['GET'])
def ads_search():
    result = [Ad.to_dict(ad) for ad in Ad.all()]
    if flask.request.method == 'GET':
        for value in flask.request.json:
            for ad in range(len(result)):
                if flask.request.json[value] not in result[ad][value]:
                    result.pop(ad)

    return flask.jsonify(result)


if __name__ == '__main__':
    app.run()
