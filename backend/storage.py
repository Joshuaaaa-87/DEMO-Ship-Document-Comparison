from __future__ import annotations

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Iterator


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = Path(os.getenv("PLIMSOLL_DATA_DIR", ROOT_DIR / ".plimsoll")).resolve()
DB_PATH = DATA_DIR / "plimsoll.sqlite3"


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def json_dump(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def json_load(value: str | None, default: Any) -> Any:
    if not value:
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return default


class Store:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path
        self.data_dir = db_path.parent
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "sessions").mkdir(exist_ok=True)

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        connection = sqlite3.connect(self.db_path, timeout=30)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def initialize(self) -> None:
        statements = [
            """
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                status TEXT NOT NULL,
                old_name TEXT NOT NULL,
                new_name TEXT NOT NULL,
                old_version TEXT,
                new_version TEXT,
                old_sha256 TEXT NOT NULL,
                new_sha256 TEXT NOT NULL,
                old_path TEXT NOT NULL,
                new_path TEXT NOT NULL,
                total_differences INTEGER NOT NULL DEFAULT 0,
                high_count INTEGER NOT NULL DEFAULT 0,
                medium_count INTEGER NOT NULL DEFAULT 0,
                low_count INTEGER NOT NULL DEFAULT 0,
                coverage_issues INTEGER NOT NULL DEFAULT 0,
                llm_model TEXT,
                error_message TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                side TEXT NOT NULL CHECK(side IN ('old', 'new')),
                page_number INTEGER NOT NULL,
                print_label TEXT,
                width REAL NOT NULL,
                height REAL NOT NULL,
                extraction_method TEXT NOT NULL,
                confidence REAL NOT NULL,
                page_hash TEXT NOT NULL,
                text TEXT NOT NULL,
                blocks_json TEXT NOT NULL,
                UNIQUE(session_id, side, page_number)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS coverage_issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                side TEXT NOT NULL CHECK(side IN ('old', 'new')),
                page_number INTEGER NOT NULL,
                issue_type TEXT NOT NULL,
                message TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'open',
                resolved_by TEXT,
                resolved_at TEXT,
                resolution_note TEXT
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS differences (
                id TEXT NOT NULL,
                session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                kind TEXT NOT NULL,
                priority TEXT NOT NULL,
                confidence TEXT NOT NULL,
                title TEXT NOT NULL,
                old_page INTEGER,
                new_page INTEGER,
                old_text TEXT,
                new_text TEXT,
                old_bbox_json TEXT,
                new_bbox_json TEXT,
                triggers_json TEXT NOT NULL,
                system_explanation TEXT,
                llm_explanation TEXT,
                recommended_action TEXT,
                must_review INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY(session_id, id)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS review_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_id TEXT NOT NULL UNIQUE,
                session_id TEXT NOT NULL,
                difference_id TEXT NOT NULL,
                verdict TEXT NOT NULL,
                disposition TEXT NOT NULL,
                final_priority TEXT NOT NULL,
                reviewer TEXT NOT NULL,
                note TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY(session_id, difference_id)
                    REFERENCES differences(session_id, id) ON DELETE CASCADE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS export_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                export_id TEXT NOT NULL UNIQUE,
                session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                format TEXT NOT NULL,
                report_state TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """,
            "CREATE INDEX IF NOT EXISTS idx_pages_session_side ON pages(session_id, side, page_number)",
            "CREATE INDEX IF NOT EXISTS idx_differences_session_priority ON differences(session_id, priority)",
            "CREATE INDEX IF NOT EXISTS idx_review_events_difference ON review_events(session_id, difference_id, id)",
            "CREATE INDEX IF NOT EXISTS idx_sessions_updated ON sessions(updated_at DESC)",
        ]
        with self.connect() as connection:
            for statement in statements:
                connection.execute(statement)
            existing_columns = {
                row["name"] for row in connection.execute("PRAGMA table_info(coverage_issues)")
            }
            for column, data_type in (
                ("resolved_by", "TEXT"),
                ("resolved_at", "TEXT"),
                ("resolution_note", "TEXT"),
            ):
                if column not in existing_columns:
                    connection.execute(
                        f"ALTER TABLE coverage_issues ADD COLUMN {column} {data_type}"
                    )
            connection.execute("PRAGMA optimize")

    def new_session_id(self) -> str:
        return uuid.uuid4().hex[:12]

    def session_dir(self, session_id: str) -> Path:
        path = self.data_dir / "sessions" / session_id
        path.mkdir(parents=True, exist_ok=True)
        return path

    def create_session(self, data: dict[str, Any]) -> None:
        now = utc_now()
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO sessions (
                    id, created_at, updated_at, status,
                    old_name, new_name, old_version, new_version,
                    old_sha256, new_sha256, old_path, new_path
                ) VALUES (?, ?, ?, 'processing', ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    data["id"], now, now,
                    data["old_name"], data["new_name"],
                    data.get("old_version"), data.get("new_version"),
                    data["old_sha256"], data["new_sha256"],
                    data["old_path"], data["new_path"],
                ),
            )

    def replace_analysis(
        self,
        session_id: str,
        pages: list[dict[str, Any]],
        issues: list[dict[str, Any]],
        differences: list[dict[str, Any]],
        llm_model: str | None,
    ) -> None:
        counts = {"high": 0, "medium": 0, "low": 0}
        for difference in differences:
            counts[difference["priority"]] = counts.get(difference["priority"], 0) + 1

        with self.connect() as connection:
            connection.execute("DELETE FROM pages WHERE session_id = ?", (session_id,))
            connection.execute("DELETE FROM coverage_issues WHERE session_id = ?", (session_id,))
            connection.execute("DELETE FROM differences WHERE session_id = ?", (session_id,))

            connection.executemany(
                """
                INSERT INTO pages (
                    session_id, side, page_number, print_label, width, height,
                    extraction_method, confidence, page_hash, text, blocks_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        session_id, page["side"], page["page_number"], page.get("print_label"),
                        page["width"], page["height"], page["extraction_method"],
                        page["confidence"], page["page_hash"], page["text"],
                        json_dump(page["blocks"]),
                    )
                    for page in pages
                ],
            )
            connection.executemany(
                """
                INSERT INTO coverage_issues (
                    session_id, side, page_number, issue_type, message, status
                ) VALUES (?, ?, ?, ?, ?, 'open')
                """,
                [
                    (
                        session_id, issue["side"], issue["page_number"],
                        issue["issue_type"], issue["message"],
                    )
                    for issue in issues
                ],
            )
            connection.executemany(
                """
                INSERT INTO differences (
                    id, session_id, kind, priority, confidence, title,
                    old_page, new_page, old_text, new_text,
                    old_bbox_json, new_bbox_json, triggers_json,
                    system_explanation, llm_explanation, recommended_action, must_review
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        diff["id"], session_id, diff["kind"], diff["priority"],
                        diff["confidence"], diff["title"], diff.get("old_page"),
                        diff.get("new_page"), diff.get("old_text"), diff.get("new_text"),
                        json_dump(diff.get("old_bbox")) if diff.get("old_bbox") else None,
                        json_dump(diff.get("new_bbox")) if diff.get("new_bbox") else None,
                        json_dump(diff.get("triggers", [])), diff.get("system_explanation"),
                        diff.get("llm_explanation"), diff.get("recommended_action"),
                        1 if diff.get("must_review") else 0,
                    )
                    for diff in differences
                ],
            )
            connection.execute(
                """
                UPDATE sessions
                SET status = 'ready', updated_at = ?, total_differences = ?,
                    high_count = ?, medium_count = ?, low_count = ?,
                    coverage_issues = ?, llm_model = ?, error_message = NULL
                WHERE id = ?
                """,
                (
                    utc_now(), len(differences), counts.get("high", 0),
                    counts.get("medium", 0), counts.get("low", 0),
                    len(issues), llm_model, session_id,
                ),
            )

    def mark_failed(self, session_id: str, message: str) -> None:
        with self.connect() as connection:
            connection.execute(
                "UPDATE sessions SET status = 'failed', updated_at = ?, error_message = ? WHERE id = ?",
                (utc_now(), message[:1000], session_id),
            )

    def append_review(
        self,
        session_id: str,
        difference_id: str,
        verdict: str,
        disposition: str,
        final_priority: str,
        reviewer: str,
        note: str,
    ) -> dict[str, Any]:
        event_id = f"rev_{uuid.uuid4().hex[:16]}"
        created_at = utc_now()
        with self.connect() as connection:
            exists = connection.execute(
                "SELECT 1 FROM differences WHERE session_id = ? AND id = ?",
                (session_id, difference_id),
            ).fetchone()
            if not exists:
                raise KeyError(difference_id)
            connection.execute(
                """
                INSERT INTO review_events (
                    event_id, session_id, difference_id, verdict, disposition,
                    final_priority, reviewer, note, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_id, session_id, difference_id, verdict, disposition,
                    final_priority, reviewer.strip(), note.strip(), created_at,
                ),
            )
            connection.execute(
                "UPDATE sessions SET updated_at = ? WHERE id = ?",
                (created_at, session_id),
            )
        return {
            "event_id": event_id,
            "difference_id": difference_id,
            "verdict": verdict,
            "disposition": disposition,
            "final_priority": final_priority,
            "reviewer": reviewer.strip(),
            "note": note.strip(),
            "created_at": created_at,
        }

    def acknowledge_coverage(
        self,
        session_id: str,
        issue_id: int,
        reviewer: str,
        note: str,
    ) -> dict[str, Any]:
        resolved_at = utc_now()
        with self.connect() as connection:
            issue = connection.execute(
                "SELECT * FROM coverage_issues WHERE session_id = ? AND id = ?",
                (session_id, issue_id),
            ).fetchone()
            if not issue:
                raise KeyError(issue_id)
            connection.execute(
                """
                UPDATE coverage_issues
                SET status = 'acknowledged', resolved_by = ?, resolved_at = ?, resolution_note = ?
                WHERE session_id = ? AND id = ?
                """,
                (reviewer.strip(), resolved_at, note.strip(), session_id, issue_id),
            )
            connection.execute(
                "UPDATE sessions SET updated_at = ? WHERE id = ?",
                (resolved_at, session_id),
            )
        return {
            "issue_id": issue_id,
            "status": "acknowledged",
            "resolved_by": reviewer.strip(),
            "resolved_at": resolved_at,
            "resolution_note": note.strip(),
        }

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        with self.connect() as connection:
            session_row = connection.execute(
                "SELECT * FROM sessions WHERE id = ?", (session_id,)
            ).fetchone()
            if not session_row:
                return None

            pages = connection.execute(
                "SELECT * FROM pages WHERE session_id = ? ORDER BY side, page_number",
                (session_id,),
            ).fetchall()
            issues = connection.execute(
                "SELECT * FROM coverage_issues WHERE session_id = ? ORDER BY side, page_number",
                (session_id,),
            ).fetchall()
            differences = connection.execute(
                """
                SELECT d.*,
                       r.event_id AS review_event_id,
                       r.verdict, r.disposition, r.final_priority,
                       r.reviewer, r.note, r.created_at AS reviewed_at
                FROM differences d
                LEFT JOIN review_events r ON r.id = (
                    SELECT r2.id FROM review_events r2
                    WHERE r2.session_id = d.session_id AND r2.difference_id = d.id
                    ORDER BY r2.id DESC LIMIT 1
                )
                WHERE d.session_id = ?
                ORDER BY CASE d.priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END, d.id
                """,
                (session_id,),
            ).fetchall()

        session = dict(session_row)
        session["pages"] = []
        for row in pages:
            page = dict(row)
            page["blocks"] = json_load(page.pop("blocks_json"), [])
            session["pages"].append(page)

        session["coverage"] = [dict(row) for row in issues]
        session["differences"] = []
        for row in differences:
            diff = dict(row)
            diff["old_bbox"] = json_load(diff.pop("old_bbox_json"), None)
            diff["new_bbox"] = json_load(diff.pop("new_bbox_json"), None)
            diff["triggers"] = json_load(diff.pop("triggers_json"), [])
            diff["must_review"] = bool(diff["must_review"])
            diff["reviewed"] = bool(diff.get("review_event_id"))
            session["differences"].append(diff)

        reviewed = sum(1 for diff in session["differences"] if diff["reviewed"])
        must_review_open = sum(
            1 for diff in session["differences"] if diff["must_review"] and not diff["reviewed"]
        ) + sum(1 for issue in session["coverage"] if issue["status"] == "open")
        session["reviewed_count"] = reviewed
        session["must_review_open"] = must_review_open
        session["report_state"] = "official" if must_review_open == 0 else "draft"
        return session

    def list_sessions(self, limit: int = 30) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT id, created_at, updated_at, status, old_name, new_name,
                       old_version, new_version, total_differences,
                       high_count, medium_count, low_count, coverage_issues
                FROM sessions ORDER BY updated_at DESC LIMIT ?
                """,
                (max(1, min(limit, 100)),),
            ).fetchall()
        return [dict(row) for row in rows]

    def register_export(self, session_id: str, format_name: str, report_state: str) -> str:
        export_id = f"exp_{uuid.uuid4().hex[:16]}"
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO export_events (export_id, session_id, format, report_state, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (export_id, session_id, format_name, report_state, utc_now()),
            )
        return export_id


store = Store()
