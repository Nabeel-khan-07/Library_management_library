from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13)
    publisher = models.CharField(max_length=255)
    page_count = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

class Member(models.Model):
    name = models.CharField(max_length=255)
    outstanding_debt = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.name

class Transaction(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    issue_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.member} borrowed {self.book}" 
