from django.urls import path
from . import views

urlpatterns = [
    path('', views.contact_page, name='contact'),
    path('inbox/', views.inbox, name='inbox'),
    path('inbox/<int:message_id>/', views.message, name='message'),
    path('delete/<int:message_id>/',
         views.delete_message, name="delete_message")
]
