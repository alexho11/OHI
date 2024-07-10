from django.contrib import admin
from .models import Dataset, DataRecord, HealthRecord


# Register your models here.
admin.site.register(Dataset)
admin.site.register(DataRecord)
admin.site.register(HealthRecord)