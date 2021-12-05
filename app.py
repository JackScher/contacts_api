import re

from flask import Flask, Response, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates
from sqlalchemy import inspect


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1111@localhost/flask_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Contacts(db.Model):
    __tablename__ = 'Contacts'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(60), nullable=False)
    last_name = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(60))
    phone = db.Column(db.String(15))
    company = db.Column(db.String(60))
    address = db.Column(db.Integer, db.ForeignKey('Addresses.id'), nullable=False)

    def __init__(self, first_name, last_name, email, phone, company, address):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.phone = phone
        self.company = company
        self.address = address

    def __repr__(self):
        return f'Contacts {self.id}'

    @validates('email')
    def validate_email(self, key, email):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if email:
            if not re.fullmatch(regex, email):
                raise AssertionError('invalid email')
        return email


class Addresses(db.Model):
    __tablename__ = 'Addresses'

    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(2), nullable=False)
    city = db.Column(db.String(60), nullable=False)
    street = db.Column(db.String(60), nullable=False)
    unit = db.Column(db.String(60))
    zip = db.Column(db.Integer)

    def __init__(self, country, city, street, unit, zip):
        self.country = country
        self.city = city
        self.street = street
        self.unit = unit
        self.zip = zip

    def __repr__(self):
        return f'Addresses {self.id}'

    @validates('zip')
    def validate_zip(self, key, zip):
        if len(str(zip)) > 5:
            raise AssertionError('"zip" digits length is more than 5')
        if len(str(zip)) < 4:
            raise AssertionError('"zip" digits length is less than 4')
        return zip

    @validates('country')
    def validate_country(self, key, country):
        if not country.isupper():
            raise AssertionError('"country" should be in upper case')
        return country


@app.route('/', methods=('POST', 'GET'))
def index():

    if request.method == 'POST':
        if not request.is_json:
            return jsonify("Not JSON request."), 415

        data = request.get_json()
        try:
            a = Addresses(country=data.get('country', None), city=data.get('city', None), street=data.get('street', None),
                          unit=data.get('unit', None), zip=data.get('zip', None))
            db.session.add(a)
            db.session.flush()
            c = Contacts(first_name=data.get('first_name', None), last_name=data.get('last_name', None), email=data.get('email', None),
                         phone=data.get('phone', None), company=data.get('company', None), address=a.id)
            db.session.add(c)
            db.session.commit()
            response = {key: data[key] for key in data}
            return jsonify(response), 201
        except Exception as e:
            db.session.rollback()
            return Response(f"{e}", status=422, mimetype='application/json')

    if request.method == 'GET':
        if not request.args:
            data = Contacts.query.all()
            return Response(f"{data}", status=200, mimetype='application/json')

        data = {key: "'" + str(request.args[key]) + "'" if type(request.args[key]) is str else str(request.args[key]) for key in request.args}
        sql_params = [f'"{Contacts.__tablename__}".{key}=' + data[key] if key in inspect(Contacts).attrs else f'"{Addresses.__tablename__}".{key}=' + data[key] for key in data]
        sql = f'select "{Contacts.__tablename__}".id from "{Contacts.__tablename__}" join "{Addresses.__tablename__}" on "{Contacts.__tablename__}".address = "{Addresses.__tablename__}".id where '
        sql_params = ' and '.join(sql_params)
        sql += sql_params
        try:
            result = db.session.execute(sql)
            ids = [item[0] for item in result]
            result = Contacts.query.filter(Contacts.id.in_(ids)).all()
            return Response(f"{result}", status=200, mimetype='application/json')
        except:
            return Response(f"Wrong parameter input", status=422, mimetype='application/json')


if __name__ == '__main__':
    app.run(debug=True)
