from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.
from django.db import models

class CarMake(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name
    

class Vehicle(models.Model):
    date = models.DateField()
    registration_number = models.CharField(max_length=20)
    year = models.IntegerField()
    mileage = models.IntegerField(null=True, blank=True)
    time_in = models.TimeField()
    work_completed = models.BooleanField(default=False)
    car_make = models.ForeignKey(CarMake, on_delete=models.CASCADE)
    model = models.CharField(max_length=100)
    color = models.CharField(max_length=30)
    customer_name = models.CharField(max_length=100)
    contact_number = models.CharField(max_length=15)
    engine_number = models.CharField(max_length=30)
    vin_number = models.CharField(max_length=30)
    reported_defect = models.TextField()
    body_marks = models.TextField()  
    completed_on = models.DateField(null=True, blank=True)  # Add this field

    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.registration_number} - {self.customer_name}"

class RepairJob(models.Model):
    vehicle = models.ForeignKey(Vehicle, related_name='repair_jobs', on_delete=models.CASCADE)
    technician_name = models.CharField(max_length=100)
    date = models.DateField()

    def __str__(self):
        return f"Repair Job on {self.date} for {self.vehicle}"

class Part(models.Model):
    repair_job = models.ForeignKey(RepairJob, related_name='parts', on_delete=models.CASCADE)
    part_number = models.CharField(max_length=100)
    description = models.CharField(max_length=255)
    quantity = models.IntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    labor_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return self.part_number

class RepairCost(models.Model):
    vehicle = models.OneToOneField(Vehicle, related_name='repair_cost', on_delete=models.CASCADE)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"Repair Cost for {self.vehicle}"

@receiver(post_save, sender=Part)
def update_repair_cost(sender, instance, **kwargs):
    # Get or create a RepairCost object for the vehicle
    repair_cost, created = RepairCost.objects.get_or_create(vehicle=instance.repair_job.vehicle)
    # Calculate subtotal and total based on parts and labor
    parts_cost = sum(part.quantity * part.unit_price + part.labor_cost for part in instance.repair_job.parts.all())
    repair_cost.subtotal = parts_cost
    # Assuming total is the same as subtotal, but you can add additional costs here
    repair_cost.total = parts_cost
    repair_cost.save()