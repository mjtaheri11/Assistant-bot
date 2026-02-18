
from __future__ import annotations
from typing import Any


# ── Type maps ────────────────────────────────────────────────────

_SQL_TYPE = {
    "String": "TEXT", "Int64": "BIGINT", "Int32": "INTEGER",
    "Float": "REAL", "Double": "DOUBLE PRECISION", "Decimal": "NUMERIC",
    "Bool": "BOOLEAN", "Date": "DATE", "DateTime": "TIMESTAMP",
}

_YAML_GROUP = {
    "String": "string_type", "Int64": "int64_type", "Int32": "int32_type",
    "Float": "float_type", "Double": "double_type", "Decimal": "decimal_type",
    "Bool": "bool_type", "Date": "date_type", "DateTime": "datetime_type",
}


# ── Relation normalization ───────────────────────────────────────

def _normalize_relation(rel: dict) -> dict | None:
    """Normalize both old and new relation formats into a uniform shape.

    Returns:
        {"source_column": ..., "target_bo": ..., "target_column": ..., "label": ...}
        or None if the relation can't be parsed.
    """
    if "boid" in rel:
        # New format
        fk = rel.get("foreign_key", {})
        local = fk.get("local", {})
        ref = fk.get("Referenced", fk.get("referenced", {}))
        return {
            "source_column": local.get("name", ""),
            "target_bo": rel["boid"],
            "target_column": ref.get("name", ""),
            "label": rel.get("title", rel.get("name", "")),
        }
    elif "targetBo" in rel or "target_bo" in rel:
        # Old format
        return {
            "source_column": rel.get("sourceColumn", rel.get("source_column", "")),
            "target_bo": rel.get("targetBo", rel.get("target_bo", "")),
            "target_column": rel.get("targetColumn", rel.get("target_column", "")),
            "label": rel.get("name", rel.get("label", "")),
        }
    return None


def _iter_relations(bo: dict):
    """Yield normalized relations for a BO."""
    for rel in bo.get("relations", []):
        norm = _normalize_relation(rel)
        if norm and norm["target_bo"]:
            yield norm


# ── Enum resolution ──────────────────────────────────────────────

def _resolve_enum(col: dict, bo_name: str, enums: dict) -> dict | None:
    col_name = col["name"]
    persian = col.get("persianTitle", col.get("persian_title", ""))
    enum_id = col.get("enumId", col.get("enum_id", ""))

    if enum_id and enum_id in enums:
        return enums[enum_id]

    key = f"{bo_name}_{col_name}"
    if key in enums:
        return enums[key]

    for edef in enums.values():
        edef_persian = edef.get("persianTitle", edef.get("persian_title", ""))
        if edef_persian == persian and persian:
            return edef

    frags = set(col_name.lower().split("_"))
    if len(frags) < 2:
        return None
    prefix = f"{bo_name}_".lower()
    for eid, edef in enums.items():
        suffix = eid.lower()
        if suffix.startswith(prefix):
            suffix = suffix[len(prefix):]
        if suffix and all(f in suffix for f in frags):
            return edef
    return None


def _enum_values_persian(enum_def: dict) -> list[str]:
    return [v.get("persianTitle", v.get("persian_title", ""))
            for v in enum_def.get("values", [])]


# ── Parse helpers ────────────────────────────────────────────────

def _col_persian(col: dict) -> str:
    return col.get("persianTitle", col.get("persian_title", ""))

def _bo_persian(bo: dict) -> str:
    return bo.get("persianTitle", bo.get("persian_title", ""))

def _iter_bos(raw: dict):
    enums = raw.get("enums", {})
    for bo in raw.get("boNames", []):
        yield bo["name"], bo, enums


# =====================================================================
# Format: create_table  (CR_P)
# =====================================================================

def _to_create_table(raw: dict) -> str:
    parts = []
    for bo_name, bo, enums in _iter_bos(raw):
        lines = [f"-- {_bo_persian(bo)} ({bo.get('title', '')})"]
        lines.append(f"CREATE TABLE {bo_name} (")

        col_defs = []
        for col in bo.get("columns", []):
            sql_type = _SQL_TYPE.get(col.get("type", "String"), "TEXT")
            comment = f"  -- {_col_persian(col)}"
            enum_def = _resolve_enum(col, bo_name, enums)
            check = ""
            if enum_def:
                vals = ", ".join(f"'{v}'" for v in _enum_values_persian(enum_def))
                check = f" CHECK ({col['name']} IN ({vals}))"
            col_defs.append(f"    {col['name']} {sql_type}{check}{comment}")

        for norm in _iter_relations(bo):
            col_defs.append(
                f"    FOREIGN KEY ({norm['source_column']}) "
                f"REFERENCES {norm['target_bo']}({norm['target_column']})"
            )

        lines.append(",\n".join(col_defs))
        lines.append(");")
        parts.append("\n".join(lines))
    return "\n\n".join(parts)


# =====================================================================
# Format: openai_demo  (OD_P)
# =====================================================================

def _to_openai_demo(raw: dict) -> str:
    lines = [
        "### Complete SQL query only and with no explanation",
        "### PostgreSQL SQL tables, with their properties:",
        "#",
    ]
    for bo_name, bo, enums in _iter_bos(raw):
        cols = ", ".join(c["name"] for c in bo.get("columns", []))
        lines.append(f"# {bo_name} ({cols})")
        for norm in _iter_relations(bo):
            lines.append(
                f"#   FK: {bo_name}.{norm['source_column']} → "
                f"{norm['target_bo']}({norm['target_column']})"
            )
    lines.append("#")
    return "\n".join(lines)


# =====================================================================
# Format: basic  (BS_P)
# =====================================================================

