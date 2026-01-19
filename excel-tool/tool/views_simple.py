from django.shortcuts import render
from django.http import JsonResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
import pandas as pd
import numpy as np
import os
import zipfile
import tempfile
from datetime import datetime

from .forms import ExcelUploadForm
from .utils import cleanup_old_files


def index(request):
    """Simple upload page"""
    form = ExcelUploadForm()
    return render(request, 'tool/simple.html', {'form': form})


@require_http_methods(["POST"])
def upload_and_process(request):
    """Upload file and check for multiple sheets"""
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
        
        # Save file temporarily to check sheets
        temp_dir = os.path.join(settings.MEDIA_ROOT, 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_filename = f"temp_{timestamp}_{uploaded_file.name}"
        temp_path = os.path.join(temp_dir, temp_filename)
        
        with open(temp_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # Check for multiple sheets
        try:
            excel_file = pd.ExcelFile(temp_path, engine='openpyxl')
        except:
            try:
                excel_file = pd.ExcelFile(temp_path, engine='xlrd')
            except Exception as e:
                os.remove(temp_path)
                raise ValueError(f"Cannot read Excel file: {str(e)}")
        
        sheet_names = excel_file.sheet_names
        
        # If single sheet, process immediately (backward compatible)
        if len(sheet_names) == 1:
            df = pd.read_excel(temp_path, sheet_name=sheet_names[0], skiprows=skip_rows)
            os.remove(temp_path)  # Clean up temp file
            
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
                'single_sheet': True,
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
        
        # Multiple sheets - return sheet info for user selection
        else:
            return JsonResponse({
                'success': True,
                'single_sheet': False,
                'multiple_sheets': True,
                'sheets': sheet_names,
                'temp_file': temp_filename,
                'skip_rows': skip_rows,
                'original_filename': uploaded_file.name
            })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Processing error: {str(e)}'
        }, status=400)


@require_http_methods(["POST"])
def process_selected_sheets(request):
    """Process selected sheets from Excel file"""
    import json
    
    try:
        data = json.loads(request.body)
        temp_filename = data.get('temp_file')
        selected_sheets = data.get('selected_sheets', [])
        skip_rows = int(data.get('skip_rows', 0))
        original_filename = data.get('original_filename', 'file')
        
        if not temp_filename or not selected_sheets:
            return JsonResponse({
                'success': False,
                'error': 'Missing required parameters'
            }, status=400)
        
        temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', temp_filename)
        
        if not os.path.exists(temp_path):
            return JsonResponse({
                'success': False,
                'error': 'Temporary file not found'
            }, status=404)
        
        # Process each selected sheet
        results = []
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = os.path.splitext(original_filename)[0]
        
        for sheet_name in selected_sheets:
            try:
                # Read sheet
                df = pd.read_excel(temp_path, sheet_name=sheet_name, skiprows=skip_rows)
                
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
                
                # Generate output filename
                safe_sheet_name = "".join(c for c in sheet_name if c.isalnum() or c in (' ', '-', '_')).strip()
                output_filename = f"extract_{base_name}_{safe_sheet_name}_{timestamp}.csv"
                
                # Save to media/outputs/
                output_dir = os.path.join(settings.MEDIA_ROOT, 'outputs')
                os.makedirs(output_dir, exist_ok=True)
                
                output_path = os.path.join(output_dir, output_filename)
                
                # Save CSV
                df.to_csv(output_path, index=False, encoding='utf-8-sig')
                
                results.append({
                    'sheet_name': sheet_name,
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
                results.append({
                    'sheet_name': sheet_name,
                    'error': str(e)
                })
        
        # Cleanup temp file
        try:
            os.remove(temp_path)
        except:
            pass
        
        # Cleanup old files
        output_dir = os.path.join(settings.MEDIA_ROOT, 'outputs')
        cleanup_old_files(output_dir, max_files=20)
        
        return JsonResponse({
            'success': True,
            'results': results
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Processing error: {str(e)}'
        }, status=400)


@require_http_methods(["POST"])
def download_all_sheets_zip(request):
    """Process all sheets and return as ZIP file"""
    import json
    
    try:
        data = json.loads(request.body)
        temp_filename = data.get('temp_file')
        skip_rows = int(data.get('skip_rows', 0))
        original_filename = data.get('original_filename', 'file')
        
        if not temp_filename:
            return JsonResponse({
                'success': False,
                'error': 'Missing required parameters'
            }, status=400)
        
        temp_path = os.path.join(settings.MEDIA_ROOT, 'temp', temp_filename)
        
        if not os.path.exists(temp_path):
            return JsonResponse({
                'success': False,
                'error': 'Temporary file not found'
            }, status=404)
        
        # Read all sheets
        try:
            excel_file = pd.ExcelFile(temp_path, engine='openpyxl')
        except:
            excel_file = pd.ExcelFile(temp_path, engine='xlrd')
        
        sheet_names = excel_file.sheet_names
        
        # Create temporary directory for CSV files
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base_name = os.path.splitext(original_filename)[0]
        csv_files = []
        
        for sheet_name in sheet_names:
            try:
                # Read sheet
                df = pd.read_excel(temp_path, sheet_name=sheet_name, skiprows=skip_rows)
                
                # Remove empty columns
                df = df.dropna(axis=1, how='all')
                
                # Rename Unnamed columns
                rename_dict = {}
                extra_counter = 1
                for col in df.columns:
                    if 'Unnamed' in str(col):
                        rename_dict[col] = f'Extra_Info_{extra_counter}'
                        extra_counter += 1
                
                if rename_dict:
                    df = df.rename(columns=rename_dict)
                
                # Generate CSV filename
                safe_sheet_name = "".join(c for c in sheet_name if c.isalnum() or c in (' ', '-', '_')).strip()
                csv_filename = f"extract_{safe_sheet_name}.csv"
                
                # Save to temp location
                temp_csv_path = os.path.join(tempfile.gettempdir(), csv_filename)
                df.to_csv(temp_csv_path, index=False, encoding='utf-8-sig')
                
                csv_files.append((csv_filename, temp_csv_path))
                
            except Exception as e:
                print(f"Error processing sheet {sheet_name}: {str(e)}")
        
        # Create ZIP file
        zip_filename = f"extract_{base_name}_{timestamp}.zip"
        zip_dir = os.path.join(settings.MEDIA_ROOT, 'outputs')
        os.makedirs(zip_dir, exist_ok=True)
        
        zip_path = os.path.join(zip_dir, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for csv_filename, csv_path in csv_files:
                zipf.write(csv_path, csv_filename)
        
        # Cleanup temp CSV files
        for _, csv_path in csv_files:
            try:
                os.remove(csv_path)
            except:
                pass
        
        # Cleanup temp Excel file
        try:
            os.remove(temp_path)
        except:
            pass
        
        # Cleanup old files
        cleanup_old_files(zip_dir, max_files=20)
        
        return JsonResponse({
            'success': True,
            'filename': zip_filename,
            'download_url': f'/excel/download-simple/{zip_filename}/',
            'sheets_processed': len(csv_files)
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
