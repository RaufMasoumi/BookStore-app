from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, UpdateView, DeleteView
from .models import Review, ReviewReply
# Create your views here.


class ReviewCreateView(CreateView):
    model = Review
    fields = ('author', 'name', 'email', 'book', 'review', 'rating')
    template_name = 'reviews/review_create.html'

    def form_valid(self, form):
        user = self.request.user
        if user.is_authenticated:
            form.instance.author = user
            form.instance.name = user.username
            form.instance.email = user.email
        return super().form_valid(form)


class ReviewUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Review
    fields = ('review',)
    template_name = 'reviews/review_update.html'
    login_url = 'account_login'

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user or self.request.user.has_perm('books.change_review')


class ReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Review
    login_url = 'account_login'
    template_name = 'reviews/review_delete.html'

    def get_success_url(self):
        obj = self.get_object()
        return obj.book.get_absolute_url()
        
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user or self.request.user.has_perm('books.delete_review')


class ReviewReplyCreateView(CreateView):
    model = ReviewReply
    fields = ('author', 'name', 'email', 'review', 'to', 'reply')
    template_name = 'reviews/replies/review_reply_create.html'
    login_url = 'account_login'

    def form_valid(self, form):
        user = self.request.user
        if user.is_authenticated:
            form.instance.author = user
            form.instance.name = user.username
            form.instance.email = user.email
        return super().form_valid(form)


class ReviewReplyUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = ReviewReply
    fields = ('reply', )
    template_name = 'reviews/replies/review_reply_update.html'
    login_url = 'account_login'

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user or self.request.user.has_perm('books.change_reviewreply')


class ReviewReplyDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = ReviewReply
    template_name = 'reviews/replies/review_reply_delete.html'
    login_url = 'account_login'

    def get_success_url(self):
        obj = self.get_object()
        return obj.review.get_absolute_url()

    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user or self.request.user.has_perm('books.delete_reviewreply')


@require_POST
def update_votes(request):
    post = request.POST
    if post.get('positive'):
        pos_vote = True
    else:
        pos_vote = False

    if post.get('review'):
        pk = post['review']
        review = get_object_or_404(Review, pk=pk)
        if pos_vote:
            review.votes += 1
        else:
            review.votes -= 1
        review.save()
        return redirect(review.get_absolute_url())

    if post.get('reply'):
        pk = post['reply']
        reply = get_object_or_404(ReviewReply, pk=pk)
        if pos_vote:
            reply.votes += 1
        else:
            reply.votes -= 1
        reply.save()
        return redirect(reply.get_absolute_url())