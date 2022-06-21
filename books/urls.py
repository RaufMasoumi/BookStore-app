from django.urls import path
from .views import *

urlpatterns = [
    path('<uuid:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('drafts/<uuid:pk>/', DraftBookDetailView.as_view(), name='draft_book_detail'),
    path('drafts/make-published/', book_make_published, name='book_make_published'),
    path('create/', BookCreateView.as_view(), name='book_create'),
    path('<uuid:pk>/update/', BookUpdateView.as_view(), name='book_update'),
    path('<uuid:pk>/delete/', BookDeleteView.as_view(), name='book_delete'),
    path('categories/', CategoryListView.as_view(), name='category_list'),
    path('categories/<int:pk>/', CategoryBooksListView.as_view(), name='category_books_list'),
    path('categories/<int:pk>/page/<int:page>/', CategoryBooksListView.as_view(), name='category_books_list'),
    path('categories/create/', CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/update/', CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),
    path('search/', SearchResultsView.as_view(), name='search_results'),
    path('search/<int:page>/', SearchResultsView.as_view(), name='search_results'),
    path('compare/', BookComparingView.as_view(), name='book_comparing'),
    path('reviews/create/', ReviewCreateView.as_view(), name='review_create'),
    path('reviews/<int:pk>/update/', ReviewUpdateView.as_view(), name='review_update'),
    path('reviews/<int:pk>/delete/', ReviewDeleteView.as_view(), name='review_delete'),
    path('reviews/votes/', update_votes, name='votes_update'),
    path('reviews/replies/create/', ReviewReplyCreateView.as_view(), name='reply_create'),
    path('reviews/replies/<int:pk>/update/', ReviewReplyUpdateView.as_view(), name='reply_update'),
    path('reviews/replies/<int:pk>/delete/', ReviewReplyDeleteView.as_view(), name='reply_delete'),
]