from django.db import models
from django.utils import timezone
import json


class UploadedFile(models.Model):
    """Track uploaded Excel files"""
    original_filename = models.CharField(max_length=255)
    file_path = models.FileField(upload_to='uploads/%Y/%m/%d/')
    file_size = models.IntegerField(help_text="File size in bytes")
    upload_timestamp = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-upload_timestamp']
    
    def __str__(self):
        return f"{self.original_filename} ({self.upload_timestamp.strftime('%Y-%m-%d %H:%M')})"


class ConversionHistory(models.Model):
    """Track all conversion operations"""
    STATUS_CHOICES = [
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    
    uploaded_file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE, related_name='conversions')
    columns_selected = models.JSONField(help_text="List of column names that were kept")
    columns_removed = models.JSONField(help_text="List of column names that were removed")
    output_csv_path = models.FileField(upload_to='outputs/%Y/%m/%d/')
    conversion_timestamp = models.DateTimeField(default=timezone.now)
    rows_processed = models.IntegerField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='success')
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-conversion_timestamp']
        verbose_name_plural = "Conversion histories"
    
    def __str__(self):
        return f"{self.uploaded_file.original_filename} - {self.conversion_timestamp.strftime('%Y-%m-%d %H:%M')}"
