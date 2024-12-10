from django.db import models

class Process(models.Model):
    pid = models.IntegerField(unique=True)  # Process ID
    name = models.CharField(max_length=255)  # Process Name
    cpu_percent = models.FloatField()  # CPU Usage (%)
    memory_percent = models.FloatField()  # Memory Usage (%)
    start_time = models.DateTimeField()  # Process Start Time
    username = models.CharField(max_length=255, null=True, blank=True)  # Allow NULL values for username

    def __str__(self):
        return f"{self.name} ({self.pid})"
