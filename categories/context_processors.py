from .models import Category


def active_categories(request):
    categories = Category.objects.active()
    display_categories = [Category.objects.filter(status=True, parent=None).first()]
    categories_dict = {'categories': categories, 'display_categories': display_categories}
    return categories_dict