import pandas as pd
import numpy as np

def compare_excel_files(file1_path, file2_path, key_column=None):
    """
    Compare two Excel files with improved accuracy.
    
    Args:
        key_column: Column name to use for matching rows (e.g., 'id', 'name')
                   If None, compares by position (row index)
    """
    # Read both Excel files
    df1 = pd.read_excel(file1_path)
    df2 = pd.read_excel(file2_path)
    
    print(f"File 1 shape: {df1.shape}")
    print(f"File 2 shape: {df2.shape}")

    # Normalize column names
    df1.columns = df1.columns.str.strip().str.lower()
    df2.columns = df2.columns.str.strip().str.lower()

    # Identify missing columns
    missing_in_file2 = sorted(list(set(df1.columns) - set(df2.columns)))
    missing_in_file1 = sorted(list(set(df2.columns) - set(df1.columns)))

    # Find shared columns
    common_columns = sorted(list(set(df1.columns) & set(df2.columns)))
    
    differences = []

    if key_column:
        # Match rows by key column
        key_col = key_column.strip().lower()
        
        if key_col not in common_columns:
            print(f"\nERROR: Key column '{key_column}' not found in both files!")
            return
        
        # Merge on key column
        merged = df1.merge(df2, on=key_col, how='outer', suffixes=('_file1', '_file2'), indicator=True)
        
        # Find rows only in one file
        only_in_file1 = merged[merged['_merge'] == 'left_only']
        only_in_file2 = merged[merged['_merge'] == 'right_only']
        
        print(f"\nRows only in File 1: {len(only_in_file1)}")
        print(f"Rows only in File 2: {len(only_in_file2)}")
        
        # Compare common rows
        common_rows = merged[merged['_merge'] == 'both']
        
        for idx, row in common_rows.iterrows():
            key_value = row[key_col]
            
            for col in common_columns:
                if col == key_col:
                    continue
                
                val1 = row.get(f'{col}_file1', np.nan)
                val2 = row.get(f'{col}_file2', np.nan)
                
                # Skip if both are NaN
                if pd.isna(val1) and pd.isna(val2):
                    continue
                
                # Compare values with type awareness
                if not values_equal(val1, val2):
                    differences.append({
                        "key": key_value,
                        "column": col,
                        "file1_value": val1,
                        "file2_value": val2,
                        "file1_type": type(val1).__name__,
                        "file2_type": type(val2).__name__
                    })
    else:
        # Position-based comparison (original method, but improved)
        max_len = max(len(df1), len(df2))
        
        for i in range(max_len):
            for col in common_columns:
                val1 = df1.iloc[i][col] if i < len(df1) else np.nan
                val2 = df2.iloc[i][col] if i < len(df2) else np.nan

                # Skip if both are NaN
                if pd.isna(val1) and pd.isna(val2):
                    continue

                # Compare values
                if not values_equal(val1, val2):
                    differences.append({
                        "row": i + 1,
                        "column": col,
                        "file1_value": val1,
                        "file2_value": val2,
                        "file1_type": type(val1).__name__,
                        "file2_type": type(val2).__name__
                    })

    # Summarize
    summary = {
        "rows_in_file1": len(df1),
        "rows_in_file2": len(df2),
        "missing_columns_in_file2": len(missing_in_file2),
        "missing_columns_in_file1": len(missing_in_file1),
        "differences_found": len(differences)
    }

    # Print results
    print("\n=== SUMMARY ===")
    for k, v in summary.items():
        print(f"{k}: {v}")
    
    if missing_in_file2:
        print(f"\nColumns in File1 but not in File2: {missing_in_file2}")
    if missing_in_file1:
        print(f"\nColumns in File2 but not in File1: {missing_in_file1}")

    if differences:
        print(f"\n=== DETAILED DIFFERENCES ({len(differences)} total) ===")
        diff_df = pd.DataFrame(differences)
        print(diff_df.to_string(max_rows=50))
        
        # Save to Excel for easier review
        output_file = "comparison_differences.xlsx"
        diff_df.to_excel(output_file, index=False)
        print(f"\nFull differences saved to: {output_file}")
    else:
        print("\n✓ No differences found!")


def values_equal(val1, val2):
    """Compare two values accounting for type and NaN"""
    # Both NaN
    if pd.isna(val1) and pd.isna(val2):
        return True
    
    # One is NaN, other isn't
    if pd.isna(val1) or pd.isna(val2):
        return False
    
    # Numeric comparison
    if isinstance(val1, (int, float)) and isinstance(val2, (int, float)):
        return abs(val1 - val2) < 1e-9
    
    # String comparison (case-sensitive)
    return str(val1).strip() == str(val2).strip()


# Usage examples:

# If you have a key column (recommended):
# compare_excel_files(
#     r"C:\Users\atharvsj\Downloads\kaas_table_check.xlsx",
#     r"C:\Users\atharvsj\Downloads\dss_table_check.xlsx",
#     key_column="id"  # or "name", "employee_id", etc.
# )

# Without key column (position-based):
compare_excel_files(
    r"C:\Users\atharvsj\Downloads\kaas_table_check.xlsx",
    r"C:\Users\atharvsj\Downloads\dss_table_check.xlsx"
)