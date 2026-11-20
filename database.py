"""
Database module for AI Test Case Generator Agent.
Handles SQLite database operations for storing requirements and test cases.
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
from contextlib import contextmanager


DB_PATH = "test_cases.db"


@contextmanager
def get_db_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_database():
    """Initialize the database with required tables."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Create requirements table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS requirements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requirement_text TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create test_cases table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_cases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requirement_id INTEGER NOT NULL,
                test_case_id TEXT NOT NULL,
                scenario_type TEXT NOT NULL,
                title TEXT NOT NULL,
                preconditions TEXT,
                steps TEXT NOT NULL,
                test_data TEXT,
                expected_result TEXT NOT NULL,
                priority TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (requirement_id) REFERENCES requirements (id) ON DELETE CASCADE
            )
        """)

        conn.commit()


def save_requirement(requirement_text: str) -> int:
    """Save a requirement and return its ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO requirements (requirement_text) VALUES (?)",
            (requirement_text,)
        )
        conn.commit()
        return cursor.lastrowid


def update_requirement(requirement_id: int, requirement_text: str) -> bool:
    """Update requirement text for an existing history item."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE requirements SET requirement_text = ? WHERE id = ?",
            (requirement_text, requirement_id),
        )
        conn.commit()
        return cursor.rowcount > 0


def delete_test_cases_for_requirement(requirement_id: int) -> bool:
    """Delete all test cases associated with a requirement."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM test_cases WHERE requirement_id = ?",
            (requirement_id,),
        )
        conn.commit()
        return cursor.rowcount >= 0


def save_test_cases(requirement_id: int, test_cases: List[Dict[str, Any]]) -> List[int]:
    """Save multiple test cases for a requirement. Returns list of test case IDs."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        test_case_ids = []

        for tc in test_cases:
            cursor.execute("""
                INSERT INTO test_cases
                (requirement_id, test_case_id, scenario_type, title, preconditions,
                 steps, test_data, expected_result, priority)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                requirement_id,
                tc.get('test_case_id', ''),
                tc.get('scenario_type', ''),
                tc.get('title', ''),
                tc.get('preconditions', ''),
                tc.get('steps', ''),
                tc.get('test_data', ''),
                tc.get('expected_result', ''),
                tc.get('priority', 'Medium')
            ))
            test_case_ids.append(cursor.lastrowid)

        conn.commit()
        return test_case_ids


def get_all_requirements() -> List[Dict[str, Any]]:
    """Get all requirements with their test case counts."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.id, r.requirement_text, r.created_at,
                   COUNT(tc.id) as test_case_count
            FROM requirements r
            LEFT JOIN test_cases tc ON r.id = tc.requirement_id
            GROUP BY r.id
            ORDER BY r.created_at DESC
        """)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]


def get_requirement_with_test_cases(requirement_id: int) -> Optional[Dict[str, Any]]:
    """Get a requirement and all its test cases."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Get requirement
        cursor.execute("SELECT * FROM requirements WHERE id = ?", (requirement_id,))
        req_row = cursor.fetchone()
        if not req_row:
            return None

        requirement = dict(req_row)

        # Get test cases
        cursor.execute("""
            SELECT * FROM test_cases
            WHERE requirement_id = ?
            ORDER BY id
        """, (requirement_id,))
        tc_rows = cursor.fetchall()

        requirement['test_cases'] = [dict(row) for row in tc_rows]
        return requirement


def update_test_case(test_case_id: int, updates: Dict[str, Any]) -> bool:
    """Update a test case. Returns True if successful."""
    with get_db_connection() as conn:
        cursor = conn.cursor()

        # Build dynamic update query
        allowed_fields = ['test_case_id', 'scenario_type', 'title', 'preconditions',
                         'steps', 'test_data', 'expected_result', 'priority']
        set_clauses = []
        values = []

        for field, value in updates.items():
            if field in allowed_fields:
                set_clauses.append(f"{field} = ?")
                values.append(value)

        if not set_clauses:
            return False

        set_clauses.append("updated_at = CURRENT_TIMESTAMP")
        values.append(test_case_id)

        query = f"UPDATE test_cases SET {', '.join(set_clauses)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()

        return cursor.rowcount > 0


def delete_test_case(test_case_id: int) -> bool:
    """Delete a test case. Returns True if successful."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM test_cases WHERE id = ?", (test_case_id,))
        conn.commit()
        return cursor.rowcount > 0


def delete_requirement(requirement_id: int) -> bool:
    """Delete a requirement and all its test cases. Returns True if successful."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM test_cases WHERE requirement_id = ?", (requirement_id,))
        cursor.execute("DELETE FROM requirements WHERE id = ?", (requirement_id,))
        conn.commit()
        return cursor.rowcount > 0


# Initialize database on import
init_database()