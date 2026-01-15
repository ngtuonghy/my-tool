import pandas as pd

def main():
    # Read Excel file starting from row 9 (skip first 8 rows)
    excel_file = r"HKKSZFIL_回収情報Ｆ_移行ツール.xls"
    
    try:
        df = pd.read_excel(excel_file, skiprows=8)
        
        print("Excel data loaded (from row 9):")
        print(f"Original shape: {df.shape[0]} rows, {df.shape[1]} columns")
        
        # Only remove columns that are completely empty (all NaN)
        # Keep all columns with any data, including Unnamed columns with comments
        df_cleaned = df.dropna(axis=1, how='all')
        
        print(f"After removing completely empty columns: {df_cleaned.shape[1]} columns")
        print(f"Removed {df.shape[1] - df_cleaned.shape[1]} empty columns")
        
        # Rename 'Unnamed' columns to more meaningful names for bot analysis
        rename_dict = {}
        extra_counter = 1
        for col in df_cleaned.columns:
            if 'Unnamed' in str(col):
                rename_dict[col] = f'Extra_Info_{extra_counter}'
                extra_counter += 1
        
        if rename_dict:
            df_cleaned = df_cleaned.rename(columns=rename_dict)
            print(f"\nRenamed {len(rename_dict)} 'Unnamed' columns to 'Extra_Info_X' format")
        
        # Display first few rows to verify
        print("\nFirst 5 rows of cleaned data:")
        print(df_cleaned.head())
        
        # Convert to CSV with proper Japanese encoding
        csv_file = r"HKKSZFIL_回収情報Ｆ_移行ツール.csv"
        df_cleaned.to_csv(csv_file, index=False, encoding='utf-8-sig')
        
        print(f"\n✓ Successfully converted {excel_file} to {csv_file}")
        print(f"CSV file saved with {df_cleaned.shape[0]} rows and {df_cleaned.shape[1]} columns")
        print(f"\nColumn names:")
        for i, col in enumerate(df_cleaned.columns, 1):
            print(f"  {i}. {col}")
        
    except FileNotFoundError:
        print(f"❌ Error: File '{excel_file}' not found!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
