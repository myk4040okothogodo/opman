from datetime import datetime
from flask import render_template, session, abort,redirect, url_for,request,flash,current_app
from . import main
from ..import db
from ..models import User,Account, Opportunity,Permission,Role
from .forms import AccountRegistryForm, OpportunityRegistryForm, EditProfileForm,EditprofileAdminForm
from flask_login import login_required, current_user

@main.route('/', methods=['GET','POST'])
def index():
    form = AccountRegistryForm()
    page = request.args.get('page', 1, type=int)
    pagination = Account.query.order_by(Account.timestamp.desc()).paginate(page, error_out=False)
    accounts = pagination.items
    return render_template('index.html',
                            accounts=accounts,pagination=pagination,
                           current_time=datetime.utcnow())

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    accounts = user.accounts.order_by(Account.timestamp.desc()).all()
    return render_template('user.html', user=user, accounts=accounts,current_time=datetime.utcnow())

@main.route('/users/<username>')
def users(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    page = request.args.get('page', 1, type=int)   
    pagination = User.query.order_by(User.username).paginate(page, error_out=False)
    users = pagination.items
    return render_template('users.html', users=users,title="App Users", pagination=pagination,user=user,endpoint=".users",current_time=datetime.utcnow())


@main.route('/account/<int:id>', methods=['GET','POST'])
@login_required
def account(id):
    account = Account.query.get_or_404(id)
    form = OpportunityRegistryForm()
    if form.validate_on_submit():
        opportunity = Opportunity(position_name=form.position_name.data,
                                  no_of_positions= form.no_of_positons.data,
                                  author=current_user._get_current_object(),
                                  account=account)
        db.session.add(opportunity)
        flash("the Opportunity has been posted","positive")
        return redirect(url_for('.post', id=post.id, page=-1))
    page = request.args.get('page', 1 , type=int)
    if page == -1:
        page = (account.opportunities.count() - 1) / \
               current_app.config['APP_COMMENTS_PER_PAGE'] + 1
    pagination = account.opportunities.order_by(Opportunity.timestamp.asc()).paginate(
        page, per_page=current_app.config['APP_COMMENTS_PER_PAGE'], error_out=False)
    opportunities = pagination.items
    return render_template('account.html', accounts=[account],form=form, opportunities=opportunities, pagination=pagination,current_user=current_user)


@main.route('/edit/<int:id>', methods=['GET','POST'])
@login_required
def edit(id):
    account = Account.query.get_or_404(id)
    if current_user != account.creator and not current_user.is_administrator:
        abort(403)
    form = AccountRegistryForm()
    if form.validate_on_submit():
        account.company_name=form.company_name.data
        account.company_address= form.company_address.data
        account.author=current_user._get_current_object()
        db.session.add(account)
        flash("The account has been updated")
        return redirect(url_for('.account', id=account.id))
    form.company_name.data = account.company_name
    form.company_address.data = account.company_address
    return render_template('create_account.html', form=form, current_time=datetime.utcnow())

@main.route('/edit-profile', methods=['GET','POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated.','positive')
        return redirect(url_for('.user', username=current_user.username))
    form.username.data = current_user.username
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', current_user=current_user,form=form,current_time=datetime.utcnow())

@main.route('/edit-profile-admin/<int:id>', methods=['GET','POST'])
@login_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditprofileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.role = Role.query.get(form.role.data)
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.','positive')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.role.data = user.role_id
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form,user=user,current_time=datetime.utcnow())

@main.route('/accounts/<username>')
def accounts(username):
    user = User.query.filter_by(username= username).first()
    if user is None:
        flash('Invalid user','negative')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = Account.query.order_by(Account.timestamp.desc()).paginate(page, error_out=False)
    accounts = pagination.items
    return render_template('accounts.html', user=user, title="All-Accounts ", endpoint=".accounts", pagination=pagination, accounts=accounts)

@main.route('/opportunities/<username>')
def opportunities(username):
    user = User.query.filter_by(username= username).first()
    if user is None:
        flash('Invalid user.','negative')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = Opportunity.query.order_by(Opportunity.timestamp.desc()).paginate(page, error_out=False)
    opportunities = pagination.items
    return render_template('opportunities.html', title="All-Opportunities",endpoint=".opportunities" ,pagination=pagination, opportunities=opportunities,user=user)

@main.route('/Register_Account', methods=['GET','POST'])
@login_required
def Register_Account():
    form = AccountRegistryForm()
    if form.validate_on_submit():
        account = Account(company_name=form.company_name.data,
                          company_address=form.company_address.data,
                          creator = current_user._get_current_object())
        db.session.add(account)
        db.session.commit()
        flash ('You have successufuly created the account', 'positive')
        return redirect(url_for('main.index'))
    return render_template("create_account.html", form=form,current_time=datetime.utcnow())

@main.route('/account/<int:id>/add_opportunity', methods=['GET','POST'])
@login_required
def add_opportunity(id):
    account = Account.query.get_or_404(id)
    form = OpportunityRegistryForm()
    if form.validate_on_submit():
        opportunity = Opportunity(position_name=form.position_name.data,
                                  no_of_positions= form.no_of_positions.data,
                                  author=current_user._get_current_object(),
                                  account=account)
        db.session.add(opportunity)
        flash("the Opportunity has been posted","positive")
        return redirect(url_for('main.account', id=account.id))
    return render_template("add_opportunity.html", form=form,current_time=datetime.utcnow())

@main.route('/moderate')
@login_required
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Opportunity.query.order_by(Opportunity.timestamp.desc()).paginate(page,per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
                                                                           error_out=False)
    opportunities = pagination.items
    return render_template('moderate.html', opportunities=opportunities, pagination=pagination, page=page)


@main.route('/delete_user/<int:id>', methods=['GET','POST'])
def delete_user(id):
    user = User.query.get_or_404(id)
    user2 = User.query.get_or_404((id+1))
    username = user2.username
    if current_user.is_administrator:
        db.session.delete(user)
        db.session.commit()
        flash("the user has been deleted", 'positive')
        return redirect(url_for('main.users', username=username))
    flash('You are not authorised to perform function.')
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/delete_opportunity/<int:id>', methods=['GET','POST'])
@login_required
def delete_opportunity(id):
    opportunity = Opportunity.query.get_or_404(id)
    opportunity2 = Opportunity.query.get_or_404(id-1)
    account = Account.query.filter_by(id= opportunity.account.id)
    if current_user.is_administrator or current_user == opportunity.author:
        db.session.delete(opportunity)
        db.session.commit()
        flash("The opportunity has been deleted")
        return redirect(url_for('main.account', id=opportunity2.account.id))
    flash('You are not authorized to perform function.')
    #return render_template('account.html')

@main.route('/account/<int:id>/delete_account', methods=['GET','POST'])
@login_required
def delete_account(id):
    account = Account.query.get_or_404(id)
    account2 = Account.query.get_or_404((id+1))
    username = account.creator.username
    if current_user.is_administrator or current_user == account.creator:
        db.session.delete(account)
        db.session.commit()
        flash('Account successfully deleted.')
        return redirect(url_for('.accounts', username=username))
    flash("you are not authorized to perform function.")
    return redirect(url_for('auth.login'))
