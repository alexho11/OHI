from django.db import models

# Create your models here.
class Dataset(models.Model):
    variable = models.CharField(max_length=10)
    var_name = models.CharField(max_length=10)
    dataset_name = models.CharField(max_length=100)
    product = models.CharField(max_length=64)
    unit=models.CharField(max_length=10)
    # description = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.variable} from {self.product}"
    
class DataRecord(models.Model):
    variable = models.CharField(max_length=10)
    start_date = models.DateField()
    end_date = models.DateField()
    lon = models.FloatField()
    lat = models.FloatField()
    radius = models.IntegerField()
    requested_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.variable} from {self.start_date} to {self.end_date} at [{self.lon},{self.lat}] with radius {self.radius}"

class HealthRecord(models.Model):
    start_date = models.DateField()
    end_date = models.DateField()
    lon = models.FloatField()
    lat = models.FloatField()
    radius = models.IntegerField()
    requested_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Health record from {self.start_date} to {self.end_date} at [{self.lon},{self.lat}] with radius {self.radius}"
    