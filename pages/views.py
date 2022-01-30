from django.shortcuts import render
from django.views.generic import TemplateView
from books.forms import BookSearchForm
# Create your views here.


class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = BookSearchForm()
        return context


class AboutPageView(TemplateView):
    template_name = 'about.html'


def hello(request):
    return render(request, 'hello.html')