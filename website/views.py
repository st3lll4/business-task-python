from datetime import datetime, date
from re import search

from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, DecimalField
from wtforms.validators import DataRequired, Length, NumberRange
from .models import db, Business, Person, Shareholder, Share

views = Blueprint('views', __name__)


class BusinessForm(FlaskForm):
    business_name = StringField('Business Name',
                                validators=[DataRequired(), Length(min=3, max=100)])
    registry_code = StringField('Registry Code',
                                validators=[DataRequired(), Length(min=7, max=7)])
    founding_date = DateField('Founding Date',
                              validators=[DataRequired()], default=datetime.today)
    total_capital = DecimalField('Total Capital',
                                 validators=[DataRequired(), NumberRange(min=2500)])


def get_starting_data():
    business1 = Business(
        name="Bulbasauri aiand OU",
        registry_code="1234567",
        founding_date=date.today(),
        total_capital=5000
    )

    person1 = Person(
        name="Sigmar",
        surname="Kirjak",
        personal_code="12345678987"
    )
    person2 = Person(
        name="Dino",
        surname="Saur",
        personal_code="11112222333"
    )

    share1 = Share(
        shareholder_id=1,
        business_id=1,
        share=1500
    )

    share2 = Share(
        shareholder_id=2,
        business_id=1,
        share=3500
    )

    shareholder1 = Shareholder(
        is_founder=True,
        person_id=1
    )

    shareholder2 = Shareholder(
        is_founder=True,
        person_id=2
    )

    db.session.add(business1)
    db.session.add(person1)
    db.session.add(person2)
    db.session.add(share1)
    db.session.add(share2)
    db.session.add(shareholder1)
    db.session.add(shareholder2)

    db.session.commit()

@views.route('/create-business', methods=['GET', 'POST'])
def create_business():
    if Person.query.count() == 0 and Business.query.count() == 0:
        get_starting_data()

    form = BusinessForm()

    persons = Person.query.all()
    businesses = Business.query.all()

    shareholders_list = [(None, "Select a shareholder")] + [(f"P_{p.id}", f"{p.name} {p.surname}") for p in persons] + \
                        [(f"B_{b.id}", b.name) for b in businesses]

    if request.method == 'POST':
        if form.validate_on_submit():
            shareholders_data = []
            total_shares = 0

            for key in request.form:
                if key.startswith('shareholder_id_'):
                    index = key.split('_')[-1]
                    share_amount = request.form.get(f'share_amount_{index}')
                    shareholder_id = request.form.get(key)

                    if shareholder_id and share_amount:
                        if int(share_amount) < 1:
                            flash('Enter a share for each shareholder', 'error')
                            return redirect(url_for('views.create_business'))
                        if not search(r'^[0-9]+$', share_amount):
                            flash('Shares have to be a number', 'error')
                            return redirect(url_for('views.create_business'))
                        shareholders_data.append({
                            'id': shareholder_id,
                            'share': int(share_amount)
                        })
                        total_shares += int(share_amount)

            if not shareholders_data:
                flash('At least one shareholder is required', 'error')
                return redirect(url_for('views.create_business'))

            if total_shares != form.total_capital.data:
                flash('Total shares have to be equal to total capital', 'error')
                return redirect(url_for('views.create_business'))

            if form.founding_date.data > date.today():
                flash('Founding date cant be in the future', 'error')
                return redirect(url_for('views.create_business'))

            if form.total_capital.data < 2500:
                flash('Total capital has to be at least 2500', 'error')
                return redirect(url_for('views.create_business'))

            shareholder_ids = [data['id'] for data in shareholders_data]
            if len(shareholder_ids) != len(set(shareholder_ids)):
                flash('Enter each shareholder once', 'error')
                return redirect(url_for('views.create_business'))

            try:
                business = Business(
                    name=form.business_name.data,
                    registry_code=form.registry_code.data,
                    founding_date=form.founding_date.data,
                    total_capital=int(form.total_capital.data)
                )
                db.session.add(business)
                db.session.flush()

                for data in shareholders_data:
                    type_id, s_id = data['id'].split('_')

                    sh = Shareholder(
                        is_founder=True,
                        person_id=int(s_id) if type_id == 'P' else None,
                        business_id=int(s_id) if type_id == 'B' else None
                    )
                    db.session.add(sh)
                    db.session.flush()

                    share = Share(
                        shareholder_id=sh.id,
                        business_id=business.id,
                        share=data['share']
                    )
                    db.session.add(share)
                    db.session.commit()

                return redirect(url_for('views.details', id=business.id))

            except Exception as e:
                db.session.rollback()
                flash(f'Error creating business: {str(e)}', 'error')
                return render_template('create_business.html',
                                       form=form,
                                       shareholders_list=shareholders_list)

    return render_template('create_business.html',
                           form=form, shareholders_list=shareholders_list)


@views.route('/')
def home():
    if Person.query.count() == 0 and Business.query.count() == 0:
        get_starting_data()

    search_query = request.args.get('search', '')

    if search_query:
        businesses = db.session.query(Business).filter(Business.name.contains(search_query)).all()
        businesses += db.session.query(Business).filter(Business.registry_code.contains(search_query)).all()
        #todo: query by other things too
    else:
        businesses = Business.query.all()

    return render_template('home.html', businesses=businesses)


@views.route('/details/<int:id>')
def details(id):
    business = Business.query.get_or_404(id)

    shareholders_data = (
        db.session.query(
            Share,
            Shareholder,
            Person,
            Business.name.label('business_name')
        )
        .join(Shareholder, Share.shareholder_id == Shareholder.id)
        .outerjoin(Person, Shareholder.person_id == Person.id)
        .outerjoin(
            Business,
            Shareholder.business_id == Business.id
        )
        .filter(Share.business_id == id)
        .all()
    )

    shareholders = []
    for share, shareholder, person, business_name in shareholders_data:
        shareholder_info = {
            'share': share.share,
            'is_founder': shareholder.is_founder,
            'name': f"{person.name} {person.surname}" if person else business_name,
            'code': person.personal_code if person else business.registry_code,
            'type': 'P' if person else 'B'
        }
        shareholders.append(shareholder_info)

    return render_template('details.html', business=business, shareholders=shareholders)
