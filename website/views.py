from flask import Blueprint, render_template, request, jsonify, flash, abort, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, DecimalField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError
from datetime import datetime, date
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

    def validate_founding_date(self, field):
        if field.data > date.today():
            raise ValidationError('Founding date cant be in the future')


def get_starting_data():
    business1 = Business(
        name="Bulbasauri aiand OU",
        registry_code="1234567",
        founding_date=date.today(),
        total_capital=5000
    )
    business2 = Business(
        name="OU Sauruse Pagarikoda",
        registry_code="9876543",
        founding_date=date.today(),
        total_capital=3000
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
    db.session.add(business1)
    db.session.add(business2)
    db.session.add(person1)
    db.session.add(person2)

    db.session.commit()


@views.route('/create-business', methods=['GET', 'POST'])
def create_business():

    if Person.query.count() == 0 and Business.query.count() == 0:
        get_starting_data()

    form = BusinessForm()

    persons = Person.query.all()
    businesses = Business.query.all()


    shareholders_list = [(None, "Select a shareholder")] + \
                        [(f"P_{p.id}", f"{p.name} {p.surname}") for p in persons] + \
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
                        shareholders_data.append({
                            'id': shareholder_id,
                            'share': float(share_amount)
                        })
                        total_shares += float(share_amount)

            #if total_shares != form.total_capital.data:
            #    flash('Total shares must equal total capital')
            #    return render_template('create_business.html',
            #                           form=form, shareholders_list=shareholders_list)


            try:
                business = Business(
                    name=form.business_name.data,
                    registry_code=form.registry_code.data,
                    founding_date=form.founding_date.data,
                    total_capital=form.total_capital.data
                )
                db.session.add(business)
                db.session.flush()

                for data in shareholders_data: # siin tahab sama id/ga lisada need
                    type_id, s_id = data['id'].split('_')
                    if data:
                        print(data)
                    else:
                        print("i got nothing")

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

                flash('Business created successfully!', 'success')
                return redirect(url_for('views.create_business'))  # todo: Redirect to details


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
    search_query = request.args.get('search', '')

    if search_query:
        businesses = Business.query.filter(Business.name.ilike(f'%{search_query}%')).all()
        # todo: shareholderite kaudu ka otsima panna
    else:
        businesses = Business.query.all()

    return render_template('home.html', businesses=businesses)


@views.route('/details/')
def details():
    business_id = request.args.get('id')
    if not business_id:
        abort(404)  # Return 404 if no ID provided

    business = Business.query.get_or_404(business_id)
    return render_template('details.html', business=business)