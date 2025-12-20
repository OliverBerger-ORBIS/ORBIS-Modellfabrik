#!/usr/bin/env python3
"""
Script to create Track & Trace fixtures from log files.
Combines FTS state, CCU orders, and module state messages into fixture files.
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any

def load_json_file(file_path: Path) -> List[Dict[str, Any]]:
    """Load JSON array from file."""
    if not file_path.exists():
        print(f"Warning: {file_path} does not exist")
        return []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        if isinstance(data, list):
            return data
        return [data]

def load_jsonl_file(file_path: Path) -> List[Dict[str, Any]]:
    """Load JSONL file (one JSON object per line)."""
    if not file_path.exists():
        print(f"Warning: {file_path} does not exist")
        return []
    
    messages = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                msg = json.loads(line)
                messages.append(msg)
            except json.JSONDecodeError as e:
                print(f"Warning: Failed to parse line in {file_path}: {e}")
    
    return messages

def create_fixture(
    name: str,
    fts_state_file: Path | None = None,
    ccu_order_file: Path | None = None,
    module_state_file: Path | None = None,
    log_file: Path | None = None,
    output_dir: Path = Path('osf/testing/fixtures/orders')
):
    """Create a fixture file by combining messages from multiple sources.
    
    If log_file is provided, it will be used directly (JSONL format).
    Otherwise, individual JSON files will be combined.
    """
    messages: List[Dict[str, Any]] = []
    
    # If log_file is provided, use it directly
    if log_file and log_file.exists():
        log_messages = load_jsonl_file(log_file)
        messages.extend(log_messages)
        print(f"[{name}] Loaded {len(log_messages)} messages from log file")
    else:
        # Load FTS state messages
        if fts_state_file and fts_state_file.exists():
            fts_messages = load_json_file(fts_state_file)
            messages.extend(fts_messages)
            print(f"[{name}] Loaded {len(fts_messages)} FTS state messages")
        
        # Load CCU order messages
        if ccu_order_file and ccu_order_file.exists():
            ccu_messages = load_json_file(ccu_order_file)
            messages.extend(ccu_messages)
            print(f"[{name}] Loaded {len(ccu_messages)} CCU order messages")
        
        # Load module state messages
        if module_state_file and module_state_file.exists():
            module_messages = load_json_file(module_state_file)
            messages.extend(module_messages)
            print(f"[{name}] Loaded {len(module_messages)} module state messages")
    
    # Sort by timestamp
    messages.sort(key=lambda x: x.get('timestamp', ''))
    
    # Count messages with loadId (for validation)
    fts_with_load = sum(
        1 for m in messages
        if m.get('topic', '').startswith('fts/v1/ff/')
        and isinstance(m.get('payload'), str)
        and 'loadId' in m.get('payload', '')
        and '"loadId":null' not in m.get('payload', '')
        and '"loadId": null' not in m.get('payload', '')
    )
    
    print(f"[{name}] Total messages: {len(messages)}")
    print(f"[{name}] FTS messages with loadId: {fts_with_load}")
    print(f"[{name}] Unique topics: {len(set(m.get('topic', '') for m in messages))}")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / name / f"{name}.log"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Write JSONL format (one JSON object per line)
    with open(output_file, 'w', encoding='utf-8') as f:
        for msg in messages:
            # Ensure payload is a string (if it's already a dict, stringify it)
            if isinstance(msg.get('payload'), dict):
                msg['payload'] = json.dumps(msg['payload'])
            f.write(json.dumps(msg, ensure_ascii=False) + '\n')
    
    print(f"[{name}] Created fixture: {output_file}")
    return output_file

def main():
    """Main function to create all Track & Trace fixtures."""
    data_dir = Path('data/omf-data/fts-analysis')
    
    # 1. Production BWR (rename from track-trace)
    print("\n=== Creating production_bwr fixture ===")
    create_fixture(
        name='production_bwr',
        fts_state_file=data_dir / 'production_order_bwr_20251110_182819_fts_state.json',
        ccu_order_file=data_dir / 'production_order_bwr_20251110_182819_ccu_order.json',
        module_state_file=data_dir / 'production_order_bwr_20251110_182819_module_state.json',
    )
    
    # 2. Production White (from sessions directory)
    print("\n=== Creating production_white fixture ===")
    sessions_dir = Path('data/omf-data/sessions')
    white_log_file = sessions_dir / 'production_order_white_20251110_184459.log'
    if white_log_file.exists():
        create_fixture(
            name='production_white',
            log_file=white_log_file,
        )
    else:
        print(f"Production white log file not found: {white_log_file} - skipping")
    
    # 3. Storage Blue
    print("\n=== Creating storage_blue fixture ===")
    storage_blue_files = list(data_dir.glob('storage_order_blue*.json'))
    if storage_blue_files:
        print(f"Found {len(storage_blue_files)} storage blue files")
        create_fixture(
            name='storage_blue',
            fts_state_file=data_dir / 'storage_order_blue_20251110_181104_all_fts_messages.json' if (data_dir / 'storage_order_blue_20251110_181104_all_fts_messages.json').exists() else None,
            ccu_order_file=data_dir / 'storage_order_blue_20251110_181104_ccu_order.json' if (data_dir / 'storage_order_blue_20251110_181104_ccu_order.json').exists() else None,
            module_state_file=data_dir / 'storage_order_blue_20251110_181104_module_state.json' if (data_dir / 'storage_order_blue_20251110_181104_module_state.json').exists() else None,
        )
    else:
        print("No storage blue files found - skipping")
    
    print("\n=== Done ===")

if __name__ == '__main__':
    main()

