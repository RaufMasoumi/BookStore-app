from django.urls import path
from .views import BookDetailView, DraftBookDetailView, book_make_published, BookCreateView, BookUpdateView, \
    BookDeleteView, SearchResultsView, BookComparingView

urlpatterns = [
    path('<uuid:pk>/', BookDetailView.as_view(), name='book_detail'),
    path('drafts/<uuid:pk>/', DraftBookDetailView.as_view(), name='draft_book_detail'),
    path('drafts/make-published/', book_make_published, name='book_make_published'),
    path('create/', BookCreateView.as_view(), name='book_create'),
    path('<uuid:pk>/update/', BookUpdateView.as_view(), name='book_update'),
    path('<uuid:pk>/delete/', BookDeleteView.as_view(), name='book_delete'),
    path('search/', SearchResultsView.as_view(), name='search_results'),
    path('search/<int:page>/', SearchResultsView.as_view(), name='search_results'),
    path('compare/', BookComparingView.as_view(), name='book_comparing'),
]