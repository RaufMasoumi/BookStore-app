from django.urls import path
from .views import CategoryBooksListView, CategoryListView, CategoryCreateView, CategoryUpdateView, \
    CategoryDeleteView

urlpatterns = [
    path('', CategoryListView.as_view(), name='category_list'),
    path('<int:pk>/', CategoryBooksListView.as_view(), name='category_books_list'),
    path('<int:pk>/page/<int:page>/', CategoryBooksListView.as_view(), name='category_books_list'),
    path('create/', CategoryCreateView.as_view(), name='category_create'),
    path('<int:pk>/update/', CategoryUpdateView.as_view(), name='category_update'),
    path('<int:pk>/delete/', CategoryDeleteView.as_view(), name='category_delete'),
]
