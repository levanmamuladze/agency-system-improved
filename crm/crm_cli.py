"""
CRM Command Line Interface

Provides user-friendly commands for managing leads.
"""

from typing import Optional
from datetime import datetime

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from .database import LeadDatabase
from config import LEAD_STATUSES, NICHES


class CRMCommands:
    """
    Command-line interface for CRM operations.
    
    Used by run.py to provide CLI commands.
    """
    
    def __init__(self):
        self.db = LeadDatabase()
    
    def initialize(self):
        """Initialize the database."""
        self.db.initialize()
        print("✓ CRM database initialized")
    
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
    ) -> int:
        """Add a new lead."""
        lead_id = self.db.add_lead(
            name=name,
            website=website,
            email=email,
            phone=phone,
            city=city,
            state=state,
            niche=niche,
            source=source,
        )
        
        print(f"✓ Added lead #{lead_id}: {name}")
        return lead_id
    
    def list_leads(
        self,
        status: str = None,
        niche: str = None,
        city: str = None,
        limit: int = 50,
    ):
        """List leads with optional filters."""
        leads = self.db.get_all_leads(
            status=status,
            niche=niche,
            city=city,
            limit=limit,
        )
        
        if not leads:
            print("No leads found")
            return
        
        # Print table header
        print("\n" + "=" * 100)
        print(f"{'ID':<6} {'Name':<25} {'Status':<12} {'Score':<8} {'Niche':<12} {'City':<15}")
        print("=" * 100)
        
        for lead in leads:
            score = lead.get('score') or '-'
            niche = lead.get('niche') or '-'
            city = lead.get('city') or '-'
            
            # Truncate long names
            name = lead['name'][:23] + '..' if len(lead['name']) > 25 else lead['name']
            
            print(f"{lead['id']:<6} {name:<25} {lead['status']:<12} {str(score):<8} {niche:<12} {city:<15}")
        
        print("=" * 100)
        print(f"Total: {len(leads)} leads")
    
    def show_lead(self, lead_id: int):
        """Show detailed information about a lead."""
        lead = self.db.get_lead(lead_id)
        
        if not lead:
            print(f"Lead #{lead_id} not found")
            return
        
        analysis = self.db.get_analysis(lead_id)
        notes = self.db.get_notes(lead_id)
        outreach = self.db.get_outreach_history(lead_id)
        
        print("\n" + "=" * 60)
        print(f"LEAD #{lead_id}: {lead['name']}")
        print("=" * 60)
        
        print(f"""
Status:   {lead['status']}
Website:  {lead['website'] or 'None'}
Email:    {lead['email'] or 'None'}
Phone:    {lead['phone'] or 'None'}
City:     {lead['city'] or 'None'}
State:    {lead['state'] or 'None'}
Niche:    {lead['niche'] or 'None'}
Source:   {lead['source']}
Score:    {lead['score'] or 'Not analyzed'}
Created:  {lead['created_at']}
Updated:  {lead['updated_at']}
""")
        
        if analysis:
            print("-" * 60)
            print("ANALYSIS:")
            print(f"  Score: {analysis['score']} ({analysis['lead_quality']})")
            print(f"  Load Time: {analysis['load_time']:.2f}s")
            print(f"  SSL: {'✓' if analysis['has_ssl'] else '✗'}")
            print(f"  Mobile: {'✓' if analysis['is_mobile_friendly'] else '✗'}")
            print(f"  Issues: {len(analysis['issues'])}")
            for issue in analysis['issues'][:5]:  # Show first 5
                print(f"    - {issue.get('description', issue)}")
        
        if outreach:
            print("-" * 60)
            print(f"OUTREACH ({len(outreach)} attempts):")
            for o in outreach[:5]:  # Show last 5
                response = "✓ Got reply" if o['response_received'] else ""
                print(f"  {o['sent_at'][:10]} - {o['type']} {response}")
        
        if notes:
            print("-" * 60)
            print(f"NOTES ({len(notes)}):")
            for note in notes[:3]:  # Show last 3
                print(f"  [{note['created_at'][:10]}] {note['note'][:50]}...")
        
        print("=" * 60 + "\n")
    
    def update_status(self, lead_id: int, status: str):
        """Update a lead's status."""
        if status not in LEAD_STATUSES:
            print(f"Invalid status: {status}")
            print(f"Valid statuses: {', '.join(LEAD_STATUSES)}")
            return
        
        if self.db.update_status(lead_id, status):
            print(f"✓ Lead #{lead_id} status updated to: {status}")
        else:
            print(f"Failed to update lead #{lead_id}")
    
    def add_note(self, lead_id: int, note: str):
        """Add a note to a lead."""
        note_id = self.db.add_note(lead_id, note)
        print(f"✓ Added note #{note_id} to lead #{lead_id}")
    
    def log_outreach(
        self,
        lead_id: int,
        outreach_type: str,
        subject: str = None,
        body: str = None,
    ):
        """Log an outreach attempt."""
        outreach_id = self.db.log_outreach(lead_id, outreach_type, subject, body)
        print(f"✓ Logged {outreach_type} outreach #{outreach_id} for lead #{lead_id}")
        
        # Update lead status if needed
        lead = self.db.get_lead(lead_id)
        if lead and lead['status'] == 'analyzed':
            self.db.update_status(lead_id, 'contacted')
        elif lead and lead['status'] == 'contacted':
            self.db.update_status(lead_id, 'followed_up')
    
    def show_stats(self):
        """Show CRM statistics."""
        stats = self.db.get_stats()
        
        print("\n" + "=" * 50)
        print("CRM STATISTICS")
        print("=" * 50)
        
        print(f"""
Total Leads:      {stats['total_leads']}
Total Outreach:   {stats['total_outreach']}
Response Rate:    {stats['response_rate']}%
Average Score:    {stats['avg_score']}
Needs Follow-up:  {stats['needs_followup']}

BY STATUS:
""")
        
        for status, count in sorted(stats['by_status'].items()):
            bar = "█" * min(count, 20)
            print(f"  {status:<15} {count:>4}  {bar}")
        
        if stats['by_niche']:
            print("\nBY NICHE:")
            for niche, count in list(stats['by_niche'].items())[:10]:
                bar = "█" * min(count, 20)
                print(f"  {niche:<15} {count:>4}  {bar}")
        
        print("=" * 50 + "\n")
    
    def search(self, query: str):
        """Search leads by name, website, or email."""
        leads = self.db.search_leads(query)
        
        if not leads:
            print(f"No leads found matching: {query}")
            return
        
        print(f"\nFound {len(leads)} leads matching '{query}':\n")
        
        for lead in leads:
            score = f"Score: {lead['score']}" if lead.get('score') else ""
            print(f"  #{lead['id']} - {lead['name']} ({lead['status']}) {score}")
    
    def export_csv(self, filepath: str, status: str = None):
        """Export leads to CSV."""
        count = self.db.export_to_csv(filepath, status)
        if count:
            print(f"✓ Exported {count} leads to {filepath}")
    
    def import_csv(self, filepath: str):
        """Import leads from CSV."""
        count = self.db.import_from_csv(filepath)
        print(f"✓ Imported {count} leads from {filepath}")
    
    def delete_lead(self, lead_id: int, confirm: bool = False):
        """Delete a lead."""
        lead = self.db.get_lead(lead_id)
        
        if not lead:
            print(f"Lead #{lead_id} not found")
            return
        
        if not confirm:
            print(f"Are you sure you want to delete '{lead['name']}'?")
            print("Run with --confirm to delete")
            return
        
        if self.db.delete_lead(lead_id):
            print(f"✓ Deleted lead #{lead_id}: {lead['name']}")
        else:
            print(f"Failed to delete lead #{lead_id}")
    
    def get_leads_for_outreach(self, limit: int = 20):
        """Get leads ready for outreach."""
        # Get leads that are analyzed but not yet contacted
        analyzed = self.db.get_all_leads(status='analyzed', limit=limit)
        
        # Get leads that need follow-up
        contacted = self.db.get_all_leads(status='contacted', limit=limit)
        
        print("\n" + "=" * 60)
        print("LEADS READY FOR OUTREACH")
        print("=" * 60)
        
        if analyzed:
            print(f"\n📧 NEW LEADS (analyzed, not contacted): {len(analyzed)}")
            for lead in analyzed[:10]:
                score = lead.get('score') or '?'
                print(f"  #{lead['id']} - {lead['name']} (Score: {score})")
        
        if contacted:
            print(f"\n📞 NEEDS FOLLOW-UP (contacted, no reply): {len(contacted)}")
            for lead in contacted[:10]:
                outreach_count = self.db.get_outreach_count(lead['id'])
                print(f"  #{lead['id']} - {lead['name']} ({outreach_count} touches)")
        
        print("=" * 60 + "\n")
    
    def close(self):
        """Close database connection."""
        self.db.close()


if __name__ == "__main__":
    crm = CRMCommands()
    crm.initialize()
    crm.show_stats()
    crm.close()
