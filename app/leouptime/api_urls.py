from django.urls import path

from . import views

urlpatterns = [
    path("", views.api_root),
    path("sites-down/", views.SiteDownList.as_view()),
    path("sites/", views.SiteList.as_view(), name="site-list"),
    path("sites/<str:pk>/", views.SiteDetail.as_view(), name="site-detail"),
    path("sites/<str:pk>/checks/", views.SiteChecks.as_view()),
    path("sites/<str:pk>/downtime/", views.SiteDowntime.as_view()),
]
