from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, DecimalField, SelectField
from wtforms.validators import DataRequired, Length, NumberRange
from datetime import datetime
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


@views.route('/create-business', methods=['GET', 'POST'])
def create_business():
    form = BusinessForm()

    # Get all possible shareholders for the dropdown
    persons = Person.query.all()
    businesses = Business.query.all()

    shareholders_list = [(None, "Select a shareholder")] + \
                        [(f"P_{p.id}", f"{p.name} {p.surname}") for p in persons] + \
                        [(f"B_{b.id}", b.name) for b in businesses]

    if request.method == 'POST':
        if form.validate_on_submit():
            # Get the form data
            shareholders_data = []
            total_shares = 0

            # Process shareholders data from form
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

            # Validate total shares match total capital
            if total_shares != form.total_capital.data:
                flash('Total shares must equal total capital')
                return render_template('create_business.html',
                                       form=form, shareholders_list=shareholders_list)

            try:
                # Create new business
                business = Business(
                    name=form.business_name.data,
                    registry_code=form.registry_code.data,
                    founding_date=form.founding_date.data,
                    total_capital=form.total_capital.data
                )
                db.session.add(business)
                db.session.flush()  # Get business ID without committing

                # Create shareholders
                for data in shareholders_data:
                    type_id, s_id = data['id'].split('_')

                    sh = Shareholder(
                        is_founder=True,
                        business_id=business.id,
                        person_id=int(s_id) if type_id == 'P' else None,
                        sh_business_id=int(s_id) if type_id == 'B' else None
                    )
                    db.session.add(sh)
                    db.session.flush()

                    # Create share record
                    share = Share(
                        shareholder_id=sh.id,
                        business_id=business.id,
                        share=data['share']
                    )
                    db.session.add(share)

                db.session.commit()
                return jsonify({'success': True, 'business_id': business.id})

            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'error': str(e)})

    return render_template('create_business.html',
                           form=form, shareholders_list=shareholders_list)

@views.route('/')
def home():
    search_query = request.args.get('search', '')

    if search_query:
        businesses = Business.query.filter(Business.name.ilike(f'%{search_query}%')).all()
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