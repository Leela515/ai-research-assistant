from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

class PaperRegistry:
    "A JsonL-bcked registry of ingested papers."
    def __init__(self, jsonl_path: str):
        self.path = Path(jsonl_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

        self._arxiv_ids = set()

        self._fh = None

        if self.path.exists():
            self._load_existing()

    def _load_existing(self) -> None:
        """Read existing JSONL records and populate the in-memory arxiv_id set."""
        with self.path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError:
                    continue

                arxiv_id = record.get("arxiv_id")
                if arxiv_id:
                    self._arxiv_ids.add(arxiv_id)
    
    def has_arxiv_id(self, arxiv_id: str) -> bool:
        """
        Check if a paper with this arxiv_id is already registered (ingested).
        """
        return arxiv_id in self._arxiv_ids

    def add(self, record: Dict[str, Any]) -> None:
        """
        Add a new paper record to the registry. The record must contain an 'arxiv_id' field.
        """

        arxiv_id = record.get("arxiv_id")
        if not arxiv_id:
            raise ValueError("Registry record must include 'arxiv_id")

        if arxiv_id in self._arxiv_ids:
            return
        
        if self._fh is None:
            self._fh = self.path.open("a", encoding="utf-8")
        
        self._fh.write(json.dumps(record, ensure_ascii=False) + "\n")
        self._fh.flush()

        self._arxiv_ids.add(arxiv_id)
    
    def iter_records(self) -> Iterable[Dict[str, Any]]:
        """Iterate over all stored records"""

        if not self.path.exists():
            return[]
        
        def _gen():
            with self.path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        continue
        return _gen()
    
    def close(self) -> None:
        """Close the file handle if open"""
        if self._fh is not None:
            self._fh.close()
            self._fh = None