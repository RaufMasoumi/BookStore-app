from django.urls import path
from .views import BookListView, BookDetailView, BookCreateView, BookUpdateView, SearchResultsView
urlpatterns = [
    path('', BookListView.as_view(), name='book_list'),
    path('<uuid:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('create/', BookCreateView.as_view(), name='book_create'),
    path('<uuid:pk>/update/', BookUpdateView.as_view(), name='book_update'),
    path('search/', SearchResultsView.as_view(), name='search_results'),
]