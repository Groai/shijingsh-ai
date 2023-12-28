from django.urls import path
from .views import *

urlpatterns=[
    path('Login',index,name='index'),
    path('',Jobcart,name='jobcart'),
    path('login/', custom_login, name='login'),
    path('vechile_list/',vehicle_list,name='vechile_list'),
    path('vehicle/repair/<int:vehicle_id>/',repair_job_entry, name='repair_job_entry'),
    path('vehicle/edit/<str:regnumber>/', edit_vehicle, name='edit_vehicle'),
    # path('bill/view/<int:repair_job_id>/', view_bill, name='view_bill'),
    path('vehicle/finish-work/<int:vehicle_id>/', finish_work, name='finish_work'),
    path('finshed/',finished,name='finished'),
    path('checkout/',Checkout,name='checkout'),
    path('vehicle/<int:vehicle_id>/repair-details/',vehicle_repair_details, name='vehicle_repair_details'),


    # path('bill/download/<int:repair_job_id>/', download_bill, name='download_bill'),



]
