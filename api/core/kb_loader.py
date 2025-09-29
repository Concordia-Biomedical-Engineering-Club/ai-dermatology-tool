import json
import re
from pathlib import Path
import aiofiles

BASE_DIR = Path(__file__).resolve().parent.parent  # go up from api/core/
print(BASE_DIR)
knowledge_base_file = BASE_DIR / "data" / "knowledge_base.txt"


def parse_knowledge_base(text):
    """Parses the raw text into a list of condition dictionaries."""
    # (Code is identical to the previous version)
    conditions = []
    pattern = re.compile(
        r"\[Condition:\s*(.*?)\]\n(.*?)(?=\n\s*\[Condition:|\Z)",
        re.DOTALL | re.IGNORECASE,
    )
    category_pattern = re.compile(r"^\s*(\d+)\.\s+(.*?)\s*$", re.MULTILINE)

    categories = {
        match.group(1): match.group(2).strip()
        for match in category_pattern.finditer(text)
    }
    category_positions = {
        match.start(): match.group(1) for match in category_pattern.finditer(text)
    }
    sorted_cat_positions = sorted(category_positions.keys())

    current_category_num = None

    for match in pattern.finditer(text):
        condition_name = match.group(1).strip()
        details_text = match.group(2).strip()
        condition_start_pos = match.start()

        # Determine category based on position
        determined_category = "Unknown"  # Default
        for i, pos in enumerate(sorted_cat_positions):
            next_pos_index = i + 1
            next_pos = (
                sorted_cat_positions[next_pos_index]
                if next_pos_index < len(sorted_cat_positions)
                else float("inf")
            )
            if pos <= condition_start_pos < next_pos:
                determined_category_num = category_positions[pos]
                determined_category = categories.get(determined_category_num, "Unknown")
                break

        red_flags = []
        rule = ""
        ddx = []
        flags_raw_text = ""

        lines = details_text.split("\n")
        in_flags_section = False
        flags_buffer = ""  # Buffer to collect flag text across lines

        for line in lines:
            stripped_line = line.strip()
            line_lower = stripped_line.lower()

            if line_lower.startswith("- red flags:"):
                in_flags_section = True
                # Start collecting flags, handle text after colon on the same line
                try:
                    flags_buffer += line.split(":", 1)[1].strip() + " "
                except IndexError:
                    pass  # No text after colon on this line
                continue  # Move to the next line

            # Check for end markers BEFORE processing potential flag lines
            if line_lower.startswith("- rule:") or line_lower.startswith("- ddx:"):
                in_flags_section = False  # Stop collecting flags
                # Process rule or ddx AFTER flags section ends
                if line_lower.startswith("- rule:"):
                    try:
                        rule = stripped_line.split(":", 1)[1].strip()
                    except IndexError:
                        rule = ""  # Handle empty rule
                elif line_lower.startswith("- ddx:"):
                    try:
                        ddx_str = stripped_line.split(":", 1)[1].strip()
                        ddx = [d.strip() for d in ddx_str.split(",") if d.strip()]
                    except IndexError:
                        ddx_str = ""
                        ddx = []
                continue  # Move to next line after processing rule/ddx start

            # If we are still in the flags section, append the line content
            if in_flags_section and stripped_line:
                # Append the content, remove leading hyphens if present
                flag_content = (
                    stripped_line[1:].strip()
                    if stripped_line.startswith("-")
                    else stripped_line
                )
                flags_buffer += flag_content + " "

        # Assign the collected buffer to flags_raw_text after the loop
        flags_raw_text = flags_buffer.strip()

        # Process flags_raw_text into a list
        potential_flags = re.split(
            r"[,\n|]", flags_raw_text
        )  # Split by comma, newline, or pipe
        processed_flags = set()
        for flag in potential_flags:
            cleaned_flag = flag.strip()
            # Basic cleanup of leading/trailing brackets/parentheses etc.
            cleaned_flag = re.sub(
                r"^[\[\(']*(.*?)[\]\)']*\s*$", r"\1", cleaned_flag
            ).strip()
            if cleaned_flag:
                processed_flags.add(cleaned_flag)

        conditions.append(
            {
                "name": condition_name,
                "category": determined_category,  # Use determined category
                "red_flags_list": list(processed_flags),
                "red_flags_text": " | ".join(
                    processed_flags
                ).lower(),  # Join with pipes for text matching
                "num_flags": len(processed_flags),
                "rule": rule,
                "ddx": ddx,
            }
        )

    if not conditions:
        print("Warning: No conditions parsed. Check knowledge base format and content.")

    return conditions


async def load_knowledge():
    conditions_database = None
    print("Loading knowledge base...")
    if not knowledge_base_file.exists():
        print(f"Error: {knowledge_base_file} not found")
        return []

    async with aiofiles.open(knowledge_base_file, "r", encoding="utf-8") as f:
        lines = await f.read()

    conditions_database = parse_knowledge_base(lines)
    if not conditions_database:
        print("Failed to load knowledge base. Server may not work properly.")
    else:
        print(f"Loaded {len(conditions_database)} conditions.")
    return conditions_database
