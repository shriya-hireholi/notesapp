from notes import (
    app, db, bcrypt, mail)
from notes.forms import (
    NotebookForm,
    NoteForm,
    RegisterForm,
    LoginForm,
    ResetRequestForm,
    ResetPasswordForm,
    UpdateAccountForm)
from notes.models import Notebook, Note, Users
from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
import datetime


def send_reset_email(subject, user, body, url):
    token = user.get_reset_token()
    msg = Message(subject,
                  sender='hireholis@gmail.com',
                  recipients=[user.email])
    msg.body = f'''{body}
    {url_for(url, token=token, _external=True)}'''
    mail.send(msg)


@app.route('/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('notebooks'))

    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)\
            .decode('utf-8')
        user = Users(
            username=form.username.data,
            email=form.email.data,
            password=hashed_password)
        db.session.add(user)
        db.session.commit()

        subject = 'Email Confirmation'
        body = '''Welcome! Thanks for signing up.
        Please follow this link to activate your account:'''
        url = 'confirm_email'
        send_reset_email(subject, user, body, url)
        login_user(user)
        flash('A confirmation email has been sent via email.', 'success')
        return redirect(url_for('unconfirmed'))

    return render_template('register.html', form=form)


@app.route('/confirm/<token>')
@login_required
def confirm_email(token):
    user = Users.verify_reset_token(token)
    if user is None:
        flash('The confirmation link is invalid or has expired.', 'danger')

    confirm_user = Users.query.filter_by(email=user.email).first_or_404()
    if confirm_user.confirmed:
        flash('Account already confirmed. Please login.', 'success')
    else:
        confirm_user.confirmed = True
        confirm_user.confirmed_on = datetime.datetime.now()
        db.session.add(confirm_user)
        db.session.commit()
        flash('You have confirmed your account. Thanks!', 'success')

    return redirect(url_for('unconfirmed'))


@app.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect(url_for('login'))
    flash('Please confirm your account!', 'warning')
    return render_template('unconfirmed.html')


@app.route('/resend')
@login_required
def resend_confirmation():
    subject = 'Email Confirmation'
    body = "Welcome! Thanks for signing up. Please follow this link to activate your account:"
    url = 'confirm_email'
    send_reset_email(subject, current_user, body, url)
    # token = generate_confirmation_token(current_user.email)
    # confirm_url = url_for('confirm_email', token=token, _external=True)
    # html = render_template('activate.html', confirm_url=confirm_url)
    # subject = "Please confirm your email"
    # send_email(current_user.email, subject, html)
    flash('A new confirmation email has been sent.', 'success')
    return redirect(url_for('unconfirmed'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('notebooks'))

    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(
                                    user.password,
                                    form.password.data):
            login_user(user,  remember=form.remember.data)
            next_page = request.args.get('next')
            flash('You have been Logged In', 'success')
            return redirect(next_page or url_for('notebooks'))
        else:
            flash(
                'Login Unsuccessful, Please check email and password',
                'danger')
    return render_template('login.html', form=form)


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/home', methods=['GET', 'POST'])
@login_required
def notebooks():
    form = NotebookForm()
    user_id = current_user.get_id()
    if form.validate_on_submit():
        notebook_name = Notebook(name=form.name.data, user=user_id)
        db.session.add(notebook_name)
        db.session.commit()
        return redirect(url_for('notebooks'))

    notebooks = Notebook.query.filter_by(user=user_id)
    return render_template('notebook.html', form=form, notebooks=notebooks)


@app.route('/notes/<int:id>', methods=['GET', 'POST'])
@login_required
def notes(id):
    notebook = Notebook.query.get_or_404(id)
    form = NoteForm()
    if form.validate_on_submit():
        note = Note(
            title=form.title.data,
            content=form.content.data,
            notebook=id)
        db.session.add(note)
        db.session.commit()
        return redirect(url_for('notes', id=id))

    notes = Note.query.filter_by(notebook=id)
    return render_template(
        'note.html',
        form=form,
        notes=notes,
        notebook=notebook)


@app.route('/delete/<int:pk>/<int:id>')
@login_required
def note_delete(pk, id):
    note_to_delete = Note.query.get_or_404(pk)

    try:
        db.session.delete(note_to_delete)
        db.session.commit()
        return redirect(url_for('notes', id=id))
    except Exception:
        return 'There was a problem deleting that Note'


@app.route('/update/<int:pk>/<int:id>', methods=['GET', 'POST'])
@login_required
def note_update(pk, id):
    note_to_update = Note.query.get_or_404(pk)

    if request.method == 'POST':
        note_to_update.title = request.form['title']
        note_to_update.content = request.form['content']
        try:
            db.session.commit()
            return redirect(url_for('notes', id=id))
        except Exception:
            return 'There was a problem editing that Note'

    return render_template('update.html', note=note_to_update)


@app.route('/delete/<int:id>')
@login_required
def notebook_delete(id):
    notebook_to_delete = Notebook.query.get_or_404(id)

    try:
        db.session.delete(notebook_to_delete)
        db.session.commit()
        return redirect(url_for('notebooks'))
    except Exception:
        return 'There was a problem deleting that Note'


@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def notebook_update(id):
    notebook_to_update = Notebook.query.get_or_404(id)

    if request.method == 'POST':
        notebook_to_update.name = request.form['name']
        try:
            db.session.commit()
            return redirect(url_for('notes', id=id))
        except Exception:
            return 'There was a problem editing that Note'

    return render_template('notebook_update.html', notebook=notebook_to_update)


@app.route('/reset', methods=['GET', 'POST'])
def reset_request():
    form = ResetRequestForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        subject = 'Password Reset Request'
        body = "To reset your password, visit the following link:"
        url = 'reset_token'
        send_reset_email(subject, user, body, url)
        flash('An email has been sent to reset your password.', 'info')
        return redirect(url_for('login'))
    return render_template('request_reset.html', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_token(token):
    user = Users.verify_reset_token(token)
    if user is None:
        flash('That is an invalid  or expired token', 'warning')
        return redirect(url_for('reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)\
            .decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash(
            'Your password has been updated! You are now able to log in',
            'success')
        return redirect(url_for('login'))
    return render_template('request_password.html', form=form)


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.confirmed = False
        db.session.commit()
        subject = 'Email Confirmation'
        body = '''Welcome! Thanks for signing up.
        Please follow this link to activate your account:'''
        url = 'confirm_email'
        send_reset_email(subject, current_user, body, url)
        flash('A confirmation email has been sent via email.', 'success')
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.email.data = current_user.email
    return render_template('profile.html', form=form)
