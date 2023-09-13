from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Member, Transaction
from django.utils.timezone import now
from decimal import Decimal
import requests

def book_list(request):
    books = Book.objects.all()
    return render(request, 'book_list.html', {'books': books})

def member_list(request):
    members = Member.objects.all()
    return render(request, 'member_list.html', {'members': members})

def add_book(request):
    if request.method == 'POST':
        try:
            title = request.POST.get('title')
            author = request.POST.get('author')
            isbn = request.POST.get('isbn')
            publisher = request.POST.get('publisher')
            page_count = request.POST.get('page_count')
            stock = request.POST.get('stock')

            Book.objects.create(
                title=title,
                author=author,
                isbn=isbn,
                publisher=publisher,
                page_count=page_count,
                stock=stock
            )
            return redirect('book_list')
        except Exception as e:
            return render(request, 'add_book.html', {'error_message': str(e)})

    return render(request, 'add_book.html')

def issue_book(request, book_id, member_id):
    book = get_object_or_404(Book, id=book_id)
    member = get_object_or_404(Member, id=member_id)

    if request.method == 'POST':
        try:
            with transaction.atomic():
                transaction = Transaction.objects.create(
                    book=book,
                    member=member,
                    issue_date=now()
                )
                book.stock -= 1
                book.save()
            return redirect('book_list')
        except Exception as e:
            return render(request, 'issue_book.html', {'book': book, 'member': member, 'error_message': str(e)})

    return render(request, 'issue_book.html', {'book': book, 'member': member})

def return_book(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    if request.method == 'POST':
        try:
            with transaction.atomic():
                transaction.return_date = now()
                days_late = (transaction.return_date - transaction.issue_date).days
                if days_late > 0:
                    late_fee = Decimal(days_late) * 10
                    transaction.fee = late_fee
                    member = transaction.member
                    member.outstanding_debt += late_fee
                    member.save()
                transaction.save()
                transaction.book.stock += 1
                transaction.book.save()
            return redirect('book_list')
        except Exception as e:
            return render(request, 'return_book.html', {'transaction': transaction, 'error_message': str(e)})

    return render(request, 'return_book.html', {'transaction': transaction})

def search_books(request):
    if request.method == 'POST':
        try:
            search_title = request.POST.get('title')
            search_author = request.POST.get('author')
            books = Book.objects.filter(title__icontains=search_title, author__icontains=search_author)
            return render(request, 'search_results.html', {'books': books})
        except Exception as e:
            return render(request, 'search_books.html', {'error_message': str(e)})

    return render(request, 'search_books.html')

def charge_fee(request, member_id):
    member = get_object_or_404(Member, id=member_id)

    if request.method == 'POST':
        try:
            fee = Decimal(request.POST['fee'])
            member.outstanding_debt += fee
            member.save()
            return redirect('book_list')
        except Exception as e:
            return render(request, 'charge_fee.html', {'member': member, 'error_message': str(e)})

    return render(request, 'charge_fee.html', {'member': member})

def import_books(request):
    if request.method == 'POST':
        try:
            num_books = request.POST.get('num_books')
            title = request.POST.get('title')

            api_url = 'https://frappe.io/api/method/frappe-library'
            params = {
                'page': 2,
                'title': title,
            }
            response = requests.get(api_url, params=params)


            if response.status_code == 200:
                books_data = response.json().get('message')
                with transaction.atomic():
                    for book_data in books_data:
                        existing_book = Book.objects.filter(isbn=book_data['isbn']).first()
                        if existing_book:
                            existing_book.stock += num_books
                            existing_book.save()
                        else:
                            Book.objects.create(
                                title=book_data['title'],
                                author=book_data['authors'],
                                isbn=book_data['isbn'],
                                publisher=book_data['publisher'],
                                page_count=book_data['num_pages'],
                                stock=num_books
                            )
                return render(request, 'import_success.html')
            else:
                return render(request, 'import_error.html', {'error_message': 'Failed to fetch data from the API'})

        except Exception as e:
            return render(request, 'import_form.html', {'error_message': str(e)})

    return render(request, 'import_form.html')
