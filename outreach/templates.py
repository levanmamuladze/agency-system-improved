"""
Outreach Templates Module

Ready-to-use templates for all outreach channels.
Copy, personalize, and send.

Templates are organized by:
- Cold emails (initial + follow-ups)
- Phone scripts
- SMS/WhatsApp
- LinkedIn
- Voicemail drops
"""

# =============================================================================
# COLD EMAIL TEMPLATES
# =============================================================================

COLD_EMAIL_TEMPLATES = {
    "problem_aware": {
        "name": "Problem Aware (They Know They Need Help)",
        "subject_options": [
            "Your website, {business_name}",
            "Quick question about {business_name}",
            "{first_name}, noticed something about your site",
        ],
        "body": """Hi {first_name},

I was looking at {business_name}'s website and noticed {main_issue}.

I help local {niche} owners like you get more customers with modern, mobile-friendly websites that actually convert.

Would you be open to a quick 10-minute call? No pressure.

{your_name}
{calendly_link}""",
    },
    
    "no_website": {
        "name": "No Website (Best Leads)",
        "subject_options": [
            "{business_name} online",
            "Getting {business_name} found online",
            "Customers searching for you",
        ],
        "body": """Hi {first_name},

I noticed {business_name} doesn't have a website yet.

Here's the thing: 97% of people search online before visiting a local business. Without a website, you're invisible to a lot of potential customers.

I build simple, professional websites for {niche} businesses. Nothing fancy—just clean designs that help you get found and get more customers.

Want me to put together a quick mockup? Takes me an hour, zero commitment.

{your_name}
{calendly_link}""",
    },
    
    "competitor_angle": {
        "name": "Competitor Comparison",
        "subject_options": [
            "Your competitors are doing this",
            "{business_name} vs your competition",
            "Noticed something about {niche}s in {city}",
        ],
        "body": """Hi {first_name},

I've been looking at {niche} websites in {city} and noticed your competitors are investing in their online presence.

{business_name}'s website {main_issue}—which means you might be losing customers to businesses with better sites.

I help level the playing field. Would 10 minutes to chat be worth it?

{your_name}""",
    },
    
    "value_offer": {
        "name": "Free Value Offer",
        "subject_options": [
            "Free website audit for {business_name}",
            "I made something for you",
            "Quick gift for {business_name}",
        ],
        "body": """Hi {first_name},

I put together a free website audit for {business_name}. Found a few things that could be costing you customers:

{issues_list}

I help {niche} businesses fix these issues and get more customers. Want me to send over the full report?

{your_name}""",
    },
    
    "social_proof": {
        "name": "Social Proof Angle",
        "subject_options": [
            "Helped another {niche} in {city}",
            "Case study you might like",
            "What we did for a {niche} like yours",
        ],
        "body": """Hi {first_name},

Just finished a website for another {niche} in {city}. They went from barely any online presence to booking {result}.

Looking at {business_name}'s website, I think we could get similar results for you.

Worth a 10-minute call to explore?

{your_name}
{calendly_link}""",
    },
}

FOLLOWUP_TEMPLATES = {
    1: {
        "subject": "Re: {original_subject}",
        "body": """Hi {first_name},

Just bumping this up. Would love to show you what {business_name}'s website could look like.

If now's not a good time, no worries—just let me know.

{your_name}""",
    },
    
    2: {
        "subject": "Thought of {business_name}",
        "body": """Hi {first_name},

Was working on a project for another {niche} and thought of you.

Still happy to put together a free mockup. No strings attached.

Worth a look?

{your_name}""",
    },
    
    3: {
        "subject": "Last one from me",
        "body": """Hi {first_name},

I'll keep this short—I don't want to be annoying.

If a new website isn't on your radar right now, totally get it. But if you ever want to chat, my calendar's here: {calendly_link}

Best of luck with everything,
{your_name}""",
    },
    
    4: {
        "subject": "One more thing",
        "body": """Hi {first_name},

Circling back one final time. Your competitors in {city} are stepping up their websites.

Happy to help you stay competitive, or just say the word and I'll stop reaching out.

{your_name}""",
    },
}

# =============================================================================
# PHONE SCRIPTS
# =============================================================================

