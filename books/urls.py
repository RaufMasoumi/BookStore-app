from django.urls import path
from .views import BookListView, BookDetailView, SearchResultsView
urlpatterns = [
    path('', BookListView.as_view(), name='book_list'),
    path('<uuid:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('search/', SearchResultsView.as_view(), name='search_result'),
]