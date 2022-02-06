from django.urls import path
from .views import *

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('about/', AboutPageView.as_view(), name='about'),
    path('hello/', hello),
    path('index/', IndexView.as_view(), name='index'),
    path('new-about/', AboutView.as_view(), name='new-about'),
    path('account/', AccountView.as_view(), name='account'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('contacts/', ContenctsView.as_view(), name='contacts'),
    path('faq/', FaqView.as_view(), name='faq'),
    path('goods/', GoodsView.as_view(), name='goods'),
    path('item/', ItemView.as_view(), name='item'),
    path('privacy/', PrivacyPolicyView.as_view(), name='privacy'),
    path('product/list/', ProductListView.as_view(), name='product_list'),
    path('search/', SearchResultView.as_view(), name='search_result'),
    path('cart/', ShoppingCartView.as_view(), name='shopping_cart'),
    path('cart/null/', ShoppingCartNullView.as_view(), name='shopping_cart_null'),
    path('standard/forms/', StandardFormsView.as_view(), name='standard_forms'),
    path('terms/', TermsConditionsView.as_view(), name='terms'),
    path('wishlist/', WishListView.as_view(), name='wishlist'),
]