PHONE_SCRIPTS = {
    "cold_call_standard": """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COLD CALL SCRIPT: Standard
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[WHEN THEY ANSWER]

"Hi, is this {first_name}?"

[IF YES]

"Hey {first_name}, this is {your_name}. I'm reaching out because I was looking 
at {business_name}'s website and noticed it {main_issue}.

I work with {niche} businesses to help them get more customers through better 
websites. Quick question: is getting more customers something you're focused 
on right now?"

[IF YES → INTEREST]

"Great! What I'd love to do is show you a few ideas—takes about 10 minutes. 
Would tomorrow at [time] or [alternative time] work better for a quick call?"

[IF HESITANT]

"I totally get it—you're busy. Tell you what: let me send over a mockup of 
what your site could look like. You check it out when you have a minute, and 
if you like it, we can chat. Sound fair?"

[IF NOT INTERESTED]

"No problem at all. If anything changes, feel free to reach out. Have a great day!"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",

    "warm_followup": """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHONE SCRIPT: Warm Follow-Up (After Email)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

"Hi {first_name}, this is {your_name}. I sent you an email a few days ago 
about {business_name}'s website—did you get a chance to see it?"

[IF NO / DOESN'T REMEMBER]

"No worries! The gist is: I noticed your website {main_issue}, and I help 
{niche} businesses like yours get more customers with modern sites.

I know you're busy, so I'll keep this quick: would you have 10 minutes 
this week to see some ideas? No obligation at all."

[IF YES, SAW IT]

"What did you think? Any interest in seeing what a refreshed site could 
look like for {business_name}?"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",

    "gatekeeper": """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHONE SCRIPT: Getting Past the Gatekeeper
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[RECEPTIONIST/EMPLOYEE ANSWERS]

"Hi, I'm trying to reach the owner regarding the business website. 
Who would that be?"

[IF THEY ASK WHO'S CALLING]

"My name is {your_name}. I was looking at your website and had some ideas 
that might help bring in more customers. Is [owner] available?"

[IF THEY ASK WHAT IT'S ABOUT]

"I noticed some things on your website that might be costing you customers. 
Wanted to share some ideas. Is the owner available for a quick minute?"

[IF OWNER NOT AVAILABLE]

"No problem. What's the best time to reach them? ... Great, I'll try back then. 
Thanks!"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""",
}

# =============================================================================
# VOICEMAIL SCRIPTS
# =============================================================================

VOICEMAIL_SCRIPTS = {
    "first_voicemail": """
"Hi {first_name}, this is {your_name}. I sent you an email about 
{business_name}'s website. Just wanted to follow up—I noticed a few things 
that might be costing you customers.

Give me a call back at {your_phone} or check out the email I sent. 
Talk soon!"
""",

    "second_voicemail": """
"Hey {first_name}, {your_name} again. Trying to catch you about your website. 
Just wanted to show you some quick ideas to help {business_name} get more 
customers online.

Feel free to call me at {your_phone} or book time at {calendly_link}. 
Hope to connect soon!"
""",
}

# =============================================================================
# SMS / WHATSAPP TEMPLATES
# =============================================================================

SMS_TEMPLATES = {
    "initial": """Hey {first_name}! This is {your_name}. I sent an email about {business_name}'s website—just wanted to follow up. Would you be open to a quick call about getting more customers online? 👍""",
    
    "followup": """Hi {first_name}, following up on {business_name}'s website. Happy to show you some free ideas. Got 10 min this week?""",
    
    "after_call": """Hey {first_name}! Great chatting. Here's the link to book our next call: {calendly_link}

Talk soon!
- {your_name}""",
    
    "after_no_answer": """Hey {first_name}, tried calling but missed you! Just wanted to share some ideas for {business_name}'s website. Reply here or grab time: {calendly_link}""",
    
    "proposal_followup": """Hi {first_name}! Just checking if you had a chance to review the proposal. Any questions? Happy to hop on a quick call.""",
}

# =============================================================================
# LINKEDIN TEMPLATES
# =============================================================================

LINKEDIN_TEMPLATES = {
    "connection_request": """Hi {first_name}! I work with {niche} businesses on their online presence. Would love to connect!""",
    
    "after_connection": """Thanks for connecting, {first_name}!

I took a look at {business_name}'s website and had a few ideas that might help bring in more customers.

Would you be open to a quick chat? No pitch—just some thoughts.

{your_name}""",
    
    "inmail": """Hi {first_name},

I came across {business_name} and noticed your website {main_issue}.

I help {niche} businesses get more customers with modern websites. Would love to share some ideas if you're interested.

No pressure either way!

{your_name}""",
}

# =============================================================================
# OBJECTION HANDLERS
# =============================================================================

OBJECTION_HANDLERS = {
    "not_interested": {
        "response": """I totally get it. Quick question though—is it because you're happy with your current website, or just not a priority right now?""",
        "followup": {
            "happy_with_site": "That's great! Mind if I check back in a few months?",
            "not_priority": "Makes sense. When would be a better time to revisit this?",
        }
    },
    
    "too_expensive": {
        "response": """I hear you. What budget were you thinking? I might have options that fit.""",
        "followup": "We could start with just a landing page and build from there. Would that help?",
    },
    
    "already_have_someone": {
        "response": """Nice! Are you happy with them, or open to seeing other options?""",
        "followup": "No worries. If anything changes, feel free to reach out. Good luck!",
    },
    
    "need_to_think": {
        "response": """Totally understand. What specifically would you want to think through? Maybe I can help.""",
        "followup": "How about I send some examples and we reconnect next week?",
    },
    
    "send_info": {
        "response": """Happy to! Quick question: what specifically would be most helpful to see? That way I can tailor it.""",
        "followup": "Perfect. I'll send that over. When's a good time for a quick follow-up call?",
    },
    
    "bad_timing": {
        "response": """Totally get it. When would be a better time to reconnect?""",
        "followup": "I'll put a reminder in my calendar. Talk then!",
    },
}


class OutreachTemplates:
    """
    Access and customize outreach templates.
    
    Usage:
        templates = OutreachTemplates()
        
        # Get cold email
        email = templates.get_cold_email("problem_aware", {
            "business_name": "Joe's Barbershop",
            "first_name": "Joe",
            "niche": "barbershop",
            "main_issue": "isn't mobile-friendly",
            "your_name": "Alex",
            "calendly_link": "calendly.com/alex/15min"
        })
        print(email["subject"])
        print(email["body"])
    """
    
    @staticmethod
    def get_cold_email(template_key: str, variables: dict) -> dict:
        """Get a cold email template with variables filled in."""
        template = COLD_EMAIL_TEMPLATES.get(template_key)
        if not template:
            raise ValueError(f"Unknown template: {template_key}")
        
        # Pick first subject option by default
        subject = template["subject_options"][0].format(**variables)
        body = template["body"].format(**variables)
        
        return {
            "name": template["name"],
            "subject": subject,
            "subject_options": [s.format(**variables) for s in template["subject_options"]],
            "body": body,
        }
    
    @staticmethod
    def get_followup(followup_number: int, variables: dict) -> dict:
        """Get a follow-up email template."""
        template = FOLLOWUP_TEMPLATES.get(followup_number)
        if not template:
            template = FOLLOWUP_TEMPLATES[3]  # Default to last one
        
        return {
            "subject": template["subject"].format(**variables),
            "body": template["body"].format(**variables),
        }
    
    @staticmethod
    def get_phone_script(script_key: str, variables: dict) -> str:
        """Get a phone script with variables filled in."""
        script = PHONE_SCRIPTS.get(script_key)
        if not script:
            script = PHONE_SCRIPTS["cold_call_standard"]
        
        return script.format(**variables)
    
    @staticmethod
    def get_sms(sms_type: str, variables: dict) -> str:
        """Get an SMS template."""
        template = SMS_TEMPLATES.get(sms_type, SMS_TEMPLATES["initial"])
        return template.format(**variables)
    
    @staticmethod
    def get_objection_handler(objection: str) -> dict:
        """Get an objection handler."""
        return OBJECTION_HANDLERS.get(objection, {
            "response": "I understand. What would need to change for this to make sense?",
            "followup": "Fair enough. Can I check back in a few weeks?",
        })
    
    @staticmethod
    def list_templates():
        """List all available templates."""
        print("\nCOLD EMAIL TEMPLATES:")
        for key, template in COLD_EMAIL_TEMPLATES.items():
            print(f"  - {key}: {template['name']}")
        
        print("\nFOLLOW-UP EMAILS:")
        for num in FOLLOWUP_TEMPLATES:
            print(f"  - followup_{num}")
        
        print("\nPHONE SCRIPTS:")
        for key in PHONE_SCRIPTS:
            print(f"  - {key}")
        
        print("\nSMS TEMPLATES:")
        for key in SMS_TEMPLATES:
            print(f"  - {key}")
        
        print("\nOBJECTION HANDLERS:")
        for key in OBJECTION_HANDLERS:
            print(f"  - {key}")


if __name__ == "__main__":
    OutreachTemplates.list_templates()
