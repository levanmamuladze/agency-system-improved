"""
CRM Database Module

SQLite-based CRM for tracking leads through the sales pipeline.

Tables:
- leads: Business information and contact details
- analysis: Website analysis results
- outreach: Track all outreach attempts
- notes: Free-form notes on leads
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from pathlib import Path

import sys
sys.path.append(str(Path(__file__).parent.parent))

from config import DATABASE_PATH, LEAD_STATUSES


class LeadDatabase:
    """
    SQLite CRM for lead management.
    
    Usage:
        db = LeadDatabase()
        db.initialize()
        
        # Add a lead
        lead_id = db.add_lead(
            name="Joe's Barbershop",
            website="joesbarbershop.com",
            email="joe@email.com",
            phone="+1234567890",
            niche="barbershop",
            city="Chicago"
        )
        
        # Update status
        db.update_status(lead_id, "contacted")
        
        # Get all leads
        leads = db.get_all_leads()
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DATABASE_PATH
        
        # Ensure data directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self.conn = None
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def initialize(self):
        """Create database tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Leads table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                website TEXT,
                email TEXT,
                phone TEXT,
                city TEXT,
                state TEXT,
                niche TEXT,
                source TEXT DEFAULT 'manual',
                status TEXT DEFAULT 'found',
                score INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Analysis results table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER NOT NULL,
                score INTEGER,
                lead_quality TEXT,
                issues TEXT,
                load_time REAL,
                has_ssl INTEGER,
                is_mobile_friendly INTEGER,
                has_title INTEGER,
                has_meta_description INTEGER,
                has_h1 INTEGER,
                has_cta INTEGER,
                has_contact_info INTEGER,
                is_reachable INTEGER,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lead_id) REFERENCES leads(id)
            )
        """)
        
        # Outreach tracking table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS outreach (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                subject TEXT,
                body TEXT,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                response_received INTEGER DEFAULT 0,
                response_text TEXT,
                response_at TIMESTAMP,
                FOREIGN KEY (lead_id) REFERENCES leads(id)
            )
        """)
        
        # Notes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lead_id INTEGER NOT NULL,
                note TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (lead_id) REFERENCES leads(id)
            )
        """)
        
        # Create indexes for common queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_niche ON leads(niche)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_leads_city ON leads(city)")
        
        conn.commit()
        print(f"Database initialized: {self.db_path}")
    
    # =========================================================================
    # LEAD OPERATIONS
    # =========================================================================
    
    def add_lead(
        self,
        name: str,
        website: str = None,
        email: str = None,
        phone: str = None,
        city: str = None,
        state: str = None,
        niche: str = None,
        source: str = "manual",
        status: str = "found",
    ) -> int:
        """Add a new lead. Returns the lead ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO leads (name, website, email, phone, city, state, niche, source, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, website, email, phone, city, state, niche, source, status))
        
        conn.commit()
        return cursor.lastrowid
    
    def get_lead(self, lead_id: int) -> Optional[Dict]:
        """Get a single lead by ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM leads WHERE id = ?", (lead_id,))
        row = cursor.fetchone()
        
        if row:
            return dict(row)
        return None
    
    def get_all_leads(
        self,
        status: str = None,
        niche: str = None,
        city: str = None,
        limit: int = None,
    ) -> List[Dict]:
        """Get all leads with optional filters."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM leads WHERE 1=1"
        params = []
        
        if status:
            query += " AND status = ?"
            params.append(status)
        
        if niche:
            query += " AND niche = ?"
            params.append(niche)
        
        if city:
            query += " AND city = ?"
            params.append(city)
        
        query += " ORDER BY updated_at DESC"
        
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def update_lead(self, lead_id: int, **kwargs) -> bool:
        """Update lead fields."""
        if not kwargs:
            return False
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Build UPDATE query
        fields = []
        values = []
        
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        
        fields.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(lead_id)
        
        query = f"UPDATE leads SET {', '.join(fields)} WHERE id = ?"
        
        cursor.execute(query, values)
        conn.commit()
        
        return cursor.rowcount > 0
    
    def update_status(self, lead_id: int, status: str) -> bool:
        """Update lead status."""
        if status not in LEAD_STATUSES:
            print(f"Invalid status: {status}")
            print(f"Valid statuses: {', '.join(LEAD_STATUSES)}")
            return False
        
        return self.update_lead(lead_id, status=status)
    
    def delete_lead(self, lead_id: int) -> bool:
        """Delete a lead and all associated data."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM analysis WHERE lead_id = ?", (lead_id,))
        cursor.execute("DELETE FROM outreach WHERE lead_id = ?", (lead_id,))
        cursor.execute("DELETE FROM notes WHERE lead_id = ?", (lead_id,))
        cursor.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
        
        conn.commit()
        return cursor.rowcount > 0
    
    def search_leads(self, query: str) -> List[Dict]:
        """Search leads by name, website, or email."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        search_query = f"%{query}%"
        cursor.execute("""
            SELECT * FROM leads 
            WHERE name LIKE ? OR website LIKE ? OR email LIKE ?
            ORDER BY updated_at DESC
        """, (search_query, search_query, search_query))
        
        return [dict(row) for row in cursor.fetchall()]
    
    # =========================================================================
    # ANALYSIS OPERATIONS
    # =========================================================================
    
    def save_analysis(self, lead_id: int, analysis_data: Dict) -> int:
        """Save website analysis results."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Convert issues to JSON string
        issues_json = json.dumps(analysis_data.get("issues", []))
        
        cursor.execute("""
            INSERT INTO analysis (
                lead_id, score, lead_quality, issues, load_time,
                has_ssl, is_mobile_friendly, has_title, has_meta_description,
                has_h1, has_cta, has_contact_info, is_reachable
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            lead_id,
            analysis_data.get("score"),
            analysis_data.get("lead_quality"),
            issues_json,
            analysis_data.get("load_time"),
            int(analysis_data.get("has_ssl", False)),
            int(analysis_data.get("is_mobile_friendly", True)),
            int(analysis_data.get("has_title", False)),
            int(analysis_data.get("has_meta_description", False)),
            int(analysis_data.get("has_h1", False)),
            int(analysis_data.get("has_cta", False)),
            int(analysis_data.get("has_contact_info", False)),
            int(analysis_data.get("is_reachable", True)),
        ))
        
        # Also update the lead's score
        self.update_lead(lead_id, score=analysis_data.get("score"), status="analyzed")
        
        conn.commit()
        return cursor.lastrowid
    
    def get_analysis(self, lead_id: int) -> Optional[Dict]:
        """Get the latest analysis for a lead."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM analysis 
            WHERE lead_id = ? 
            ORDER BY analyzed_at DESC 
            LIMIT 1
        """, (lead_id,))
        
        row = cursor.fetchone()
        if row:
            result = dict(row)
            result["issues"] = json.loads(result["issues"])
            return result
        return None
    
    # =========================================================================
    # OUTREACH OPERATIONS
    # =========================================================================
    
    def log_outreach(
        self,
        lead_id: int,
        outreach_type: str,
        subject: str = None,
        body: str = None,
    ) -> int:
        """Log an outreach attempt."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO outreach (lead_id, type, subject, body)
            VALUES (?, ?, ?, ?)
        """, (lead_id, outreach_type, subject, body))
        
        conn.commit()
        return cursor.lastrowid
    
    def log_response(
        self,
        outreach_id: int,
        response_text: str,
    ) -> bool:
        """Log a response to an outreach."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE outreach 
            SET response_received = 1, response_text = ?, response_at = ?
            WHERE id = ?
        """, (response_text, datetime.now().isoformat(), outreach_id))
        
        conn.commit()
        return cursor.rowcount > 0
    
    def get_outreach_history(self, lead_id: int) -> List[Dict]:
        """Get all outreach attempts for a lead."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM outreach 
            WHERE lead_id = ? 
            ORDER BY sent_at DESC
        """, (lead_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_outreach_count(self, lead_id: int) -> int:
        """Get number of outreach attempts for a lead."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM outreach WHERE lead_id = ?",
            (lead_id,)
        )
        
        return cursor.fetchone()[0]
    
    # =========================================================================
    # NOTES OPERATIONS
    # =========================================================================
    
    def add_note(self, lead_id: int, note: str) -> int:
        """Add a note to a lead."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO notes (lead_id, note) VALUES (?, ?)",
            (lead_id, note)
        )
        
        conn.commit()
        return cursor.lastrowid
    
    def get_notes(self, lead_id: int) -> List[Dict]:
        """Get all notes for a lead."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM notes WHERE lead_id = ? ORDER BY created_at DESC",
            (lead_id,)
        )
        
        return [dict(row) for row in cursor.fetchall()]
    
    # =========================================================================
    # STATISTICS
    # =========================================================================
    
    def get_stats(self) -> Dict[str, Any]:
        """Get CRM statistics."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Total leads
        cursor.execute("SELECT COUNT(*) FROM leads")
        stats["total_leads"] = cursor.fetchone()[0]
        
        # Leads by status
        cursor.execute("""
            SELECT status, COUNT(*) as count 
            FROM leads 
            GROUP BY status
        """)
        stats["by_status"] = {row["status"]: row["count"] for row in cursor.fetchall()}
        
        # Leads by niche
        cursor.execute("""
            SELECT niche, COUNT(*) as count 
            FROM leads 
            WHERE niche IS NOT NULL
            GROUP BY niche
            ORDER BY count DESC
        """)
        stats["by_niche"] = {row["niche"]: row["count"] for row in cursor.fetchall()}
        
        # Total outreach
        cursor.execute("SELECT COUNT(*) FROM outreach")
        stats["total_outreach"] = cursor.fetchone()[0]
        
        # Response rate
        cursor.execute("SELECT COUNT(*) FROM outreach WHERE response_received = 1")
        responses = cursor.fetchone()[0]
        stats["response_rate"] = (
            round(responses / stats["total_outreach"] * 100, 1)
            if stats["total_outreach"] > 0 else 0
        )
        
        # Average score
        cursor.execute("SELECT AVG(score) FROM leads WHERE score IS NOT NULL")
        avg = cursor.fetchone()[0]
        stats["avg_score"] = round(avg, 1) if avg else 0
        
        # Leads needing follow-up (contacted but no reply)
        cursor.execute("""
            SELECT COUNT(*) FROM leads 
            WHERE status IN ('contacted', 'followed_up')
        """)
        stats["needs_followup"] = cursor.fetchone()[0]
        
        return stats
    
    # =========================================================================
    # EXPORT
    # =========================================================================
    
    def export_to_csv(self, filepath: str, status: str = None) -> int:
        """Export leads to CSV."""
        import csv
        
        leads = self.get_all_leads(status=status)
        
        if not leads:
            print("No leads to export")
            return 0
        
        fieldnames = list(leads[0].keys())
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(leads)
        
        print(f"Exported {len(leads)} leads to {filepath}")
        return len(leads)
    
    def import_from_csv(self, filepath: str) -> int:
        """Import leads from CSV."""
        import csv
        
        count = 0
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                self.add_lead(
                    name=row.get('name', ''),
                    website=row.get('website'),
                    email=row.get('email'),
                    phone=row.get('phone'),
                    city=row.get('city'),
                    state=row.get('state'),
                    niche=row.get('niche'),
                    source=row.get('source', 'csv_import'),
                )
                count += 1
        
        print(f"Imported {count} leads from {filepath}")
        return count


if __name__ == "__main__":
    # Test the database
    db = LeadDatabase()
    db.initialize()
    
    # Add a test lead
    lead_id = db.add_lead(
        name="Test Business",
        website="testbusiness.com",
        email="test@test.com",
        phone="+1234567890",
        niche="restaurant",
        city="Chicago",
    )
    print(f"Added lead ID: {lead_id}")
    
    # Get stats
    stats = db.get_stats()
    print(f"Stats: {stats}")
    
    db.close()
