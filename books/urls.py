from django.urls import path
from .views import BookListView, BookDetailView, BookCreateView, BookUpdateView, \
    SearchResultsView, ReviewUpdateView, ReviewDeleteView, save_review
urlpatterns = [
    path('', BookListView.as_view(), name='book_list'),
    path('<uuid:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('create/', BookCreateView.as_view(), name='book_create'),
    path('<uuid:pk>/update/', BookUpdateView.as_view(), name='book_update'),
    path('search/', SearchResultsView.as_view(), name='search_results'),
    path('reviews/<int:pk>/update/', ReviewUpdateView.as_view(), name='review_update'),
    path('reviews/<int:pk>/delete/', ReviewDeleteView.as_view(), name='review_delete'),
    path('reviews/save/', save_review, name='review_save'),
]