import pandas as pd
from typing import Dict, Any, List


def profile_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Profiles a relational pandas DataFrame to extract statistical attributes,
    value repetition frequencies, and candidate functional dependencies.
    """
    num_rows, num_cols = df.shape
    column_types = {col: str(dtype) for col, dtype in df.dtypes.items()}
    unique_counts = {col: int(df[col].nunique(dropna=False)) for col in df.columns}
    cardinality_ratio = {
        col: round(count / num_rows, 4) if num_rows > 0 else 0.0
        for col, count in unique_counts.items()
    }
    missing_values = {col: int(df[col].isna().sum()) for col in df.columns}
    duplicate_rows = int(df.duplicated().sum())

    # Identify repeated value columns (low to medium cardinality ratio, non-unique)
    repeated_cols = [
        col for col, ratio in cardinality_ratio.items()
        if ratio < 0.8 and num_rows > 1
    ]

    # Detect candidate functional dependencies (C1 -> C2)
    candidate_dependencies: List[str] = []
    cols = list(df.columns)
    for i, col1 in enumerate(cols):
        # Exclude high-cardinality text columns or single-value constants as determinant
        if unique_counts[col1] <= 1 or cardinality_ratio[col1] >= 0.99:
            continue
        
        for j, col2 in enumerate(cols):
            if i == j:
                continue
            
            # Check if each value of col1 deterministically maps to a single value in col2
            grouped = df.groupby(col1, observed=True)[col2].nunique(dropna=False)
            if (grouped <= 1).all():
                candidate_dependencies.append(f"{col1} -> {col2}")

    return {
        "rows": num_rows,
        "columns": num_cols,
        "column_types": column_types,
        "unique_counts": unique_counts,
        "cardinality_ratio": cardinality_ratio,
        "missing_values": missing_values,
        "duplicate_rows": duplicate_rows,
        "repeated_value_columns": repeated_cols,
        "candidate_dependencies": candidate_dependencies,
    }
