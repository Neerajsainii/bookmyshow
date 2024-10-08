"""
URL configuration for bookmyshow project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('', views.index),
    path('register', views.RegisterView.as_view(), name='register'),
    path('login_as', views.login_as,name='login_as'),
    path('login', views.LoginView.as_view(), name='login'),
    path('logout', views.LogoutView.as_view(), name='logout'),
    path('book-ticket/', views.book_ticket, name='book_ticket'),
    path('view-bookings/', views.view_bookings, name='view_bookings'),
    path('cancel-booking/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    path('createvent/', views.createvent),
    path('create-event/', views.create_event, name='create_event'),
    
]
