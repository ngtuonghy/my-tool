from django.urls import path
from . import views_simple, views_redirect

app_name = 'tool'

urlpatterns = [
    # Redirect root to simple page
    path('', views_redirect.redirect_to_simple, name='root'),
    
    # Simple workflow - upload and process immediately
    path('simple/', views_simple.index, name='index'),
    path('upload-simple/', views_simple.upload_and_process, name='upload'),
    path('download-simple/<str:filename>/', views_simple.download_simple, name='download'),
]
