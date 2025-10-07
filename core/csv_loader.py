"""
Complete CSV input handler - replaces the broken core/input_handler.py
Handles file uploads, validation, and data processing correctly
"""
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional

REQUIRED_COLUMNS = {"Tool Name", "Category", "Used By", "Criticality"}

def load_input(file_path: str) -> pd.DataFrame:
    """
    Load and validate tech stack CSV file.
    Actually uses the file_path parameter (fixes the original bug).
    """
    if not file_path:
        raise ValueError("No file path provided")
    
    file_path_obj = Path(file_path)
    if not file_path_obj.exists():
        raise ValueError(f"File not found: {file_path}")
    
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        raise ValueError(f"Failed to read CSV file: {e}")
    
    # Validate required columns
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    
    # Clean data
    df = df.dropna(subset=["Tool Name"])
    df = df.drop_duplicates(subset=["Tool Name"])
    
    if df.empty:
        raise ValueError("No valid tool data found after cleaning")
    
    return df

def convert_df_to_tool_inventory(df: pd.DataFrame) -> Dict[str, dict]:
    """
    Convert DataFrame to tool inventory format used by the audit system.
    """
    tool_inventory = {}
    
    for _, row in df.iterrows():
        tool_name = str(row['Tool Name']).strip()
        if not tool_name or tool_name.lower() == 'nan':
            continue
        
        # Handle users field - can be comma-separated
        users_raw = row.get('Used By', '')
        if pd.isna(users_raw) or str(users_raw).lower() == 'nan':
            users = ['Unknown']
        else:
            users = [u.strip() for u in str(users_raw).split(',') if u.strip()]
            if not users:
                users = ['Unknown']
        
        tool_inventory[tool_name] = {
            'category': str(row.get('Category', 'Unknown')).strip(),
            'users': users,
            'criticality': str(row.get('Criticality', 'Medium')).strip(),
            'discovery_method': 'csv_upload'
        }
    
    return tool_inventory

def validate_and_load_csv(file_path: str) -> Tuple[Dict[str, dict], List[str]]:
    """
    Complete CSV processing: load, validate, and convert to tool inventory.
    Returns: (tool_inventory, errors)
    """
    errors = []
    
    try:
        df = load_input(file_path)
        tool_inventory = convert_df_to_tool_inventory(df)
        
        if not tool_inventory:
            errors.append("No valid tools found in CSV")
            return {}, errors
        
        return tool_inventory, errors
        
    except Exception as e:
        errors.append(str(e))
        return {}, errors

def save_uploaded_file(uploaded_file_content: bytes, filename: str) -> str:
    """
    Save uploaded file content to a temporary file.
    Returns the file path.
    """
    from datetime import datetime
    
    # Create temp directory
    temp_dir = Path("data/temp")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Create unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_filename = "".join(c for c in filename if c.isalnum() or c in ".-_")
    temp_path = temp_dir / f"{timestamp}_{safe_filename}"
    
    # Save file
    with open(temp_path, 'wb') as f:
        f.write(uploaded_file_content)
    
    return str(temp_path)

# Compatibility functions for existing code
def load_and_validate_input(file_path: str) -> pd.DataFrame:
    """Legacy compatibility function"""
    return load_input(file_path)

def process_tool_inventory(df: pd.DataFrame) -> Dict[str, dict]:
    """Legacy compatibility function"""  
    return convert_df_to_tool_inventory(df)