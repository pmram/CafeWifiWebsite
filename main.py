import os
import requests
from flask import Flask, jsonify, request, render_template, redirect
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from forms import NewCafeForm, DeleteCafe

app = Flask(__name__)
Bootstrap(app)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

'''
APPLICATION DEFINITION
'''


'''
API DEFINITION
'''
API_KEY = "TopSecretAPIKEY"
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'cafes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route('/', methods=['GET'])
@app.route('/cafes', methods=['GET'])
def get_all_cafes():
    cafes = db.session.query(Cafe).all()
    cafes_json = [(cafe.to_dict()) for cafe in cafes]
    return render_template('index.html', cafes=cafes_json)


@app.route('/cafe/<int:cafe_id>', methods=['GET'])
def get_cafe_by_id(cafe_id):
    cafe = db.session.query(Cafe).where(Cafe.id == cafe_id).first()
    return jsonify(cafes=cafe.to_dict())


@app.route('/cafe', methods=['GET'])
def get_cafe_by_location():
    query_location = request.args.get('loc')
    cafe = db.session.query(Cafe).where(Cafe.location == query_location).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location."})


@app.route('/cafe/add', methods=['GET', 'POST'])
def add_cafe():
    add_form = NewCafeForm()
    if add_form.validate_on_submit():
        new_cafe = Cafe(
            name=request.form.get('name'),
            map_url=request.form.get('map_url'),
            img_url=request.form.get('img_url'),
            location=request.form.get('location'),
            seats=request.form.get('seats'),
            has_toilet=bool(request.form.get('has_toilet')),
            has_wifi=bool(request.form.get('has_wifi')),
            has_sockets=bool(request.form.get('has_sockets')),
            can_take_calls=bool(request.form.get('can_take_calls')),
            coffee_price=request.form.get('coffee_price'),
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect('/')
    return render_template('/add.html', form=add_form)


@app.route('/update-price/<int:cafe_id>', methods=['PATCH'])
def update_price(cafe_id):
    new_price = request.args.get('new_price')
    cafe = db.session.query(Cafe).where(Cafe.id == cafe_id).first()
    if cafe:
        cafe.coffee_price = new_price
        db.session.commit()
        return jsonify({"success": "Successfully updated the price."}), 200
    else:
        return jsonify(error={"Not Found": "Sorry, a cafe with that id does not exist in the database"}), 404


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    delete_form = DeleteCafe(db.session.query(Cafe).all())
    if delete_form.validate_on_submit():
        cafe_id = int(request.form.get('name'))
        params = {
            'api-key': API_KEY
        }
        response = requests.delete(f'http://localhost:5000/report-closed/{cafe_id}', params=params)
        response.raise_for_status()
        return redirect('/')
    return render_template('delete.html', form=delete_form)


@app.route('/report-closed/<int:cafe_id>', methods=['DELETE'])
def delete_cafe(cafe_id):
    cafe = db.session.query(Cafe).get(cafe_id)
    if cafe:
        if request.args.get('api-key') == API_KEY:
            db.session.delete(cafe)
            db.session.commit()
            return jsonify({"success": "Successfully removed the cafe."}), 200
        else:
            return jsonify(error={"Not Allowed": "Sorry, the key provided is not correct"}), 403
    else:
        return jsonify(error={"Not Found": "Sorry, a cafe with that id does not exist in the database"}), 404


if __name__ == "__main__":
    app.run(debug=True)
