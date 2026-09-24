"""
src/xlsx_io.py
Минимальный модуль для чтения/записи .xlsx без внешних библиотек.
Использует только zipfile и xml.etree.ElementTree (встроены в Python).
"""

import os
import zipfile
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS_CT = "http://schemas.openxmlformats.org/package/2006/content-types"


def _col_letter(idx: int) -> str:
    """1 -> A, 27 -> AA"""
    result = ""
    while idx > 0:
        idx, rem = divmod(idx - 1, 26)
        result = chr(65 + rem) + result
    return result


def _ref_to_col(ref: str) -> int:
    """A1 -> 1, B2 -> 2, AA5 -> 27"""
    letters = ""
    for ch in ref:
        if ch.isalpha():
            letters += ch
        else:
            break
    result = 0
    for ch in letters:
        result = result * 26 + (ord(ch) - 64)
    return result


def write_xlsx(filepath: str, sheets: dict) -> None:
    """
    Записывает Excel-файл.
    sheets: {имя_листа: [[row1], [row2], ...]}
    """
    os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
    names = list(sheets.keys())

    # [Content_Types].xml
    ct = [
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
        f'<Types xmlns="{NS_CT}">',
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
        '<Default Extension="xml" ContentType="application/xml"/>',
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
    ]
    for i in range(1, len(names) + 1):
        ct.append(
            f'<Override PartName="/xl/worksheets/sheet{i}.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        )
    ct.append('</Types>')

    rels = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<Relationships xmlns="{NS_PKG_REL}">'
        f'<Relationship Id="rId1" Type="{NS_REL}/officeDocument" Target="xl/workbook.xml"/>'
        '</Relationships>'
    )

    wb = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
          f'<workbook xmlns="{NS_MAIN}" xmlns:r="{NS_REL}"><sheets>']
    for i, name in enumerate(names, 1):
        wb.append(f'<sheet name="{escape(name)}" sheetId="{i}" r:id="rId{i}"/>')
    wb.append('</sheets></workbook>')

    wb_rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
               f'<Relationships xmlns="{NS_PKG_REL}">']
    for i in range(1, len(names) + 1):
        wb_rels.append(f'<Relationship Id="rId{i}" Type="{NS_REL}/worksheet" Target="worksheets/sheet{i}.xml"/>')
    wb_rels.append('</Relationships>')

    sheets_xml = {}
    for i, name in enumerate(names, 1):
        rows = sheets[name]
        parts = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                 f'<worksheet xmlns="{NS_MAIN}"><sheetData>']
        for r_idx, row in enumerate(rows, 1):
            parts.append(f'<row r="{r_idx}">')
            for c_idx, value in enumerate(row, 1):
                if value is None:
                    continue
                ref = f"{_col_letter(c_idx)}{r_idx}"
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    parts.append(f'<c r="{ref}"><v>{value}</v></c>')
                else:
                    text = escape(str(value))
                    parts.append(f'<c r="{ref}" t="inlineStr"><is><t>{text}</t></is></c>')
            parts.append('</row>')
        parts.append('</sheetData></worksheet>')
        sheets_xml[f"xl/worksheets/sheet{i}.xml"] = "".join(parts)

    with zipfile.ZipFile(filepath, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", "".join(ct))
        z.writestr("_rels/.rels", rels)
        z.writestr("xl/workbook.xml", "".join(wb))
        z.writestr("xl/_rels/workbook.xml.rels", "".join(wb_rels))
        for path, content in sheets_xml.items():
            z.writestr(path, content)


def _parse_sheet(sheet_xml: bytes) -> list:
    root = ET.fromstring(sheet_xml)
    rows = []
    for row_elem in root.iter(f'{{{NS_MAIN}}}row'):
        row_data = {}
        max_col = 0
        for c in row_elem.iter(f'{{{NS_MAIN}}}c'):
            ref = c.get('r') or ''
            col_idx = _ref_to_col(ref)
            max_col = max(max_col, col_idx)
            v_elem = c.find(f'{{{NS_MAIN}}}v')
            is_elem = c.find(f'{{{NS_MAIN}}}is')
            t_elem = is_elem.find(f'{{{NS_MAIN}}}t') if is_elem is not None else None
            value = None
            if t_elem is not None:
                value = t_elem.text
            elif v_elem is not None:
                text = v_elem.text or ""
                try:
                    if '.' in text or 'e' in text.lower():
                        value = float(text)
                    else:
                        value = int(text)
                except (ValueError, TypeError):
                    value = text
            row_data[col_idx] = value
        if max_col == 0:
            rows.append([])
        else:
            rows.append([row_data.get(i) for i in range(1, max_col + 1)])
    return rows


def read_xlsx(filepath: str) -> dict:
    """Возвращает {имя_листа: [[row1], [row2], ...]}."""
    if not os.path.exists(filepath):
        return {}
    with zipfile.ZipFile(filepath, "r") as z:
        wb_root = ET.fromstring(z.read("xl/workbook.xml"))
        rels_root = ET.fromstring(z.read("xl/_rels/workbook.xml.rels"))
        rid_to_target = {r.get("Id"): r.get("Target") for r in rels_root}
        result = {}
        for sheet in wb_root.iter(f'{{{NS_MAIN}}}sheet'):
            name = sheet.get("name")
            rid = sheet.get(f'{{{NS_REL}}}id')
            target = rid_to_target.get(rid)
            if not target:
                continue
            path = "xl/" + target.lstrip("/")
            if path not in z.namelist():
                continue
            result[name] = _parse_sheet(z.read(path))
        return result