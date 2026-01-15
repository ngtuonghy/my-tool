from django.contrib import admin
from .models import UploadedFile, ConversionHistory


@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ['original_filename', 'file_size', 'upload_timestamp']
    list_filter = ['upload_timestamp']
    search_fields = ['original_filename']
    readonly_fields = ['upload_timestamp']


@admin.register(ConversionHistory)
class ConversionHistoryAdmin(admin.ModelAdmin):
    list_display = ['uploaded_file', 'conversion_timestamp', 'rows_processed', 'status']
    list_filter = ['status', 'conversion_timestamp']
    search_fields = ['uploaded_file__original_filename']
    readonly_fields = ['conversion_timestamp']
