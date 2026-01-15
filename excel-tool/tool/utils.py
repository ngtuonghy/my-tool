import pandas as pd
import os
from pathlib import Path
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import models


def read_excel_file(file_path):
    """
    Read Excel file and return pandas DataFrame
    
    Args:
        file_path: Path to Excel file
        
    Returns:
        pandas.DataFrame
    """
    try:
        # Try reading with openpyxl first (for .xlsx)
        df = pd.read_excel(file_path, engine='openpyxl')
    except Exception:
        try:
            # Fallback to xlrd for older .xls files
            df = pd.read_excel(file_path, engine='xlrd')
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {str(e)}")
    
    return df


def filter_columns(df, columns_to_keep):
    """
    Filter DataFrame to keep only specified columns
    
    Args:
        df: pandas.DataFrame
        columns_to_keep: List of column names to keep
        
    Returns:
        pandas.DataFrame with only selected columns
    """
    # Ensure all columns exist
    missing_cols = set(columns_to_keep) - set(df.columns)
    if missing_cols:
        raise ValueError(f"Columns not found: {missing_cols}")
    
    return df[columns_to_keep]


def remove_empty_rows(df):
    """
    Remove rows that are completely empty
    
    Args:
        df: pandas.DataFrame
        
    Returns:
        pandas.DataFrame with empty rows removed
    """
    return df.dropna(how='all')


def convert_to_csv(df, output_filename):
    """
    Convert DataFrame to CSV and save to media storage
    
    Args:
        df: pandas.DataFrame
        output_filename: Name for the output CSV file
        
    Returns:
        Path to saved CSV file
    """
    # Convert DataFrame to CSV string
    csv_content = df.to_csv(index=False, encoding='utf-8-sig')
    
    # Save to Django storage
    file_path = f'outputs/{output_filename}'
    saved_path = default_storage.save(file_path, ContentFile(csv_content.encode('utf-8-sig')))
    
    return saved_path


def get_csv_as_text(df):
    """
    Convert DataFrame to CSV text for clipboard copying
    
    Args:
        df: pandas.DataFrame
        
    Returns:
        CSV string
    """
    return df.to_csv(index=False, encoding='utf-8')


def process_excel_file(file_path, columns_to_keep=None, remove_empty=True, skip_rows=0):
    """
    Complete processing pipeline for Excel file
    
    Args:
        file_path: Path to Excel file
        columns_to_keep: List of columns to keep (None = keep all)
        remove_empty: Whether to remove empty rows
        skip_rows: Number of rows to skip from the beginning (default: 0)
        
    Returns:
        dict with processed DataFrame and metadata
    """
    # Read Excel file with skiprows parameter
    try:
        # Try reading with openpyxl first (for .xlsx)
        df = pd.read_excel(file_path, engine='openpyxl', skiprows=skip_rows)
    except Exception:
        try:
            # Fallback to xlrd for older .xls files
            df = pd.read_excel(file_path, engine='xlrd', skiprows=skip_rows)
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {str(e)}")
    
    original_rows = len(df)
    original_columns = list(df.columns)
    original_column_count = len(df.columns)
    
    # Step 1: Remove columns that are completely empty (all NaN)
    df = df.dropna(axis=1, how='all')
    empty_columns_removed = original_column_count - len(df.columns)
    
    # Step 2: Rename 'Unnamed' columns to more meaningful names for bot analysis
    rename_dict = {}
    extra_counter = 1
    for col in df.columns:
        if 'Unnamed' in str(col):
            rename_dict[col] = f'Extra_Info_{extra_counter}'
            extra_counter += 1
    
    if rename_dict:
        df = df.rename(columns=rename_dict)
    
    # Step 3: Filter columns if specified
    if columns_to_keep:
        df = filter_columns(df, columns_to_keep)
        columns_removed = list(set(original_columns) - set(columns_to_keep))
    else:
        columns_to_keep = list(df.columns)
        columns_removed = []
    
    # Step 4: Remove empty rows if requested
    if remove_empty:
        df = remove_empty_rows(df)
    
    processed_rows = len(df)
    
    return {
        'dataframe': df,
        'original_rows': original_rows,
        'processed_rows': processed_rows,
        'columns_kept': columns_to_keep,
        'columns_removed': columns_removed,
        'empty_columns_removed': empty_columns_removed,
        'unnamed_columns_renamed': len(rename_dict),
        'skip_rows': skip_rows,
    }


def cleanup_old_files(directory_path, max_files=10):
    """
    Delete oldest files in a directory if count exceeds max_files
    
    Args:
        directory_path: Path to the directory
        max_files: Maximum number of files to keep
    """
    if not os.path.exists(directory_path):
        return
    
    # Get all files with their modification times
    files = []
    for filename in os.listdir(directory_path):
        filepath = os.path.join(directory_path, filename)
        if os.path.isfile(filepath):
            files.append((filepath, os.path.getmtime(filepath)))
    
    # Sort files by modification time (oldest first)
    files.sort(key=lambda x: x[1])
    
    # Delete oldest files
    if len(files) > max_files:
        files_to_delete = files[:len(files) - max_files]
        for filepath, _ in files_to_delete:
            try:
                os.remove(filepath)
            except Exception as e:
                print(f"Error deleting file {filepath}: {e}")


def cleanup_old_instances(model_class, max_instances=10):
    """
    Delete oldest database instances and their associated files
    
    Args:
        model_class: The Django model class
        max_instances: Maximum number of records to keep
    """
    count = model_class.objects.count()
    if count > max_instances:
        # Get oldest instances (Django's queryset slicing is [start:stop])
        # To get the oldest, we use the default ordering (which is -timestamp)
        # and skip the first 'max_instances'.
        instances_to_delete = model_class.objects.all()[max_instances:]
        for instance in instances_to_delete:
            try:
                # Manually delete files if they exist
                for field in instance._meta.fields:
                    if isinstance(field, models.FileField):
                        file_field = getattr(instance, field.name)
                        if file_field and os.path.exists(file_field.path):
                            try:
                                os.remove(file_field.path)
                            except Exception as fe:
                                print(f"Error deleting file {file_field.path}: {fe}")
                
                instance.delete()
            except Exception as e:
                print(f"Error deleting instance {instance.id}: {e}")