def _to_basic(raw: dict) -> str:
    lines = []
    fk_notes = []
    for bo_name, bo, enums in _iter_bos(raw):
        cols = ", ".join(c["name"] for c in bo.get("columns", []))
        lines.append(f"Table {bo_name}, columns = [{cols}]")
        for norm in _iter_relations(bo):
            fk_notes.append(
                f"FK: {bo_name}.{norm['source_column']} = "
                f"{norm['target_bo']}.{norm['target_column']}"
            )
    if fk_notes:
        lines.append("")
        lines.extend(fk_notes)
    return "\n".join(lines)


# =====================================================================
# Format: text_repr  (TR_P)
# =====================================================================

def _to_text_repr(raw: dict) -> str:
    lines = ["Given the following database schema:", ""]
    for bo_name, bo, enums in _iter_bos(raw):
        lines.append(f"{bo_name} ({_bo_persian(bo)}):")
        col_parts = [f"{c['name']} ({_col_persian(c)})" for c in bo.get("columns", [])]
        lines.append("  " + ", ".join(col_parts))

        enum_notes = []
        for col in bo.get("columns", []):
            edef = _resolve_enum(col, bo_name, enums)
            if edef:
                vals = ", ".join(f'"{v}"' for v in _enum_values_persian(edef))
                enum_notes.append(f"    {col['name']}: [{vals}]")
        if enum_notes:
            lines.append("")
            lines.append("  Allowed values for enum columns:")
            lines.extend(enum_notes)

        rel_notes = list(_iter_relations(bo))
        if rel_notes:
            lines.append("")
            lines.append("  References:")
            for norm in rel_notes:
                lines.append(f"    {norm['source_column']} → {norm['target_bo']}.{norm['target_column']}")
        lines.append("")
    return "\n".join(lines)


# =====================================================================
# Format: simple_ddl_md  (SimpleDDL-MD-Chat)
# =====================================================================

def _to_simple_ddl_md(raw: dict) -> str:
    lines = ["### Database Schema", ""]
    for bo_name, bo, enums in _iter_bos(raw):
        lines.append("```sql")
        lines.append(f"-- Table: {bo_name}  ({_bo_persian(bo)})")
        lines.append(f"CREATE TABLE {bo_name} (")

        col_lines = []
        for col in bo.get("columns", []):
            sql_t = _SQL_TYPE.get(col.get("type", "String"), "TEXT")
            col_lines.append(f"  {col['name']} {sql_t}  -- {_col_persian(col)}")
        for norm in _iter_relations(bo):
            col_lines.append(
                f"  FOREIGN KEY ({norm['source_column']}) "
                f"REFERENCES {norm['target_bo']}({norm['target_column']})"
            )
        lines.append(",\n".join(col_lines))
        lines.append(");")
        lines.append("```")

        enum_notes = []
        for col in bo.get("columns", []):
            edef = _resolve_enum(col, bo_name, enums)
            if edef:
                vals = " | ".join(f"`{v}`" for v in _enum_values_persian(edef))
                enum_notes.append(f"- `{col['name']}`: {vals}")
        if enum_notes:
            lines.append("")
            lines.extend(enum_notes)
        lines.append("")
    return "\n".join(lines)


# =====================================================================
# Format: yaml_grouped
# =====================================================================

def _to_yaml_grouped(raw: dict) -> str:
    lines = []
    for bo_name, bo, enums in _iter_bos(raw):
        lines.append(f"{bo_name}:")
        lines.append(f'  title: "{_bo_persian(bo)}"')
        context = bo_name.split("_")[0] if "_" in bo_name else bo_name
        lines.append(f'  context: "{context}"')
        lines.append("  parameters: {}")
        lines.append("  attributes:")

        groups: dict[str, list] = {}
        enum_cols = []
        for col in bo.get("columns", []):
            edef = _resolve_enum(col, bo_name, enums)
            if edef:
                enum_cols.append((col, edef))
            else:
                gk = _YAML_GROUP.get(col.get("type", "String"), "string_type")
                groups.setdefault(gk, []).append(col)

        for gk in sorted(groups):
            lines.append(f"    {gk}:")
            for col in groups[gk]:
                lines.append(f'      {col["name"]}: "{_col_persian(col)}"')

        if enum_cols:
            lines.append("    enum_type:")
            for col, edef in enum_cols:
                lines.append(f"      {col['name']}:")
                lines.append(f'        title: "{_col_persian(col)}"')
                lines.append("        allowed_values:")
                for v in _enum_values_persian(edef):
                    lines.append(f'          - "{v}"')

        rels = list(_iter_relations(bo))
        if rels:
            lines.append("  relations:")
            for norm in rels:
                lines.append(f"    - source: {norm['source_column']}")
                lines.append(f"      target_bo: {norm['target_bo']}")
                lines.append(f"      target_column: {norm['target_column']}")
        else:
            lines.append("  relations: []")

    return "\n".join(lines)


# =====================================================================
# Public API
# =====================================================================

_FORMATTERS = {
    "create_table": _to_create_table,
    "openai_demo": _to_openai_demo,
    "basic": _to_basic,
    "text_repr": _to_text_repr,
    "simple_ddl_md": _to_simple_ddl_md,
    "yaml_grouped": _to_yaml_grouped,
}

SUPPORTED_FORMATS = list(_FORMATTERS.keys())


def format_bo(raw_bo: dict, fmt: str = "create_table") -> str:
    """Convert a raw BO JSON dict to a prompt-ready schema string."""
    if fmt not in _FORMATTERS:
        raise ValueError(f"Unknown format '{fmt}'. Choose from: {SUPPORTED_FORMATS}")
    return _FORMATTERS[fmt](raw_bo)
