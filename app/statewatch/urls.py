from django.urls import path
from statewatch import views

urlpatterns = [
    path('', views.api_root),
    path('sites/',
         views.SiteList.as_view(),
         name='site-list'),
    path('sites/<str:pk>/',
         views.SiteDetail.as_view(),
         name='site-detail'),
    path('sites/<str:pk>/checks/', views.SiteChecks.as_view()),
    path('sites/<str:pk>/downtime/', views.SiteDowntime.as_view()),
    path('sites/<str:pk>/changes_filtered/', views.SiteChangesFiltered.as_view()),
    path('sites/<str:pk>/changes_unfiltered/', views.SiteChangesUnfiltered.as_view()),
    path('checks/<int:pk>', views.CheckDetail.as_view()),
    path('blob/<str:pk>', views.get_blob),
    path('diff/<str:a>/<str:b>', views.diff_blob),
]
