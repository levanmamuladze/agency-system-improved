#!/usr/bin/env python3
"""
Agency Client Acquisition System - Main CLI

Usage:
    python run.py <command> [options]

Commands:
    find-leads          🔍 SEARCH for businesses automatically
    init                Initialize the CRM database
    add-lead            Add a new lead
    list                List all leads
    show                Show lead details
    analyze             Analyze a website
    analyze-all         Analyze all unanalyzed leads
    generate-message    Generate outreach message
    update-status       Update lead status
    add-note            Add a note to a lead
    log-outreach        Log an outreach attempt
    stats               Show CRM statistics
    outreach            Show leads ready for outreach
    search              Search leads
    export              Export leads to CSV
    import-csv          Import leads from CSV
    dashboard           Show dashboard info
    templates           List outreach templates
    guide               Show lead finding guide
"""

import sys
import argparse
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from crm.database import LeadDatabase
from crm.crm_cli import CRMCommands
from leads.website_analyzer import WebsiteAnalyzer, print_analysis_report
from leads.message_generator import MessageGenerator, generate_all_messages
from leads.lead_finder import print_lead_finding_guide, generate_search_urls
from leads.business_search import BusinessSearcher, quick_search
from outreach.templates import OutreachTemplates
from config import LEAD_STATUSES, NICHES


def cmd_init(args):
    """Initialize the CRM database."""
    crm = CRMCommands()
    crm.initialize()
    crm.close()


def cmd_add_lead(args):
    """Add a new lead."""
    crm = CRMCommands()
    crm.add_lead(
        name=args.name,
        website=args.website,
        email=args.email,
        phone=args.phone,
        city=args.city,
        state=args.state,
        niche=args.niche,
        source=args.source or "manual",
    )
    crm.close()


def cmd_list(args):
    """List leads."""
    crm = CRMCommands()
    crm.list_leads(
        status=args.status,
        niche=args.niche,
        city=args.city,
        limit=args.limit or 50,
    )
    crm.close()


def cmd_show(args):
    """Show lead details."""
    crm = CRMCommands()
    crm.show_lead(args.lead_id)
    crm.close()


def cmd_analyze(args):
    """Analyze a website."""
    analyzer = WebsiteAnalyzer()
    result = analyzer.analyze(args.website)
    print_analysis_report(result)
    
    # Save to database if lead_id provided
    if args.lead_id:
        db = LeadDatabase()
        db.save_analysis(args.lead_id, result.to_dict())
        print(f"✓ Saved analysis to lead #{args.lead_id}")
        db.close()


def cmd_analyze_all(args):
    """Analyze all unanalyzed leads."""
    db = LeadDatabase()
    analyzer = WebsiteAnalyzer()
    
    leads = db.get_all_leads(status="found")
    leads = [l for l in leads if l.get("website")]
    
    if not leads:
        print("No unanalyzed leads with websites found")
        return
    
    print(f"Analyzing {len(leads)} websites...\n")
    
    for lead in leads:
        print(f"Analyzing: {lead['website']}...")
        result = analyzer.analyze(lead["website"])
        db.save_analysis(lead["id"], result.to_dict())
        print(f"  Score: {result.score} ({result.lead_quality})")
    
    print(f"\n✓ Analyzed {len(leads)} websites")
    db.close()


def cmd_generate_message(args):
    """Generate outreach message."""
    db = LeadDatabase()
    lead = db.get_lead(args.lead_id)
    
    if not lead:
        print(f"Lead #{args.lead_id} not found")
        return
    
    analysis = db.get_analysis(args.lead_id)
    issues = []
    
    if analysis:
        issues = [i.get("description", str(i)) for i in analysis.get("issues", [])]
    
    generator = MessageGenerator()
    
    if args.type == "email":
        if lead.get("website"):
            msg = generator.generate_cold_email(
                business_name=lead["name"],
                owner_name=args.owner_name,
                niche=lead.get("niche"),
                issues=issues,
                city=lead.get("city"),
            )
        else:
            msg = generator.generate_cold_email_no_website(
                business_name=lead["name"],
                owner_name=args.owner_name,
                niche=lead.get("niche"),
            )
        
        print(f"\n{'='*60}")
        print(f"Subject: {msg.subject}")
        print(f"{'='*60}")
        print(msg.body)
        print(f"{'='*60}\n")
    
    elif args.type == "phone":
        msg = generator.generate_phone_script(
            business_name=lead["name"],
            owner_name=args.owner_name,
            niche=lead.get("niche"),
            issues=issues,
        )
        print(msg.body)
    
    elif args.type == "sms":
        msg = generator.generate_sms(
            business_name=lead["name"],
            owner_name=args.owner_name,
        )
        print(f"\n{msg.body}\n")
    
    elif args.type == "all":
        messages = generate_all_messages(
            business_name=lead["name"],
            owner_name=args.owner_name,
            niche=lead.get("niche"),
            issues=issues,
            has_website=bool(lead.get("website")),
        )
        
        print(f"\n{'='*60}")
        print("GENERATED MESSAGES")
        print(f"{'='*60}")
        
        for key, msg in messages.items():
            print(f"\n--- {key.upper()} ---")
            if msg.subject:
                print(f"Subject: {msg.subject}")
            print(msg.body)
    
    db.close()


