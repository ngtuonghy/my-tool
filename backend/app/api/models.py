"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class UploadResponse(BaseModel):
    """Response for upload endpoint"""
    success: bool
    single_sheet: Optional[bool] = None
    multiple_sheets: Optional[bool] = None
    sheets: Optional[List[str]] = None
    temp_file: Optional[str] = None
    skip_rows: Optional[int] = None
    original_filename: Optional[str] = None
    filename: Optional[str] = None
    download_url: Optional[str] = None
    stats: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ProcessSheetsRequest(BaseModel):
    """Request for processing selected sheets"""
    temp_file: str
    selected_sheets: List[str]
    skip_rows: int = 0
    original_filename: str


class SheetResult(BaseModel):
    """Result for a single processed sheet"""
    sheet_name: str
    filename: Optional[str] = None
    download_url: Optional[str] = None
    stats: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class ProcessSheetsResponse(BaseModel):
    """Response for process sheets endpoint"""
    success: bool
    results: List[SheetResult]
    error: Optional[str] = None


class DownloadZipRequest(BaseModel):
    """Request for downloading all/selected sheets as ZIP"""
    temp_file: str
    selected_sheets: Optional[List[str]] = None
    skip_rows: int = 0
    original_filename: str


class DownloadZipResponse(BaseModel):
    """Response for download ZIP endpoint"""
    success: bool
    filename: Optional[str] = None
    download_url: Optional[str] = None
    sheets_processed: Optional[int] = None
    error: Optional[str] = None
