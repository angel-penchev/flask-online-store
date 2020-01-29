from functools import wraps
import flask
import json
import sqlite3

from users import User
from ads import Ads

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
        return flask.jsonify([{
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'address': user.address,
            'telephone': user.telephone
        } for user in User.all()])

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
        return flask.jsonify({
            'id': user.id,
            'email': user.email,
            'name': user.name,
            'address': user.address,
            'telephone': user.telephone
        })

    if flask.request.method == 'PATCH':
        for value in flask.request.json:
            if value in ['email', 'password']:
                continue

            User.update(user.id, value, flask.request.json[value])
        return 'Success'

    if flask.request.method == 'DELETE':
        for ad in Ads.all():
            if ad.owner_id == user.id:
                Ads.delete(ad.id)

        User.delete(user.id)
        return 'Success'


@app.route('/ads', methods=['GET'])
def get_ads():
    if flask.request.method == 'GET':
        return flask.jsonify([{
            'id': ads.id,
            'title': ads.title,
            'description': ads.description,
            'price': ads.price,
            'date_created': ads.date_created,
            'is_active': ads.is_active,
            'owner_id': ads.owner_id,
            'buyer_id': ads.buyer_id,
        } for ads in Ads.all()])


@app.route('/ads', methods=['POST'])
@require_login
def post_ads(user):
    if flask.request.method == 'POST':
        data = flask.request.json
        Ads(*(
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
    ad = Ads.find_by('id', id)
    if flask.request.method == 'GET':
        return flask.jsonify({
            'id': ad.id,
            'title': ad.title,
            'description': ad.description,
            'price': ad.price,
            'date_created': ad.date_created,
            'is_active': ad.is_active,
            'owner_id': ad.owner_id,
            'buyer_id': ad.buyer_id,
        })


@app.route('/ads/<int:id>', methods=['PATCH', 'DELETE'])
@require_login
def ads_id(user, id):
    ad = Ads.find_by('id', id)
    if ad.owner_id != user.id:
        return 'Unauthorized', 401

    if flask.request.method == 'PATCH':
        for value in flask.request.json:
            Ads.update(ad.id, value, flask.request.json[value])
        return 'Success'

    if flask.request.method == 'DELETE':
        Ads.delete(ad.id)
        return 'Success'


@app.route('/ads/<int:id>/buy', methods=['POST'])
@require_login
def ads_id_buy(user, id):
    ad = Ads.find_by('id', id)

    if ad.owner_id == user.id:
        return 'You cannot buy your own ad'

    Ads.update(ad.id, 'is_active', 0)
    Ads.update(ad.id, 'buyer_id', user.id)

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


if __name__ == '__main__':
    app.run()
