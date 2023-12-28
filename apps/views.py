from django.shortcuts import get_object_or_404, render
from .models import *
from django.shortcuts import render, redirect
from .models import Vehicle  # Import your model here
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib import messages
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from django.utils import timezone
from django.db.models import Sum

# Create your views here.
def index(request):
    incomplete_vehicles_count = Vehicle.objects.filter(work_completed=False).count()
    finished_vehicles_count = Vehicle.objects.filter(work_completed=True).count()
    total_repair_cost = RepairCost.objects.aggregate(total_sum=Sum('total'))['total_sum']


    context = {
        'incomplete_vehicles_count': incomplete_vehicles_count,
        'finished_vehicles_count':finished_vehicles_count,
        'total_repair_cost':total_repair_cost,
        # ... other context data ...
    }

    return render(request,'index.html',context)



def custom_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect to a success page.
            return redirect('index')  # Replace 'home' with your target page
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'login.html')

def Jobcart(request):
    if request.method == 'POST':
        # Extract form data
        date = request.POST.get('date')
        regnumber = request.POST.get('regnumber')
        year = request.POST.get('year')
        mileage = request.POST.get('mileage')
        time_in = request.POST.get('timein')
        car_make_name = request.POST.get('car_make')
        car_model = request.POST.get('car_model')
        color = request.POST.get('color')
        customer_name = request.POST.get('customer_name')
        contact_number = request.POST.get('contact_number')
        engine_number = request.POST.get('engine_number')
        vin_no = request.POST.get('vinno')
        defect = request.POST.get('defect')
        marks = request.POST.get('marks')

        car_make, created = CarMake.objects.get_or_create(name=car_make_name)

        vehicle = Vehicle(
            date=date,
            registration_number=regnumber,
            year=year,
            mileage=mileage,
            time_in=time_in,
            car_make=car_make,
            model=car_model,
            color=color,
            customer_name=customer_name,
            contact_number=contact_number,
            engine_number=engine_number,
            vin_number=vin_no,
            reported_defect=defect,
            body_marks=marks,
        )
        vehicle.save()

        # Redirect or respond after saving data
        return redirect('/')  # Replace 'success_url' with the name of your success URL

    # Render your form template if method is not POST
    return render(request, 'jobcartpage.html')
def edit_vehicle(request, regnumber):
    vehicle = get_object_or_404(Vehicle, registration_number=regnumber)

    if request.method == 'POST':
        # Extract form data and update the vehicle
        vehicle.registration_number= request.POST.get('regnumber')
        vehicle.year = request.POST.get('year')
        vehicle.mileage = request.POST.get('mileage', vehicle.mileage)  # Using existing value as default
        car_make_name = request.POST.get('car_make')
        vehicle.model = request.POST.get('car_model')
        vehicle.color = request.POST.get('color')
        vehicle.customer_name = request.POST.get('customer_name')
        vehicle.contact_number = request.POST.get('contact_number')
        vehicle.engine_number = request.POST.get('engine_number')
        vehicle.vin_number = request.POST.get('vinno')
        vehicle.reported_defect = request.POST.get('defect')
        vehicle.body_marks = request.POST.get('marks')

        car_make, _ = CarMake.objects.get_or_create(name=car_make_name)
        vehicle.car_make = car_make

        vehicle.save()
        return redirect('vechile_list')

    return render(request, 'edit_vehicle.html', {'vehicle': vehicle})

def vehicle_list(request):
    vehicles = Vehicle.objects.filter(work_completed=False)
    return render(request, 'vehicle_list.html', {'vehicles': vehicles})


def repair_job_entry(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)

    if request.method == 'POST':
        technician_name = request.POST.get('technician_name')
        date = request.POST.get('date')

        # Create or update a RepairJob instance
        repair_job, created = RepairJob.objects.update_or_create(
            vehicle=vehicle,
            date=date,
            defaults={'technician_name': technician_name}
        )

        # Process each part
        part_numbers = request.POST.getlist('part_numbers[]')
        descriptions = request.POST.getlist('descriptions[]')
        quantities = request.POST.getlist('quantities[]')
        unit_prices = request.POST.getlist('unit_prices[]')
        labor_costs = request.POST.getlist('labor_costs[]')

        # Clear existing parts if this is an update
        if not created:
            Part.objects.filter(repair_job=repair_job).delete()

        total_parts_cost = 0
        for i in range(len(part_numbers)):
            part = Part.objects.create(
                repair_job=repair_job,
                part_number=part_numbers[i],
                description=descriptions[i],
                quantity=int(quantities[i]),
                unit_price=float(unit_prices[i]),
                labor_cost=float(labor_costs[i])
            )
            total_parts_cost += part.quantity * part.unit_price + part.labor_cost

        # Update RepairCost for the vehicle
        repair_cost, created = RepairCost.objects.get_or_create(vehicle=vehicle)
        repair_cost.subtotal = total_parts_cost
        repair_cost.total = total_parts_cost
        repair_cost.save()

        # Mark the vehicle as completed and update the completed date
        vehicle.completed = True
        vehicle.completed_on = timezone.now().date()  # Set the completion date to the current date
        vehicle.save()

        # Redirect to a success or summary page
        return redirect('checkout')

    # Render the repair job form
    return render(request, 'checkout.html', {'vehicle': vehicle})


def view_bill(request, repair_job_id):
    repair_job = get_object_or_404(RepairJob, pk=repair_job_id)
    parts = Part.objects.filter(repair_job=repair_job)
    repair_cost = RepairCost.objects.get(vehicle=repair_job.vehicle)

    context = {
        'repair_job': repair_job,
        'parts': parts,
        'repair_cost': repair_cost
    }
    return render(request, 'bill.html', context)



def finish_work(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
    if not vehicle.work_completed:
        vehicle.work_completed = True
        vehicle.completed_on = timezone.now().date()  # Set the completion date
        vehicle.save()
    return redirect('vechile_list') 

def finished(request):
    vehicle_finished=Vehicle.objects.filter(work_completed=True,completed=True)
    return render(request,'finished.html',{'vehicle_finished':vehicle_finished})

def Checkout(request):
    vehicles = Vehicle.objects.filter(work_completed=True,completed=False)
    return render(request,'checkoutpage.html',{'vehicles': vehicles})


def vehicle_repair_details(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, pk=vehicle_id)
    repair_jobs = RepairJob.objects.filter(vehicle=vehicle)
    repair_cost = RepairCost.objects.get(vehicle=vehicle)

    # Assuming each repair job might have multiple parts
    parts = Part.objects.filter(repair_job__in=repair_jobs)
    
    context = {
        'vehicle': vehicle,
        'repair_jobs': repair_jobs,
        'parts': parts,
        'repair_cost': repair_cost,
    }
    return render(request, 'vehicle_repair_details.html', context)



