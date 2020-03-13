import os
from forms import AddForm, DelForm, AddOwnerForm
from flask import Flask, render_template, url_for, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
app = Flask(__name__)
# Key for Forms
app.config['SECRET_KEY'] = 'mysecretkey'

############################################

# SQL DATABASE AND MODELS

##########################################
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app, db)


class Puppy(db.Model):

    __tablename__ = 'puppies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    # This is a one-to-one relationship
    # A puppy only has one owner, thus uselist is False.
    # Strong assumption of 1 dog per 1 owner and vice versa.
    owner = db.relationship('Owner', backref='puppy', uselist=False)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        if self.owner:
            return f"Puppy name: {self.name}, Owner name: {self.owner.name}"

        else:
            return f"Puppy name: {self.name}, Has not owner assigned"


class Owner(db.Model):

    __tablename__ = 'Owners'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    # We use puppies.id because __tablename__='puppies'
    puppy_id = db.Column(db.Integer, db.ForeignKey('puppies.id'))

    def __init__(self, name, puppy_id):
        self.name = name
        self.puppy_id = puppy_id

    def __repr__(self):
        return f"Owner name: {self.name}"


############################################

        # VIEWS WITH FORMS

##########################################
@app.route('/')
def index():
    return render_template('home.html')


@app.route('/add', methods=['GET', 'POST'])
def add_pup():
    form = AddForm()

    if form.validate_on_submit():
        name = form.name.data

        # Add new Puppy to database
        new_pup = Puppy(name)
        db.session.add(new_pup)
        db.session.commit()

        return redirect(url_for('list_pup'))

    return render_template('add.html', form=form)


@app.route('/add_owner', methods=['GET', 'POST'])
def add_own():
    form = AddOwnerForm()

    if form.validate_on_submit():
        name = form.name.data
        puppy_id = form.puppy_id.data

        # Add new Puppy to database
        new_owner = Owner(name, puppy_id)
        db.session.add(new_owner)
        db.session.commit()
        flash(f'The owner {new_owner.name} was added successfully')
        return redirect(url_for('list_pup'))

    return render_template('add_owner.html', form=form)


@app.route('/list')
def list_pup():
    # Grab a list of puppies from database.
    puppies = Puppy.query.all()
    owners = Owner.query.all()

    entities = {'puppies': puppies, 'owners': owners}
    return render_template('list.html', entities=entities)


@app.route('/delete', methods=['GET', 'POST'])
def del_pup():

    form = DelForm()

    if form.validate_on_submit():
        id = form.id.data
        pup = Puppy.query.get(id)
        db.session.delete(pup)
        db.session.commit()

        return redirect(url_for('list_pup'))
    return render_template('delete.html', form=form)


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