def cmd_update_status(args):
    """Update lead status."""
    crm = CRMCommands()
    crm.update_status(args.lead_id, args.status)
    crm.close()


def cmd_add_note(args):
    """Add a note to a lead."""
    crm = CRMCommands()
    crm.add_note(args.lead_id, args.note)
    crm.close()


def cmd_log_outreach(args):
    """Log an outreach attempt."""
    crm = CRMCommands()
    crm.log_outreach(
        lead_id=args.lead_id,
        outreach_type=args.type,
        subject=args.subject,
    )
    crm.close()


def cmd_stats(args):
    """Show CRM statistics."""
    crm = CRMCommands()
    crm.show_stats()
    crm.close()


def cmd_outreach(args):
    """Show leads ready for outreach."""
    crm = CRMCommands()
    crm.get_leads_for_outreach()
    crm.close()


def cmd_search(args):
    """Search leads."""
    crm = CRMCommands()
    crm.search(args.query)
    crm.close()


def cmd_export(args):
    """Export leads to CSV."""
    crm = CRMCommands()
    crm.export_csv(args.file, args.status)
    crm.close()


def cmd_import_csv(args):
    """Import leads from CSV."""
    crm = CRMCommands()
    crm.import_csv(args.file)
    crm.close()


def cmd_templates(args):
    """List outreach templates."""
    OutreachTemplates.list_templates()


def cmd_guide(args):
    """Show lead finding guide."""
    print_lead_finding_guide()
    
    if args.niche and args.city:
        print(f"\nSearch URLs for '{args.niche}' in '{args.city}':")
        urls = generate_search_urls(args.niche, args.city)
        for platform, url in urls.items():
            print(f"  {platform}: {url}")


def cmd_dashboard(args):
    """Show dashboard information."""
    crm = CRMCommands()
    crm.show_stats()
    crm.get_leads_for_outreach()
    crm.close()
    
    print("\n📊 Open dashboard.html in your browser for visual dashboard")


def cmd_find_leads(args):
    """Search for businesses online."""
    searcher = BusinessSearcher()
    
    print(f"\n🔍 Searching for {args.niche} businesses in {args.city}, {args.state}...")
    print("   This may take a minute...\n")
    
    leads = searcher.search_niche(
        niche=args.niche,
        city=args.city,
        state=args.state or '',
        max_results=args.max or 30,
        check_websites=not args.fast
    )
    
    if not leads:
        print("❌ No leads found. Check your API key in config.py")
        return
    
    hot_leads = [l for l in leads if l.priority == 'hot']
    warm_leads = [l for l in leads if l.priority == 'warm']
    
    print(f"\n{'='*60}")
    print(f"Found {len(leads)} businesses")
    print(f"  🔥 HOT (no website): {len(hot_leads)}")
    print(f"  🌡️  WARM (bad/basic site): {len(warm_leads)}")
    print(f"{'='*60}")
    
    # Show top leads
    print(f"\n🔥 TOP HOT LEADS:")
    for lead in hot_leads[:5]:
        print(f"\n  {lead.name}")
        print(f"    📍 {lead.address}")
        print(f"    📞 {lead.phone}")
        print(f"    ⭐ {lead.rating} ({lead.review_count} reviews)")
    
    if warm_leads:
        print(f"\n🌡️  TOP WARM LEADS:")
        for lead in warm_leads[:5]:
            print(f"\n  {lead.name}")
            print(f"    🌐 {lead.website}")
            print(f"    📞 {lead.phone}")
            print(f"    Quality: {lead.website_quality}")
    
    # Save to CRM if requested
    if args.save:
        db = LeadDatabase()
        count = 0
        for lead in leads:
            if lead.priority in ['hot', 'warm']:
                db.add_lead(
                    name=lead.name,
                    website=lead.website if lead.has_website else None,
                    phone=lead.phone,
                    city=lead.city,
                    niche=lead.niche,
                    source='google_places'
                )
                count += 1
        db.close()
        print(f"\n✓ Saved {count} leads to CRM")
    
    # Export to CSV if requested
    if args.export:
        searcher.export_leads(leads, args.export)


