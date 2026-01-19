"""
API Routes for Excel processing
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import FileResponse
import os
import tempfile
from pathlib import Path
from datetime import datetime

from app.core.config import settings
from app.core import excel
from app.utils.cleanup import cleanup_old_files
from app.api.models import (
    UploadResponse,
    ProcessSheetsRequest,
    ProcessSheetsResponse,
    SheetResult,
    DownloadZipRequest,
    DownloadZipResponse
)

router = APIRouter()

# Ensure directories exist
Path(settings.UPLOAD_DIR).mkdir(exist_ok=True)
Path(settings.OUTPUT_DIR).mkdir(exist_ok=True)


@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    skip_rows: int = Form(0)
):
    """
    Upload Excel file and detect sheets
    Returns sheet list if multiple, or processes immediately if single
    """
    try:
        # Save uploaded file temporarily
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        temp_filename = f"temp_{timestamp}_{file.filename}"
        temp_path = os.path.join(settings.UPLOAD_DIR, temp_filename)
        
        # Write file
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Detect sheets
        sheet_names = excel.detect_sheets(temp_path)
        
        # Single sheet - process immediately
        if len(sheet_names) == 1:
            result = excel.process_single_sheet(temp_path, sheet_names[0], skip_rows)
            
            # Generate output filename
            base_name = Path(file.filename).stem
            output_filename = excel.generate_filename(base_name)
            output_path = os.path.join(settings.OUTPUT_DIR, output_filename)
            
            # Save CSV
            excel.save_to_csv(result['dataframe'], output_path)
            
            # Cleanup temp file
            os.remove(temp_path)
            
            # Cleanup old files
            cleanup_old_files(settings.OUTPUT_DIR, settings.MAX_FILES)
            
            return UploadResponse(
                success=True,
                single_sheet=True,
                filename=output_filename,
                download_url=f"/api/download/{output_filename}",
                stats={
                    'original_rows': result['original_rows'],
                    'original_columns': result['original_columns'],
                    'final_columns': result['final_columns'],
                    'empty_columns_removed': result['empty_columns_removed'],
                    'unnamed_columns_renamed': result['unnamed_columns_renamed']
                }
            )
        
        # Multiple sheets - return sheet list
        else:
            return UploadResponse(
                success=True,
                single_sheet=False,
                multiple_sheets=True,
                sheets=sheet_names,
                temp_file=temp_filename,
                skip_rows=skip_rows,
                original_filename=file.filename
            )
    
    except Exception as e:
        return UploadResponse(
            success=False,
            error=f"Processing error: {str(e)}"
        )


@router.post("/process-sheets", response_model=ProcessSheetsResponse)
async def process_sheets(request: ProcessSheetsRequest):
    """Process selected sheets from Excel file"""
    try:
        temp_path = os.path.join(settings.UPLOAD_DIR, request.temp_file)
        
        if not os.path.exists(temp_path):
            raise HTTPException(status_code=404, detail="Temporary file not found")
        
        results = []
        base_name = Path(request.original_filename).stem
        
        for sheet_name in request.selected_sheets:
            try:
                # Process sheet
                result = excel.process_single_sheet(temp_path, sheet_name, request.skip_rows)
                
                # Generate output filename
                output_filename = excel.generate_filename(base_name, sheet_name)
                output_path = os.path.join(settings.OUTPUT_DIR, output_filename)
                
                # Save CSV
                excel.save_to_csv(result['dataframe'], output_path)
                
                results.append(SheetResult(
                    sheet_name=sheet_name,
                    filename=output_filename,
                    download_url=f"/api/download/{output_filename}",
                    stats={
                        'original_rows': result['original_rows'],
                        'original_columns': result['original_columns'],
                        'final_columns': result['final_columns'],
                        'empty_columns_removed': result['empty_columns_removed'],
                        'unnamed_columns_renamed': result['unnamed_columns_renamed']
                    }
                ))
            
            except Exception as e:
                results.append(SheetResult(
                    sheet_name=sheet_name,
                    error=str(e)
                ))
        
        # Cleanup temp file
        try:
            os.remove(temp_path)
        except:
            pass
        
        # Cleanup old files
        cleanup_old_files(settings.OUTPUT_DIR, settings.MAX_FILES)
        
        return ProcessSheetsResponse(
            success=True,
            results=results
        )
    
    except Exception as e:
        return ProcessSheetsResponse(
            success=False,
            results=[],
            error=f"Processing error: {str(e)}"
        )


@router.post("/download-zip", response_model=DownloadZipResponse)
async def download_zip(request: DownloadZipRequest):
    """Process all or selected sheets and return as ZIP file"""
    try:
        temp_path = os.path.join(settings.UPLOAD_DIR, request.temp_file)
        
        if not os.path.exists(temp_path):
            raise HTTPException(status_code=404, detail="Temporary file not found")
        
        # Determine sheets to process
        if request.selected_sheets:
            sheet_names = request.selected_sheets
        else:
            # Detect all sheets
            sheet_names = excel.detect_sheets(temp_path)
        
        # Process sheets
        csv_files = []
        base_name = Path(request.original_filename).stem
        
        for sheet_name in sheet_names:
            try:
                # Process sheet
                result = excel.process_single_sheet(temp_path, sheet_name, request.skip_rows)
                
                # Generate CSV filename
                safe_sheet_name = excel.sanitize_sheet_name(sheet_name)
                csv_filename = f"extract_{safe_sheet_name}.csv"
                
                # Save to temp location
                temp_csv_path = os.path.join(tempfile.gettempdir(), csv_filename)
                excel.save_to_csv(result['dataframe'], temp_csv_path)
                
                csv_files.append((csv_filename, temp_csv_path))
            
            except Exception as e:
                print(f"Error processing sheet {sheet_name}: {str(e)}")
        
        # Create ZIP file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        zip_filename = f"extract_{base_name}_{timestamp}.zip"
        zip_path = os.path.join(settings.OUTPUT_DIR, zip_filename)
        
        excel.create_zip_archive(csv_files, zip_path)
        
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
        cleanup_old_files(settings.OUTPUT_DIR, settings.MAX_FILES)
        
        return DownloadZipResponse(
            success=True,
            filename=zip_filename,
            download_url=f"/api/download/{zip_filename}",
            sheets_processed=len(csv_files)
        )
    
    except Exception as e:
        return DownloadZipResponse(
            success=False,
            error=f"Processing error: {str(e)}"
        )


@router.get("/download/{filename}")
async def download_file(filename: str):
    """Download processed CSV or ZIP file"""
    file_path = os.path.join(settings.OUTPUT_DIR, filename)
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine content type
    content_type = "application/zip" if filename.endswith('.zip') else "text/csv"
    
    return FileResponse(
        path=file_path,
        media_type=content_type,
        filename=filename
    )
