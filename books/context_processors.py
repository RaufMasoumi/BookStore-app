from .models import Book


def new_books(request):
    ordered_books = Book.objects.published()
    books_dict = {'new_books': ordered_books[:4]}
    return books_dict


def bestseller_books(request):
    books = Book.objects.bestseller()
    books_dict = {'bestseller_books': books[:10]}
    return books_dict


def mostpopular_books(request):
    books = Book.objects.mostpopular()
    books_dict = {'mostpopular_books': books[:10]}
    return books_dict


