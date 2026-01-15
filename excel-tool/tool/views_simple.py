from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
import pandas as pd
import numpy as np
import os
from datetime import datetime

from .forms import ExcelUploadForm
from .utils import cleanup_old_files


def index(request):
    """Simple upload page"""
    form = ExcelUploadForm()
    return render(request, 'tool/simple.html', {'form': form})


@require_http_methods(["POST"])
def upload_and_process(request):
    """Upload file and process immediately"""
    form = ExcelUploadForm(request.POST, request.FILES)
    
    if not form.is_valid():
        errors = form.errors.as_json() if form.errors else 'Invalid form'
        return JsonResponse({
            'success': False,
            'error': f'Form validation failed: {errors}'
        }, status=400)
    
    try:
        # Get uploaded file
        uploaded_file = request.FILES['file_path']
        skip_rows = int(form.cleaned_data.get('skip_rows', 0) or 0)
        
        # Read Excel
        try:
            df = pd.read_excel(uploaded_file, engine='openpyxl', skiprows=skip_rows)
        except:
            try:
                df = pd.read_excel(uploaded_file, engine='xlrd', skiprows=skip_rows)
            except Exception as e:
                raise ValueError(f"Cannot read Excel file: {str(e)}")
        
        original_cols = len(df.columns)
        original_rows = len(df)
        
        # Remove empty columns
        df = df.dropna(axis=1, how='all')
        empty_cols_removed = original_cols - len(df.columns)
        
        # Rename Unnamed columns
        rename_dict = {}
        extra_counter = 1
        for col in df.columns:
            if 'Unnamed' in str(col):
                rename_dict[col] = f'Extra_Info_{extra_counter}'
                extra_counter += 1
        
        if rename_dict:
            df = df.rename(columns=rename_dict)
        
        # Generate output filename with extract_ prefix and timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = os.path.splitext(uploaded_file.name)[0]
        output_filename = f"extract_{base_name}_{timestamp}.csv"
        
        # Save to media/outputs/
        output_dir = os.path.join(settings.MEDIA_ROOT, 'outputs')
        os.makedirs(output_dir, exist_ok=True)
        
        # Cleanup old files before saving new one
        cleanup_old_files(output_dir, max_files=10)
        
        output_path = os.path.join(output_dir, output_filename)
        
        # Save CSV
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        return JsonResponse({
            'success': True,
            'filename': output_filename,
            'download_url': f'/excel/download-simple/{output_filename}/',
            'stats': {
                'original_rows': original_rows,
                'original_columns': original_cols,
                'final_columns': len(df.columns),
                'empty_columns_removed': empty_cols_removed,
                'unnamed_columns_renamed': len(rename_dict),
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Processing error: {str(e)}'
        }, status=400)


def download_simple(request, filename):
    """Download processed CSV file"""
    from urllib.parse import quote
    
    file_path = os.path.join(settings.MEDIA_ROOT, 'outputs', filename)
    
    if not os.path.exists(file_path):
        return JsonResponse({'error': 'File not found'}, status=404)
    
    response = FileResponse(open(file_path, 'rb'), content_type='text/csv')
    # Properly encode filename for Content-Disposition to handle special characters
    encoded_filename = quote(filename)
    response['Content-Disposition'] = f'attachment; filename*=UTF-8\'\'{encoded_filename}'
    return response