def main():
    parser = argparse.ArgumentParser(
        description="Agency Client Acquisition System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # init
    subparsers.add_parser("init", help="Initialize CRM database")
    
    # add-lead
    add_parser = subparsers.add_parser("add-lead", help="Add a new lead")
    add_parser.add_argument("--name", required=True, help="Business name")
    add_parser.add_argument("--website", help="Website URL")
    add_parser.add_argument("--email", help="Email address")
    add_parser.add_argument("--phone", help="Phone number")
    add_parser.add_argument("--city", help="City")
    add_parser.add_argument("--state", help="State")
    add_parser.add_argument("--niche", choices=NICHES, help="Business niche")
    add_parser.add_argument("--source", help="Lead source")
    
    # list
    list_parser = subparsers.add_parser("list", help="List leads")
    list_parser.add_argument("--status", choices=LEAD_STATUSES, help="Filter by status")
    list_parser.add_argument("--niche", choices=NICHES, help="Filter by niche")
    list_parser.add_argument("--city", help="Filter by city")
    list_parser.add_argument("--limit", type=int, help="Max results")
    
    # show
    show_parser = subparsers.add_parser("show", help="Show lead details")
    show_parser.add_argument("lead_id", type=int, help="Lead ID")
    
    # analyze
    analyze_parser = subparsers.add_parser("analyze", help="Analyze a website")
    analyze_parser.add_argument("--website", required=True, help="Website to analyze")
    analyze_parser.add_argument("--lead-id", type=int, help="Save to this lead ID")
    
    # analyze-all
    subparsers.add_parser("analyze-all", help="Analyze all unanalyzed leads")
    
    # generate-message
    msg_parser = subparsers.add_parser("generate-message", help="Generate outreach")
    msg_parser.add_argument("--lead-id", required=True, type=int, help="Lead ID")
    msg_parser.add_argument("--type", required=True, 
                           choices=["email", "phone", "sms", "all"],
                           help="Message type")
    msg_parser.add_argument("--owner-name", help="Owner's first name")
    
    # update-status
    status_parser = subparsers.add_parser("update-status", help="Update lead status")
    status_parser.add_argument("--lead-id", required=True, type=int, help="Lead ID")
    status_parser.add_argument("--status", required=True, choices=LEAD_STATUSES,
                              help="New status")
    
    # add-note
    note_parser = subparsers.add_parser("add-note", help="Add note to lead")
    note_parser.add_argument("--lead-id", required=True, type=int, help="Lead ID")
    note_parser.add_argument("--note", required=True, help="Note text")
    
    # log-outreach
    outreach_parser = subparsers.add_parser("log-outreach", help="Log outreach")
    outreach_parser.add_argument("--lead-id", required=True, type=int, help="Lead ID")
    outreach_parser.add_argument("--type", required=True, 
                                choices=["email", "phone", "sms", "linkedin"],
                                help="Outreach type")
    outreach_parser.add_argument("--subject", help="Email subject")
    
    # stats
    subparsers.add_parser("stats", help="Show CRM statistics")
    
    # outreach
    subparsers.add_parser("outreach", help="Show leads ready for outreach")
    
    # search
    search_parser = subparsers.add_parser("search", help="Search leads")
    search_parser.add_argument("query", help="Search query")
    
    # export
    export_parser = subparsers.add_parser("export", help="Export to CSV")
    export_parser.add_argument("--file", required=True, help="Output file")
    export_parser.add_argument("--status", choices=LEAD_STATUSES, help="Filter")
    
    # import-csv
    import_parser = subparsers.add_parser("import-csv", help="Import from CSV")
    import_parser.add_argument("--file", required=True, help="Input file")
    
    # templates
    subparsers.add_parser("templates", help="List outreach templates")
    
    # guide
    guide_parser = subparsers.add_parser("guide", help="Show lead finding guide")
    guide_parser.add_argument("--niche", help="Niche for search URLs")
    guide_parser.add_argument("--city", help="City for search URLs")
    
    # dashboard
    subparsers.add_parser("dashboard", help="Show dashboard")
    
    # find-leads (NEW - automated search)
    find_parser = subparsers.add_parser("find-leads", help="Search for businesses online")
    find_parser.add_argument("--niche", required=True, help="Business type (barbershop, restaurant, etc)")
    find_parser.add_argument("--city", required=True, help="City to search")
    find_parser.add_argument("--state", help="State abbreviation")
    find_parser.add_argument("--max", type=int, default=30, help="Max results (default 30)")
    find_parser.add_argument("--save", action="store_true", help="Save hot/warm leads to CRM")
    find_parser.add_argument("--export", help="Export to CSV file")
    find_parser.add_argument("--fast", action="store_true", help="Skip website quality checks (faster)")
    
    # Parse and run
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    commands = {
        "init": cmd_init,
        "add-lead": cmd_add_lead,
        "list": cmd_list,
        "show": cmd_show,
        "analyze": cmd_analyze,
        "analyze-all": cmd_analyze_all,
        "generate-message": cmd_generate_message,
        "update-status": cmd_update_status,
        "add-note": cmd_add_note,
        "log-outreach": cmd_log_outreach,
        "stats": cmd_stats,
        "outreach": cmd_outreach,
        "search": cmd_search,
        "export": cmd_export,
        "import-csv": cmd_import_csv,
        "templates": cmd_templates,
        "guide": cmd_guide,
        "dashboard": cmd_dashboard,
        "find-leads": cmd_find_leads,
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
