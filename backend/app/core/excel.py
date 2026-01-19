"""
Excel processing utilities
Ported from Django views_simple.py
"""
import pandas as pd
import os
import zipfile
import tempfile
from typing import List, Dict, Any, Tuple
from datetime import datetime


def detect_sheets(file_path: str) -> List[str]:
    """Detect all sheet names in an Excel file"""
    try:
        excel_file = pd.ExcelFile(file_path, engine='openpyxl')
    except:
        try:
            excel_file = pd.ExcelFile(file_path, engine='xlrd')
        except Exception as e:
            raise ValueError(f"Cannot read Excel file: {str(e)}")
    
    return excel_file.sheet_names


def clean_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Clean dataframe by removing empty columns and renaming unnamed columns
    Returns cleaned dataframe and statistics
    """
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
    
    return {
        'dataframe': df,
        'original_rows': original_rows,
        'original_columns': original_cols,
        'final_columns': len(df.columns),
        'empty_columns_removed': empty_cols_removed,
        'unnamed_columns_renamed': len(rename_dict)
    }


def process_single_sheet(
    file_path: str, 
    sheet_name: str, 
    skip_rows: int = 0
) -> Dict[str, Any]:
    """Process a single sheet from Excel file"""
    # Read sheet
    df = pd.read_excel(file_path, sheet_name=sheet_name, skiprows=skip_rows)
    
    # Clean dataframe
    result = clean_dataframe(df)
    
    return result


def save_to_csv(df: pd.DataFrame, output_path: str) -> None:
    """Save dataframe to CSV file"""
    df.to_csv(output_path, index=False, encoding='utf-8-sig')


def sanitize_sheet_name(sheet_name: str) -> str:
    """Sanitize sheet name for use in filename"""
    return "".join(c for c in sheet_name if c.isalnum() or c in (' ', '-', '_')).strip()


def generate_filename(base_name: str, sheet_name: str = None, extension: str = 'csv') -> str:
    """Generate output filename with timestamp"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if sheet_name:
        safe_sheet_name = sanitize_sheet_name(sheet_name)
        return f"extract_{base_name}_{safe_sheet_name}_{timestamp}.{extension}"
    else:
        return f"extract_{base_name}_{timestamp}.{extension}"


def create_zip_archive(
    csv_files: List[Tuple[str, str]], 
    zip_path: str
) -> None:
    """
    Create ZIP archive from list of CSV files
    csv_files: List of (filename, filepath) tuples
    """
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for csv_filename, csv_path in csv_files:
            zipf.write(csv_path, csv_filename)
