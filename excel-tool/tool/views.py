from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, FileResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.conf import settings
import json
import numpy as np
import os
from datetime import datetime

from .models import UploadedFile, ConversionHistory
from .forms import ExcelUploadForm
from .utils import read_excel_file, process_excel_file, convert_to_csv, get_csv_as_text, cleanup_old_instances


def index(request):
    """Main page with upload form and history"""
    form = ExcelUploadForm()
    history = ConversionHistory.objects.select_related('uploaded_file').all()[:10]
    
    context = {
        'form': form,
        'history': history,
    }
    return render(request, 'excel_processor/index.html', context)


@require_http_methods(["POST"])
def upload_file(request):
    """Handle file upload and return preview data"""
    form = ExcelUploadForm(request.POST, request.FILES)
    
    if form.is_valid():
        # Save uploaded file
        uploaded_file = form.save(commit=False)
        uploaded_file.original_filename = request.FILES['file_path'].name
        uploaded_file.file_size = request.FILES['file_path'].size
        uploaded_file.save()
        
        # Cleanup old uploads
        cleanup_old_instances(UploadedFile, max_instances=10)
        
        # Get skip_rows from form
        skip_rows = form.cleaned_data.get('skip_rows', 0) or 0
        
        try:
            # Read Excel file for preview with skip_rows
            file_path = uploaded_file.file_path.path
            import pandas as pd
            import numpy as np
            
            try:
                df = pd.read_excel(file_path, engine='openpyxl', skiprows=skip_rows)
            except:
                try:
                    df = pd.read_excel(file_path, engine='xlrd', skiprows=skip_rows)
                except Exception as e:
                    raise ValueError(f"Cannot read Excel file: {str(e)}")
            
            # Replace NaN and NaT with None for JSON serialization
            df = df.replace({np.nan: None, pd.NaT: None})
            
            # Convert to JSON for preview (first 100 rows)
            preview_data = df.head(100).to_dict('records')
            columns = list(df.columns)
            total_rows = len(df)
            
            return JsonResponse({
                'success': True,
                'file_id': uploaded_file.id,
                'filename': uploaded_file.original_filename,
                'columns': columns,
                'preview_data': preview_data,
                'total_rows': total_rows,
                'skip_rows': skip_rows,
            })
        
        except Exception as e:
            uploaded_file.delete()
            return JsonResponse({
                'success': False,
                'error': f'Error processing file: {str(e)}'
            }, status=400)
    
    # Form validation errors
    errors = form.errors.as_json() if form.errors else 'Invalid form data'
    return JsonResponse({
        'success': False,
        'error': f'Form validation failed: {errors}'
    }, status=400)



@require_http_methods(["POST"])
def process_file(request):
    """Process file with selected columns and return CSV"""
    try:
        data = json.loads(request.body)
        file_id = data.get('file_id')
        columns_to_keep = data.get('columns', [])
        skip_rows = data.get('skip_rows', 0)
        
        uploaded_file = get_object_or_404(UploadedFile, id=file_id)
        file_path = uploaded_file.file_path.path
        
        # Process the file with skip_rows parameter
        result = process_excel_file(file_path, columns_to_keep, remove_empty=True, skip_rows=skip_rows)
        df = result['dataframe']
        
        # Generate output filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = os.path.splitext(uploaded_file.original_filename)[0]
        output_filename = f"{base_name}_{timestamp}.csv"
        
        # Save CSV
        csv_path = convert_to_csv(df, output_filename)
        
        # Create conversion history
        conversion = ConversionHistory.objects.create(
            uploaded_file=uploaded_file,
            columns_selected=result['columns_kept'],
            columns_removed=result['columns_removed'],
            output_csv_path=csv_path,
            rows_processed=result['processed_rows'],
            status='success'
        )
        
        # Cleanup old conversions
        cleanup_old_instances(ConversionHistory, max_instances=10)
        
        # Get CSV as text for clipboard
        csv_text = get_csv_as_text(df)
        
        # Prepare preview data for the processed result
        df_preview = df.replace({np.nan: None, pd.NaT: None})
        preview_data = df_preview.head(100).to_dict('records')
        
        return JsonResponse({
            'success': True,
            'conversion_id': conversion.id,
            'csv_text': csv_text,
            'download_url': f'/excel/download/{conversion.id}/',
            'rows_processed': result['processed_rows'],
            'empty_columns_removed': result.get('empty_columns_removed', 0),
            'unnamed_columns_renamed': result.get('unnamed_columns_renamed', 0),
            'preview_data': preview_data,
            'columns': list(df.columns),
            'filename': output_filename,
            'total_rows': result['processed_rows'],
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


def download_csv(request, conversion_id):
    """Download processed CSV file"""
    conversion = get_object_or_404(ConversionHistory, id=conversion_id)
    
    file_path = conversion.output_csv_path.path
    filename = os.path.basename(file_path)
    
    response = FileResponse(open(file_path, 'rb'), content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


def get_history(request):
    """Get conversion history as JSON"""
    history = ConversionHistory.objects.select_related('uploaded_file').all()[:20]
    
    data = [{
        'id': item.id,
        'filename': item.uploaded_file.original_filename,
        'timestamp': item.conversion_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'rows_processed': item.rows_processed,
        'columns_kept': len(item.columns_selected),
        'status': item.status,
    } for item in history]
    
    return JsonResponse({'history': data})


def load_conversion(request, conversion_id):
    """Load a previous conversion for preview"""
    conversion = get_object_or_404(ConversionHistory, id=conversion_id)
    
    try:
        # Read the CSV file
        file_path = conversion.output_csv_path.path
        import pandas as pd
        df = pd.read_csv(file_path)
        
        preview_data = df.head(100).to_dict('records')
        
        return JsonResponse({
            'success': True,
            'filename': conversion.uploaded_file.original_filename,
            'columns': list(df.columns),
            'preview_data': preview_data,
            'total_rows': len(df),
            'conversion_id': conversion.id,
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
