from django.contrib import admin
from django.urls import path
from .views import *

urlpatterns = [
    path('books/',book_list, name='book_list'),
    path('add/',add_book, name='add_book'),
    path('members/',member_list, name='member_list'),
    path('issue/<int:book_id>/',issue_book, name='issue_book'),
    path('return/<int:transaction_id>/', return_book, name='return_book'),
    path('search/', search_books, name='search_books'),
    path('charge_fee/<int:member_id>/', charge_fee, name='charge_fee'),
    path('import/',import_books, name='import_books'),
]   