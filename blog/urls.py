from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.BlogListView.as_view(), name='blog_list'),
    path('category/<slug:slug>/', views.BlogCategoryView.as_view(), name='blog_category'),
    path('tag/<slug:slug>/', views.BlogTagView.as_view(), name='blog_tag'),
    path('search/', views.search_blog, name='blog_search'),
    path('post/<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),
    path('post/<slug:slug>/comment/', views.add_comment, name='add_comment'),
]