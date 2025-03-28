from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    path('', views.portfolio_list, name='portfolio'),
    path('case-study/<int:case_study_id>/', views.case_study_detail, name='case_study'),
    path('category/<str:category>/', views.portfolio_category, name='portfolio_category'),
]