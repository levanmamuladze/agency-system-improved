#!/usr/bin/env python3
"""
Agency Client Acquisition System - Web UI
Run: python app.py
Open: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from crm.database import LeadDatabase
from leads.website_analyzer import WebsiteAnalyzer
from leads.message_generator import MessageGenerator
from leads.business_search import BusinessSearcher
from config import NICHES, LEAD_STATUSES, GOOGLE_PLACES_API_KEY

app = Flask(__name__)


# =============================================================================
# PAGES
# =============================================================================

@app.route('/')
def dashboard():
    """Main dashboard."""
    db = LeadDatabase()
    
    # Get stats
    all_leads = db.get_all_leads()
    stats = {
        'total': len(all_leads),
        'hot': len([l for l in all_leads if not l.get('website')]),
        'analyzed': len([l for l in all_leads if l.get('status') == 'analyzed']),
        'contacted': len([l for l in all_leads if l.get('status') in ['contacted', 'followed_up']]),
        'replied': len([l for l in all_leads if l.get('status') == 'replied']),
        'won': len([l for l in all_leads if l.get('status') == 'closed_won']),
    }
    
    # Get recent leads
    recent_leads = sorted(all_leads, key=lambda x: x.get('created_at', ''), reverse=True)[:10]
    
    # Get leads needing action
    action_leads = [l for l in all_leads if l.get('status') in ['found', 'analyzed', 'replied']][:5]
    
    db.close()
    
    return render_template('dashboard.html', 
                          stats=stats, 
                          recent_leads=recent_leads,
                          action_leads=action_leads)


@app.route('/search')
def search_page():
    """Business search page."""
    has_api_key = GOOGLE_PLACES_API_KEY and GOOGLE_PLACES_API_KEY != 'your-google-places-api-key'
    # Use the canonical niche taxonomy so search, CRM filters and the CLI all agree
    searchable_niches = [n for n in NICHES if n != 'other']
    return render_template('search.html', niches=searchable_niches, has_api_key=has_api_key)


@app.route('/leads')
def leads_page():
    """View all leads."""
    db = LeadDatabase()
    
    status_filter = request.args.get('status')
    niche_filter = request.args.get('niche')
    
    leads = db.get_all_leads(status=status_filter)
    
    if niche_filter:
        leads = [l for l in leads if l.get('niche') == niche_filter]
    
    db.close()
    
    return render_template('leads.html', 
                          leads=leads, 
                          statuses=LEAD_STATUSES,
                          niches=NICHES,
                          current_status=status_filter,
                          current_niche=niche_filter)


@app.route('/lead/<int:lead_id>')
def lead_detail(lead_id):
    """View single lead details."""
    db = LeadDatabase()
    lead = db.get_lead(lead_id)
    analysis = db.get_analysis(lead_id)
    outreach = db.get_outreach_history(lead_id)
    notes = db.get_notes(lead_id)
    db.close()
    
    if not lead:
        return redirect(url_for('leads_page'))
    
    return render_template('lead_detail.html',
                          lead=lead,
                          analysis=analysis,
                          outreach=outreach,
                          notes=notes,
                          statuses=LEAD_STATUSES)


@app.route('/analyze')
def analyze_page():
    """Website analyzer page."""
    return render_template('analyze.html')


@app.route('/messages')
def messages_page():
    """Message generator page."""
    db = LeadDatabase()
    leads = db.get_all_leads()
    db.close()
    return render_template('messages.html', leads=leads)


# =============================================================================
# API ENDPOINTS
# =============================================================================

@app.route('/api/search', methods=['POST'])
def api_search():
    """Search for businesses."""
    data = request.get_json(silent=True) or {}
    niche = data.get('niche')
    city = data.get('city')
    state = data.get('state', '')
    max_results = data.get('max_results', 20)
    
    if not niche or not city:
        return jsonify({'error': 'Niche and city required'}), 400
    
    try:
        searcher = BusinessSearcher()
        leads = searcher.search_niche(niche, city, state, max_results, check_websites=False)
        
        results = []
        for lead in leads:
            results.append({
                'name': lead.name,
                'address': lead.address,
                'phone': lead.phone,
                'website': lead.website,
                'rating': lead.rating,
                'review_count': lead.review_count,
                'has_website': lead.has_website,
                'website_quality': lead.website_quality,
                'priority': lead.priority,
                'place_id': lead.place_id,
                'niche': lead.niche,
                'city': lead.city,
            })
        
        return jsonify({
            'success': True,
            'count': len(results),
            'leads': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/analyze', methods=['POST'])
def api_analyze():
    """Analyze a website."""
    data = request.get_json(silent=True) or {}
    website = data.get('website')
    lead_id = data.get('lead_id')

    if not website:
        return jsonify({'error': 'Website URL required'}), 400

    try:
        analyzer = WebsiteAnalyzer()
        result = analyzer.analyze(website)

        # Persist to the lead if this analysis was launched from a lead page
        if lead_id:
            db = LeadDatabase()
            db.save_analysis(lead_id, result.to_dict())
            db.close()

        return jsonify({
            'success': True,
            'score': result.score,
            'lead_quality': result.lead_quality,
            'issues': [{'type': i.name, 'description': i.description, 'severity': i.severity, 'points': i.points_deducted} for i in result.issues],
            'load_time': result.load_time,
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generate-message', methods=['POST'])
def api_generate_message():
    """Generate outreach message."""
    data = request.get_json(silent=True) or {}
    
    business_name = data.get('business_name')
    owner_name = data.get('owner_name')
    niche = data.get('niche')
    issues = data.get('issues', [])
    message_type = data.get('type', 'email')
    has_website = data.get('has_website', True)
    language = data.get('language', 'en')  # NEW: language support
    
    if not business_name:
        return jsonify({'error': 'Business name required'}), 400
    
    try:
        generator = MessageGenerator()
        
        if message_type == 'email':
            if has_website:
                msg = generator.generate_cold_email(business_name, owner_name, niche, issues, language=language)
            else:
                msg = generator.generate_cold_email_no_website(business_name, owner_name, niche, language=language)
            return jsonify({
                'success': True,
                'subject': msg.subject,
                'body': msg.body
            })
            
        elif message_type == 'phone':
            msg = generator.generate_phone_script(business_name, owner_name, niche, issues, language=language)
            return jsonify({
                'success': True,
                'body': msg.body
            })
            
        elif message_type == 'sms':
            msg = generator.generate_sms(business_name, owner_name, language=language)
            return jsonify({
                'success': True,
                'body': msg.body
            })

        return jsonify({'error': f'Unknown message type: {message_type}'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/leads', methods=['POST'])
def api_add_lead():
    """Add a new lead."""
    data = request.get_json(silent=True) or {}
    
    db = LeadDatabase()
    lead_id = db.add_lead(
        name=data.get('name'),
        website=data.get('website'),
        email=data.get('email'),
        phone=data.get('phone'),
        city=data.get('city'),
        state=data.get('state'),
        niche=data.get('niche'),
        source=data.get('source', 'web_ui')
    )
    db.close()
    
    return jsonify({'success': True, 'lead_id': lead_id})


@app.route('/api/leads/<int:lead_id>/status', methods=['PUT'])
def api_update_status(lead_id):
    """Update lead status."""
    data = request.get_json(silent=True) or {}
    new_status = data.get('status')
    
    if new_status not in LEAD_STATUSES:
        return jsonify({'error': 'Invalid status'}), 400

    db = LeadDatabase()
    db.update_status(lead_id, new_status)
    db.close()
    
    return jsonify({'success': True})


@app.route('/api/leads/<int:lead_id>/note', methods=['POST'])
def api_add_note(lead_id):
    """Add note to lead."""
    data = request.get_json(silent=True) or {}
    note = data.get('note')
    
    if not note:
        return jsonify({'error': 'Note text required'}), 400
    
    db = LeadDatabase()
    db.add_note(lead_id, note)
    db.close()
    
    return jsonify({'success': True})


@app.route('/api/leads/save-batch', methods=['POST'])
def api_save_batch():
    """Save multiple leads from search."""
    data = request.get_json(silent=True) or {}
    leads = data.get('leads', [])
    
    db = LeadDatabase()
    saved = 0
    
    for lead in leads:
        try:
            db.add_lead(
                name=lead.get('name'),
                website=lead.get('website') if lead.get('has_website') else None,
                phone=lead.get('phone'),
                city=lead.get('city'),
                niche=lead.get('niche'),
                source='google_places'
            )
            saved += 1
        except Exception:
            continue
    
    db.close()
    
    return jsonify({'success': True, 'saved': saved})


@app.route('/api/leads/<int:lead_id>/outreach', methods=['POST'])
def api_log_outreach(lead_id):
    """Log an outreach attempt and advance the lead's status."""
    data = request.get_json(silent=True) or {}
    outreach_type = data.get('type')

    if outreach_type not in ('email', 'phone', 'sms', 'linkedin'):
        return jsonify({'error': 'Invalid outreach type'}), 400

    db = LeadDatabase()
    lead = db.get_lead(lead_id)
    if not lead:
        db.close()
        return jsonify({'error': 'Lead not found'}), 404

    db.log_outreach(lead_id, outreach_type, subject=data.get('subject'), body=data.get('body'))

    # Advance the pipeline: found/analyzed -> contacted, contacted -> followed_up
    if lead['status'] in ('found', 'analyzed'):
        db.update_status(lead_id, 'contacted')
    elif lead['status'] == 'contacted':
        db.update_status(lead_id, 'followed_up')

    db.close()
    return jsonify({'success': True})


# =============================================================================
# INIT
# =============================================================================

def init_db():
    """Initialize database, creating tables if they don't exist yet."""
    db = LeadDatabase()
    db.initialize()
    db.close()


if __name__ == '__main__':
    init_db()
    print("\n🚀 Agency System Web UI")
    print("   Open: http://localhost:5000\n")
    # Debug mode exposes the Werkzeug debugger (RCE risk). Opt in explicitly.
    debug = os.environ.get("FLASK_DEBUG", "").lower() in ("1", "true", "yes")
    app.run(debug=debug, port=5000)
