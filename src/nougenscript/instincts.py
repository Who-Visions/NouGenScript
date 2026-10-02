"""Bayesian Instinct Engine for NouGenScript.

Assimilates Dav1d's Bayesian-lite learning loop into script validation and narrative feedback:
1. Records behavioral reflexes (user corrections, error resolutions, stylistic preferences).
2. Updates confidence scores on repeated patterns using Bayesian-lite adjustment:
   confidence_new = min(max_confidence, confidence_old + (1.0 - confidence_old) * learning_rate)
3. Persists to local SQLite database (~/.nougen/instincts.db or in-memory / custom path).
4. Provides instant feedback hints for script generation and validation pipelines.
"""
from __future__ import annotations

import os
import sqlite3
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional


DEFAULT_DB_PATH = os.path.expanduser("~/.nougen/instincts.db")


@dataclass
class Instinct:
    id: int
    category: str  # e.g., 'dialogue_pacing', 'anti_cliche', 'formatting', 'character_voice'
    pattern: str
    response: str
    confidence: float = 0.5
    usage_count: int = 1
    last_seen: str = ""


class InstinctRecorder:
    """Manages adaptive instincts for the narrative and script engine."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._conn = None
        if db_path == ":memory:":
            self._conn = sqlite3.connect(":memory:")
        else:
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        conn = self._get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS instincts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT NOT NULL,
                pattern TEXT NOT NULL UNIQUE,
                response TEXT NOT NULL,
                confidence REAL DEFAULT 0.5,
                usage_count INTEGER DEFAULT 1,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        if self._conn is None:
            conn.close()

    def record_instinct(self, category: str, pattern: str, response: str, confidence: float = 0.5, learning_rate: float = 0.1) -> Instinct:
        """Records a new instinct or elevates confidence on pattern recurrence."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT id, confidence, usage_count, response FROM instincts WHERE pattern = ?", (pattern,))
            row = cursor.fetchone()

            if row:
                inst_id, old_conf, count, existing_resp = row
                # Bayesian-lite update: asymptotically converge toward 0.95
                new_conf = min(0.95, old_conf + (1.0 - old_conf) * learning_rate)
                new_count = count + 1
                cursor.execute("""
                    UPDATE instincts SET
                        confidence = ?,
                        usage_count = ?,
                        response = ?,
                        last_seen = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (new_conf, new_count, response or existing_resp, inst_id))
                conn.commit()
                return Instinct(inst_id, category, pattern, response or existing_resp, new_conf, new_count)
            else:
                cursor.execute("""
                    INSERT INTO instincts (category, pattern, response, confidence)
                    VALUES (?, ?, ?, ?)
                """, (category, pattern, response, confidence))
                conn.commit()
                return Instinct(cursor.lastrowid, category, pattern, response, confidence, 1)
        finally:
            if self._conn is None:
                conn.close()

    def get_instincts(self, category: Optional[str] = None, min_confidence: float = 0.4) -> list[Instinct]:
        """Queries instincts meeting or exceeding confidence threshold."""
        conn = self._get_conn()
        try:
            cursor = conn.cursor()
            if category:
                cursor.execute("""
                    SELECT id, category, pattern, response, confidence, usage_count, last_seen
                    FROM instincts
                    WHERE category = ? AND confidence >= ?
                    ORDER BY confidence DESC, usage_count DESC
                """, (category, min_confidence))
            else:
                cursor.execute("""
                    SELECT id, category, pattern, response, confidence, usage_count, last_seen
                    FROM instincts
                    WHERE confidence >= ?
                    ORDER BY confidence DESC, usage_count DESC
                """, (min_confidence,))
            rows = cursor.fetchall()
            return [Instinct(*r) for r in rows]
        finally:
            if self._conn is None:
                conn.close()

    def match_feedback(self, text: str, category: Optional[str] = None, min_confidence: float = 0.4) -> list[Instinct]:
        """Matches applicable instincts against script text or critique."""
        instincts = self.get_instincts(category=category, min_confidence=min_confidence)
        matched = []
        lower_text = text.lower()
        for inst in instincts:
            if inst.pattern.lower() in lower_text:
                matched.append(inst)
        return matched

    def build_constraint_context(self, category: Optional[str] = None, limit: int = 5) -> str:
        """Builds a condensed prompt injection block of high-confidence learned reflexes."""
        active = self.get_instincts(category=category, min_confidence=0.5)[:limit]
        if not active:
            return ""
        lines = ["LEARNED BEHAVIORAL INSTINCTS:"]
        for a in active:
            lines.append(f"- [{a.category.upper()}] When encountering '{a.pattern}' -> {a.response} (conf: {a.confidence:.2f})")
        return "\n".join(lines)
