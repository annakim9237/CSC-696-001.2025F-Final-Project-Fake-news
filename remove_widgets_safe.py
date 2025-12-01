#!/usr/bin/env python3
import json
import shutil
from pathlib import Path
import nbformat

root = Path('.')
notebooks = list(root.rglob('*.ipynb'))

def clean(path: Path):
    try:
        text = path.read_text(encoding='utf-8')
        data = json.loads(text)
    except Exception as e:
        print(f"ERROR parsing {path}: {e}")
        return False

    changed = False

    # top-level metadata
    meta = data.get('metadata')
    if isinstance(meta, dict) and 'widgets' in meta:
        del meta['widgets']
        data['metadata'] = meta
        changed = True

    # per-cell metadata
    cells = data.get('cells', [])
    for cell in cells:
        cm = cell.get('metadata', {})
        if isinstance(cm, dict) and 'widgets' in cm:
            del cm['widgets']
            cell['metadata'] = cm
            changed = True

    if changed:
        bak = path.with_suffix(path.suffix + '.bak')
        shutil.copy2(path, bak)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding='utf-8')
        print(f"CLEANED {path} -> backup {bak.name}")
        return True
    else:
        print(f"OK {path} (no widgets)")
        return False

any_changed = False
for nb in notebooks:
    res = clean(nb)
    any_changed = any_changed or res

print('\nDone. Any changed:', any_changed)
