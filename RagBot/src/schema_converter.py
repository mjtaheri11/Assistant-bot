
import yaml
from typing import Optional


TYPE_MAP = {
    "string": "VARCHAR",
    "date": "DATE",
    "int64": "BIGINT",
    "bool": "BOOLEAN",
    "enum": "VARCHAR",
    "float64": "DOUBLE PRECISION",
    "decimal": "NUMERIC",
}


def yaml_to_enriched_ddl(yaml_str: str) -> str:
    """
    Convert the refined YAML business object to an enriched DDL string
    suitable for the text-to-SQL prompt.

    This is the recommended approach:
      - Store metadata as YAML (version-controlled, human-editable)
      - Convert to DDL at inference time (LLM-friendly)
    """
    data = yaml.safe_load(yaml_str)

    for table_name, table_def in data.items():
        lines = []

        # Table-level comments
        title = table_def.get("title", "")
        desc = table_def.get("description", "").strip().replace("\n", " ")
        lines.append(f"-- Table: {table_name}")
        if title:
            lines.append(f"-- Title: {title}")
        if desc:
            lines.append(f"-- Description: {desc}")

        # Business rules as comments
        rules = table_def.get("business_rules", [])
        if rules:
            lines.append("-- Business Rules:")
            for rule in rules:
                rule_desc = rule.get("description", "").strip().replace("\n", " ")
                lines.append(f"--   * {rule_desc}")

        lines.append("")
        lines.append(f"CREATE TABLE {table_name} (")

        # Columns
        columns = table_def.get("columns", [])
        col_lines = []
        for col in columns:
            col_name = col["name"]
            col_type = TYPE_MAP.get(col["type"], "VARCHAR")
            col_title = col.get("title", "")

            # Build comment parts
            comment_parts = [col_title]

            # Add description if present and different from title
            col_desc = col.get("description", "").strip().replace("\n", " ")
            if col_desc and col_desc != col_title:
                comment_parts.append(col_desc)

            # Add allowed values for enums
            allowed = col.get("allowed_values", [])
            if allowed:
                vals_str = ", ".join(f"'{v}'" for v in allowed)
                comment_parts.append(f"مقادیر مجاز: {vals_str}")

            # Add sample values
            samples = col.get("sample_values", [])
            if samples:
                samples_str = ", ".join(f"'{v}'" for v in samples)
                comment_parts.append(f"مثال: {samples_str}")

            # Add nullable hint
            if col.get("nullable"):
                comment_parts.append("ممکن است خالی باشد")

            comment = " | ".join(filter(None, comment_parts))
            col_line = f"    {col_name:<35} {col_type}"
            if comment:
                col_line += f",  -- {comment}"
            else:
                col_line += ","

            col_lines.append(col_line)

        # Remove trailing comma from last column
        if col_lines:
            col_lines[-1] = col_lines[-1].rstrip(",").rstrip()
            # re-check: if ends with comma before comment
            last = col_lines[-1]
            if ",  --" in last:
                # fine, the comma is before the comment
                pass
            else:
                # remove trailing comma
                col_lines[-1] = col_lines[-1].rstrip(",")

        lines.extend(col_lines)
        lines.append(");")

        return "\n".join(lines)


def yaml_to_mschema(yaml_str: str) -> str:
    """
    Convert the refined YAML business object to M-Schema format
    (XiYan-SQL style semi-structured representation).
    """
    data = yaml.safe_load(yaml_str)

    for table_name, table_def in data.items():
        lines = []

        context = table_def.get("context", "default")
        title = table_def.get("title", "")
        desc = table_def.get("description", "").strip().replace("\n", " ")

        lines.append(f"【DB_ID】 {context}")
        lines.append("")
        lines.append(f"# Table: {table_name}")
        if title:
            lines.append(f"# Title: {title}")
        if desc:
            lines.append(f"# Description: {desc}")

        # Business rules
        rules = table_def.get("business_rules", [])
        if rules:
            for rule in rules:
                rule_desc = rule.get("description", "").strip().replace("\n", " ")
                lines.append(f"# Rule: {rule_desc}")

        lines.append("")
        lines.append("## Columns:")

        columns = table_def.get("columns", [])
        for col in columns:
            col_name = col["name"]
            col_type = TYPE_MAP.get(col["type"], "VARCHAR")
            col_title = col.get("title", "")

            entry = f"  - {col_name} ({col_type}): {col_title}"

            # Add allowed values inline
            allowed = col.get("allowed_values", [])
            if allowed:
                vals_str = str(allowed)
                entry += f". Values: {vals_str}"

            # Add sample values
            samples = col.get("sample_values", [])
            if samples:
                entry += f". Examples: {samples}"

            lines.append(entry)

        # Foreign keys
        lines.append("")
        relations = table_def.get("relations", [])
        lines.append("【Foreign Keys】")
        if relations:
            for rel in relations:
                lines.append(f"  {rel['from']} → {rel['to']}")
        else:
            lines.append("  (none)")

        return "\n".join(lines)

