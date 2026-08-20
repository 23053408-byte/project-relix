import pandas as pd
from typing import List, Dict, Optional

# Supported workload task instructions
WORKLOAD_INSTRUCTIONS: Dict[str, str] = {
    "sentiment": (
        "You are a sentiment analyzer. Given the product metadata and customer review below, "
        "classify the overall sentiment as 'positive', 'neutral', or 'negative'."
    ),
    "entity_extraction": (
        "You are an entity extraction assistant. Given the record below, extract key product "
        "and brand entities in JSON format."
    ),
    "attribute_extraction": (
        "You are a product attribute extractor. Identify key features, specs, and pros/cons "
        "mentioned in the text."
    ),
}


def generate_prompt_for_row(
    row: pd.Series,
    field_order: List[str],
    task_type: str = "sentiment",
    custom_system_prompt: Optional[str] = None
) -> str:
    """
    Generates a deterministic LLM query prompt for a single record row,
    formatting fields according to the specified field_order.
    """
    instruction = custom_system_prompt or WORKLOAD_INSTRUCTIONS.get(
        task_type, WORKLOAD_INSTRUCTIONS["sentiment"]
    )

    formatted_fields = []
    for field in field_order:
        if field in row.index:
            val = row[field]
            formatted_fields.append(f"{field.replace('_', ' ').title()}: {val}")

    record_block = "\n".join(formatted_fields)

    prompt = f"{instruction}\n\n[Record]\n{record_block}\n\n[Output]:"
    return prompt


def generate_prompts(
    df: pd.DataFrame,
    field_order: Optional[List[str]] = None,
    task_type: str = "sentiment",
    custom_system_prompt: Optional[str] = None
) -> List[str]:
    """
    Generates deterministic LLM prompts for all rows in the dataset dataframe.
    """
    if field_order is None:
        field_order = list(df.columns)

    prompts = [
        generate_prompt_for_row(
            row, field_order, task_type=task_type, custom_system_prompt=custom_system_prompt
        )
        for _, row in df.iterrows()
    ]
    return prompts
