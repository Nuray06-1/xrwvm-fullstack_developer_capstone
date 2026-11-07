from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from django.views.decorators.csrf import ensure_csrf_cookie
urlpatterns=[path('admin/',admin.site.urls),path('djangoapp/',include('djangoapp.urls')),
 re_path(r'^(?:about|contact|login|register|dealer/\d+|review/\d+)?/?$',ensure_csrf_cookie(TemplateView.as_view(template_name='index.html')))]
