from flask import Blueprint, render_template, request, flash, redirect, url_for,jsonify
from .models import Book,User,Transaction
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
views=Blueprint('views',__name__)

# @login_required
# def home():
#     return render_template("home.html")
@views.route('/')
@views.route('/search/',methods=['GET','POST'])
@login_required
def search():
    users = User.query
    book = request.args.get('bookname')
    if book:
        # get books like bookname that are not owned by current user
        books = Book.query.filter(Book.bookname.like(f'%{book}%'), Book.user_id != current_user.id)

        return render_template("search.html",books=books,users=users)
        
    return render_template("search.html")




@views.route('/add',methods=['GET','POST'])
@login_required
def add():
    if request.method=="POST":       
        bookname=request.form.get('bookname')
        authorname=request.form.get('authorname')
        genre=request.form.get('genre')
        review=request.form.get('review')
        new_book=Book(bookname=bookname,authorname=authorname,genre=genre,review=review,user_id=current_user.id)
        db.session.add(new_book)
        db.session.commit()

        return redirect(url_for('views.search'))
    return render_template("add.html", user=current_user)
@views.route('/profile',methods=['GET'])
@login_required
def profile():
    return render_template("profile.html",user=current_user)

    

@views.route('/about',methods=['GET'])
def about():
    return render_template("about.html")

@views.route('/changePassword',methods=['PUT'])
def getValue():
    data=request.get_json()
    old=data["oldpwd"]
    new=data["newpwd"]
    res={
        "message":"successfully changed the password",
    
    }
    return jsonify(res)

@views.route('/requestBook/<p1>/<p2>',methods=['GET','POST'])
@login_required
def requestBook(p1, p2):
    if request.method == 'POST':
        from_id = current_user.id
        book_id = p1
        to_id = p2
        message = request.form.get('request_message')
        new_transaction = Transaction(from_id=from_id, to_id=to_id, book_id=book_id, status='Pending', message=message)
        db.session.add(new_transaction)
        db.session.commit()
        print(message)

        return redirect(url_for('views.search'))
    return render_template("request.html")


@views.route('/requests',methods=['GET'])
@login_required
def requests():
    transactions = Transaction.query.filter_by(to_id=current_user.id)
    # return book info and requested person info via jinja
    book_names=[]
    user_names=[]
    messages=[]
    status=[]
    transaction_ids=[]
    emails=[]
    phonenumbers=[]
    for transaction in transactions:
        book_names.append(Book.query.filter_by(id=transaction.book_id).first().bookname)
        user_names.append(User.query.filter_by(id=transaction.from_id).first().username)
        messages.append(transaction.message)
        status.append(transaction.status)
        transaction_ids.append(transaction.id)
        if(transaction.status!="Approved"):
            emails.append("Hidden!!")
            phonenumbers.append("Hidden!!")
        else:
            emails.append(User.query.filter_by(id=transaction.from_id).first().email)
            phonenumbers.append(User.query.filter_by(id=transaction.from_id).first().phonenumber)

    return render_template("requests.html", transactions=transactions, book_names=book_names, user_names=user_names, messages=messages, status=status, transaction_ids=transaction_ids,emails=emails,phonenumbers=phonenumbers)

@views.route('/approve_request/<p1>',methods=['GET','POST'])
@login_required
def approve_request(p1):
    if request.method == 'POST':
        transaction = Transaction.query.filter_by(id=p1).first()
        transaction.status = 'Approved'
        db.session.commit()

        return redirect(url_for('views.requests'))
    return render_template("requests.html")

@views.route('/reject_request/<p1>',methods=['GET','POST'])
@login_required
def reject_request(p1):
    if request.method == 'POST':
        transaction = Transaction.query.filter_by(id=p1).first()
        transaction.status = 'Rejected'
        db.session.commit()

        return redirect(url_for('views.requests'))
    return render_template("requests.html")

@views.route('/myrequests',methods=['GET'])
@login_required
def myrequests():
    transactions = Transaction.query.filter_by(from_id=current_user.id)
    # return book info and requested person info via jinja
    book_names=[]
    user_names=[]
    messages=[]
    status=[]
    transaction_ids=[]
    emails = []
    phonenumbers =[]
    for transaction in transactions:
        book_names.append(Book.query.filter_by(id=transaction.book_id).first().bookname)
        user_names.append(User.query.filter_by(id=transaction.to_id).first().username)
        messages.append(transaction.message)
        status.append(transaction.status)
        transaction_ids.append(transaction.id)
        if(transaction.status!="Approved"):
            emails.append("Hidden!!")
            phonenumbers.append("Hidden!!")
        else:
            emails.append(User.query.filter_by(id=transaction.from_id).first().email)
            phonenumbers.append(User.query.filter_by(id=transaction.from_id).first().phonenumber)

    return render_template("myrequests.html", transactions=transactions, book_names=book_names, user_names=user_names, messages=messages, status=status, transaction_ids=transaction_ids,emails=emails,phonenumbers=phonenumbers)