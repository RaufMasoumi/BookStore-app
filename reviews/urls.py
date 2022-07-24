from django.urls import path
from .views import ReviewCreateView, ReviewUpdateView, ReviewDeleteView, ReviewReplyCreateView, \
      ReviewReplyUpdateView, ReviewReplyDeleteView, update_votes


urlpatterns = [
    path('create/', ReviewCreateView.as_view(), name='review_create'),
    path('<int:pk>/update/', ReviewUpdateView.as_view(), name='review_update'),
    path('<int:pk>/delete/', ReviewDeleteView.as_view(), name='review_delete'),
    path('votes/', update_votes, name='votes_update'),
    path('replies/create/', ReviewReplyCreateView.as_view(), name='reply_create'),
    path('replies/<int:pk>/update/', ReviewReplyUpdateView.as_view(), name='reply_update'),
    path('replies/<int:pk>/delete/', ReviewReplyDeleteView.as_view(), name='reply_delete'),
]
