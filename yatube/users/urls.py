from django.contrib.auth.views import LoginView

from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path(
        'signup/',
        views.SignUp.as_view(),
        name="signup"),
    path(
        'logout/',
        views.Logout.as_view(),
        name='logout'),
    path(
        'login/',
        LoginView.as_view(
            template_name='users/login.html'),
        name='login'),
    path(
        'password_reset_form/',
        views.Login.as_view(),
        name='password_reset_form'),
]
