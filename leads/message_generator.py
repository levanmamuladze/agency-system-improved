"""
Message Generator Module - Bilingual (English + Greek)

Generates personalized outreach messages based on website analysis.
Each message references specific issues found on their website.

Message Types:
- Cold email (initial outreach)
- Follow-up emails (2-5 touches)
- Phone scripts
- SMS/WhatsApp messages

Languages:
- English (en)
- Greek (el)
"""

from typing import Optional, Dict, List
from dataclasses import dataclass

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from config import (
    AGENCY_NAME, AGENCY_WEBSITE, YOUR_NAME, 
    AGENCY_CALENDLY, AGENCY_PHONE
)


@dataclass
class GeneratedMessage:
    """A generated outreach message."""
    type: str  # email, phone, sms
    subject: Optional[str]  # For emails
    body: str
    personalization_used: List[str]  # What we personalized
    language: str = "en"  # en or el


class MessageGenerator:
    """
    Generates personalized outreach messages in English or Greek.
    
    Usage:
        generator = MessageGenerator()
        
        # English (default)
        msg = generator.generate_cold_email(
            business_name="Joe's Barbershop",
            owner_name="Joe",
            issues=["no SSL", "slow loading"]
        )
        
        # Greek
        msg = generator.generate_cold_email(
            business_name="Κουρείο του Γιάννη",
            owner_name="Γιάννη",
            language="el"
        )
    """
    
    def __init__(self):
        self.agency_name = AGENCY_NAME
        self.your_name = YOUR_NAME
        self.calendly = AGENCY_CALENDLY
        self.phone = AGENCY_PHONE
        self.website = AGENCY_WEBSITE
    
    def _pick_top_issues(self, issues: List[str], count: int = 2) -> List[str]:
        """Pick the most impactful issues to mention."""
        priority = [
            "not mobile-friendly", "mobile",
            "no SSL", "no HTTPS", "security",
            "slow", "loading",
            "not accessible", "unreachable",
            "no call-to-action", "no CTA",
            "outdated", "design",
            "no contact info",
            "broken",
            "SEO", "Google", "meta",
        ]
        
        scored_issues = []
        for issue in issues:
            issue_lower = issue.lower()
            score = 0
            for i, keyword in enumerate(priority):
                if keyword in issue_lower:
                    score = len(priority) - i
                    break
            scored_issues.append((score, issue))
        
        scored_issues.sort(reverse=True, key=lambda x: x[0])
        return [issue for _, issue in scored_issues[:count]]
    
    def _format_issues_for_email(self, issues: List[str], language: str = "en") -> str:
        """Format issues into a natural sentence."""
        if not issues:
            if language == "el":
                return "χρειάζεται κάποιες βελτιώσεις"
            return "could use some improvements"
        
        if language == "el":
            # Greek issue translations
            issue_translations = {
                "no ssl": "δεν έχει πιστοποιητικό ασφαλείας",
                "not mobile-friendly": "δεν είναι φιλικό για κινητά",
                "slow loading": "φορτώνει αργά",
                "outdated design": "έχει παλιομοδίτικο design",
                "no call-to-action": "δεν έχει ξεκάθαρη κλήση για δράση",
                "no contact info": "δεν έχει εμφανή στοιχεία επικοινωνίας",
                "missing seo": "λείπουν βασικά στοιχεία SEO",
            }
            
            translated = []
            for issue in issues[:2]:
                issue_lower = issue.lower()
                found = False
                for key, greek in issue_translations.items():
                    if key in issue_lower:
                        translated.append(greek)
                        found = True
                        break
                if not found:
                    translated.append(issue.lower())
            
            if len(translated) == 1:
                return translated[0]
            return f"{translated[0]} και {translated[1]}"
        
        # English
        if len(issues) == 1:
            return issues[0].lower()
        return f"{issues[0].lower()} and {issues[1].lower()}"
    
    def _get_value_prop(self, niche: Optional[str], language: str = "en") -> str:
        """Get niche-specific value proposition."""
        if language == "el":
            value_props = {
                "restaurant": "να αυξήσετε τις κρατήσεις και τις online παραγγελίες",
                "barbershop": "να κλείνετε περισσότερα ραντεβού online",
                "salon": "να προσελκύσετε νέους πελάτες και να δείξετε τη δουλειά σας",
                "gym": "να αυξήσετε τις εγγραφές μελών",
                "dentist": "να χτίσετε εμπιστοσύνη με νέους ασθενείς",
                "real_estate": "να βρίσκετε περισσότερους αγοραστές και πωλητές",
                "plumber": "να δέχεστε περισσότερες κλήσεις για δουλειές",
                "electrician": "να αυξήσετε τα αιτήματα εργασίας",
                "cafe": "να φέρετε περισσότερο κόσμο στο μαγαζί",
                "lawyer": "να προσελκύσετε νέους πελάτες",
                "accountant": "να βρίσκετε νέες συνεργασίες",
                "default": "να φέρετε περισσότερους πελάτες",
            }
        else:
            value_props = {
                "restaurant": "get more reservations and online orders",
                "barbershop": "book more appointments online",
                "salon": "attract new clients and show off your work",
                "gym": "get more membership signups",
                "dentist": "build trust with new patients",
                "real_estate": "generate more buyer and seller leads",
                "plumber": "get more service calls",
                "electrician": "get more service requests",
                "cafe": "bring in more foot traffic",
                "lawyer": "attract new clients",
                "accountant": "find new collaborations",
                "default": "bring in more customers",
            }
        
        return value_props.get(niche, value_props["default"])
    
    def _get_niche_name(self, niche: Optional[str], language: str = "en") -> str:
        """Get niche name in the correct language."""
        if language == "el":
            niche_names = {
                "restaurant": "εστιατόρια",
                "barbershop": "κουρεία",
                "salon": "κομμωτήρια",
                "gym": "γυμναστήρια",
                "dentist": "οδοντιατρεία",
                "real_estate": "μεσιτικά γραφεία",
                "plumber": "υδραυλικούς",
                "electrician": "ηλεκτρολόγους",
                "cafe": "καφετέριες",
                "lawyer": "δικηγορικά γραφεία",
                "accountant": "λογιστές",
                "default": "τοπικές επιχειρήσεις",
            }
        else:
            niche_names = {
                "restaurant": "restaurants",
                "barbershop": "barbershops",
                "salon": "salons",
                "gym": "gyms",
                "dentist": "dental practices",
                "real_estate": "real estate agents",
                "plumber": "plumbers",
                "electrician": "electricians",
                "cafe": "cafes",
                "lawyer": "law firms",
                "accountant": "accountants",
                "default": "local businesses",
            }
        
        return niche_names.get(niche, niche_names["default"])
    
    # =========================================================================
    # COLD EMAILS
    # =========================================================================
    
    def generate_cold_email(
        self,
        business_name: str,
        owner_name: Optional[str] = None,
        niche: Optional[str] = None,
        issues: Optional[List[str]] = None,
        city: Optional[str] = None,
        language: str = "en",
    ) -> GeneratedMessage:
        """
        Generate initial cold email in English or Greek.
        """
        personalization = []
        
        if issues:
            top_issues = self._pick_top_issues(issues)
            issue_text = self._format_issues_for_email(top_issues, language)
            personalization.extend(top_issues)
        else:
            issue_text = "χρειάζεται μια ανανέωση" if language == "el" else "could use a refresh"
        
        value = self._get_value_prop(niche, language)
        niche_name = self._get_niche_name(niche, language)
        personalization.append(f"niche:{niche}" if niche else "niche:default")
        
        if language == "el":
            # GREEK VERSION
            greeting = f"Γεια σας {owner_name}" if owner_name else "Γεια σας"
            
            if city:
                subject = f"Μια γρήγορη ερώτηση για το {business_name}"
                personalization.append(f"city:{city}")
            else:
                subject = f"Η ιστοσελίδα του {business_name}"
            
            body = f"""{greeting},

Έριξα μια ματιά στην ιστοσελίδα του {business_name} και παρατήρησα ότι {issue_text}.

Βοηθάω {niche_name} σαν εσάς {value} με σύγχρονες, mobile-friendly ιστοσελίδες που μετατρέπουν τους επισκέπτες σε πελάτες.

Θα σας ενδιέφερε μια σύντομη κλήση 10 λεπτών για να δούμε αν μπορώ να βοηθήσω; Χωρίς καμία δέσμευση.

{self.your_name}
{self.agency_name}
{self.calendly}"""
        
        else:
            # ENGLISH VERSION
            greeting = f"Hi {owner_name}" if owner_name else "Hi"
            
            if city:
                subject = f"Quick question about {business_name}"
                personalization.append(f"city:{city}")
            else:
                subject = f"Your website, {business_name}"
            
            body = f"""{greeting},

I was looking at {business_name}'s website and noticed it {issue_text}.

I help local {niche_name} like yours {value} with modern, mobile-friendly websites that actually convert visitors into customers.

Would you be open to a quick 10-minute call to see if I can help? No pressure at all.

{self.your_name}
{self.agency_name}
{self.calendly}"""

        return GeneratedMessage(
            type="cold_email",
            subject=subject,
            body=body,
            personalization_used=personalization,
            language=language
        )
    
    def generate_cold_email_no_website(
        self,
        business_name: str,
        owner_name: Optional[str] = None,
        niche: Optional[str] = None,
        language: str = "en",
    ) -> GeneratedMessage:
        """Generate email for businesses with NO website."""
        
        niche_name = self._get_niche_name(niche, language)
        
        if language == "el":
            # GREEK VERSION
            greeting = f"Γεια σας {owner_name}" if owner_name else "Γεια σας"
            
            niche_benefits = {
                "restaurant": "να δέχεστε online παραγγελίες, να δείχνετε το μενού σας και να σας βρίσκουν στο Google",
                "barbershop": "να κλείνουν οι πελάτες ραντεβού 24/7 και να δείχνετε τις δουλειές σας",
                "gym": "να παίρνετε εγγραφές ακόμα κι όταν είστε κλειστά",
                "dentist": "να κλείνουν οι ασθενείς ραντεβού και να χτίζετε εμπιστοσύνη",
                "default": "να σας βρίσκουν online και να μετατρέπετε επισκέπτες σε πελάτες",
            }
            benefits = niche_benefits.get(niche, niche_benefits["default"])
            
            subject = f"{business_name} + online παρουσία"
            
            body = f"""{greeting},

Παρατήρησα ότι το {business_name} δεν έχει ακόμα ιστοσελίδα. Πιθανότατα είστε απασχολημένοι με τη δουλειά και είναι το τελευταίο πράγμα που σκέφτεστε.

Όμως να ξέρετε: οι περισσότεροι άνθρωποι ψάχνουν online πριν επισκεφτούν μια τοπική επιχείρηση. Χωρίς ιστοσελίδα, είστε αόρατοι σε πολλούς πιθανούς πελάτες.

Φτιάχνω απλές, επαγγελματικές ιστοσελίδες για {niche_name} που σας βοηθούν {benefits}.

Θέλετε να σας δείξω ένα γρήγορο mockup; Μου παίρνει μια ώρα και δεν υπάρχει καμία δέσμευση.

{self.your_name}
{self.agency_name}
{self.calendly}"""
        
        else:
            # ENGLISH VERSION
            greeting = f"Hi {owner_name}" if owner_name else "Hi"
            
            niche_benefits = {
                "restaurant": "take online orders, show your menu, and get found on Google",
                "barbershop": "let customers book online 24/7 and show off your cuts",
                "gym": "get membership signups even when you're closed",
                "dentist": "let patients book appointments and build trust instantly",
                "default": "get found online and convert visitors into customers",
            }
            benefits = niche_benefits.get(niche, niche_benefits["default"])
            
            subject = f"{business_name} + online"
            
            body = f"""{greeting},

I noticed {business_name} doesn't have a website yet. You're probably busy running the business, and that's the last thing on your mind.

But here's the thing: most people search online before visiting a local business. Without a website, you're invisible to a lot of potential customers.

I build simple, professional websites for {niche_name} that {benefits}.

Want me to show you a quick mockup? Takes me an hour, and there's no commitment.

{self.your_name}
{self.agency_name}
{self.calendly}"""

        return GeneratedMessage(
            type="cold_email_no_site",
            subject=subject,
            body=body,
            personalization_used=[f"no_website", f"niche:{niche}"],
            language=language
        )
    
    # =========================================================================
    # FOLLOW-UP EMAILS
    # =========================================================================
    
    def generate_followup_email(
        self,
        business_name: str,
        followup_number: int,
        owner_name: Optional[str] = None,
        language: str = "en",
    ) -> GeneratedMessage:
        """Generate follow-up email based on sequence number."""
        
        if language == "el":
            greeting = f"Γεια σας {owner_name}" if owner_name else "Γεια σας"
            
            templates = {
                1: {
                    "subject": f"Re: Ερώτηση για το {business_name}",
                    "body": f"""{greeting},

Απλά ήθελα να επανέλθω σε περίπτωση που χάθηκε το email μου. Θα χαρώ να σας δείξω πώς θα μπορούσε να μοιάζει μια ανανεωμένη ιστοσελίδα για το {business_name}.

Αν δεν είναι η κατάλληλη στιγμή, το καταλαβαίνω απόλυτα. Απλά πείτε μου.

{self.your_name}"""
                },
                2: {
                    "subject": f"Σκέφτηκα το {business_name}",
                    "body": f"""{greeting},

Δούλευα σε ένα project για μια άλλη επιχείρηση και σας σκέφτηκα.

Είμαι ακόμα στη διάθεσή σας να φτιάξω ένα δωρεάν mockup που δείχνει πώς θα μπορούσε να μοιάζει η ιστοσελίδα σας. Χωρίς καμία δέσμευση.

Αξίζει μια γρήγορη ματιά;

{self.your_name}"""
                },
                3: {
                    "subject": "Τελευταίο email από εμένα",
                    "body": f"""{greeting},

Θα το κρατήσω σύντομο: δεν θέλω να είμαι ο ενοχλητικός τύπος που συνεχίζει να στέλνει email.

Αν μια νέα ιστοσελίδα δεν είναι προτεραιότητα αυτή τη στιγμή, κανένα πρόβλημα. Αλλά αν ποτέ θέλετε να το συζητήσουμε, το ημερολόγιό μου είναι εδώ: {self.calendly}

Καλή συνέχεια,
{self.your_name}"""
                },
            }
        else:
            greeting = f"Hi {owner_name}" if owner_name else "Hi"
            
            templates = {
                1: {
                    "subject": f"Re: Quick question about {business_name}",
                    "body": f"""{greeting},

Just bumping this up in case it got buried. Happy to show you exactly what a refreshed website could look like for {business_name}.

If now's not a good time, totally understand. Just let me know.

{self.your_name}"""
                },
                2: {
                    "subject": f"Thought of you, {business_name}",
                    "body": f"""{greeting},

Was working on a project for another local business and thought of you.

Still happy to put together a free mockup showing what your site could look like. No strings attached.

Worth a quick look?

{self.your_name}"""
                },
                3: {
                    "subject": "Last one from me",
                    "body": f"""{greeting},

I'll keep this short: I don't want to be that annoying person who keeps emailing.

If a new website isn't a priority right now, no worries at all. But if you ever want to chat about it, my calendar's here: {self.calendly}

Best of luck with everything,
{self.your_name}"""
                },
            }
        
        template = templates.get(followup_number, templates[3])
        
        return GeneratedMessage(
            type=f"followup_{followup_number}",
            subject=template["subject"],
            body=template["body"],
            personalization_used=[f"followup:{followup_number}"],
            language=language
        )
    
    # =========================================================================
    # PHONE SCRIPTS
    # =========================================================================
    
    def generate_phone_script(
        self,
        business_name: str,
        owner_name: Optional[str] = None,
        niche: Optional[str] = None,
        issues: Optional[List[str]] = None,
        language: str = "en",
    ) -> GeneratedMessage:
        """Generate phone call script in English or Greek."""
        
        niche_name = self._get_niche_name(niche, language)
        
        if issues:
            top_issues = self._pick_top_issues(issues, 1)
            issue_mention = self._format_issues_for_email(top_issues, language)
        else:
            issue_mention = "θα μπορούσε να ανανεωθεί" if language == "el" else "might benefit from a refresh"
        
        if language == "el":
            intro_name = owner_name or "τον ιδιοκτήτη"
            
            script = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ΣΕΝΑΡΙΟ ΤΗΛΕΦΩΝΟΥ: {business_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[ΟΤΑΝ ΑΠΑΝΤΗΣΟΥΝ]

Εσείς: "Γεια σας, μιλάω με {intro_name};"

[ΑΝ ΝΑΙ]

Εσείς: "Γεια σας {owner_name or ''}, είμαι ο/η {self.your_name} από το {self.agency_name}. 
       Σας είχα στείλει ένα email πριν λίγες μέρες σχετικά με την ιστοσελίδα σας. 
       Προλάβατε να το δείτε;"

[ΑΝ ΠΟΥΝ ΟΧΙ / ΔΕΝ ΘΥΜΟΥΝΤΑΙ]

Εσείς: "Κανένα πρόβλημα! Έριξα μια ματιά στην ιστοσελίδα του {business_name} και 
       παρατήρησα ότι {issue_mention}. Συνεργάζομαι με {niche_name} για να τους 
       βοηθήσω να αποκτήσουν περισσότερους πελάτες μέσω μιας σύγχρονης online παρουσίας.
       
       Ξέρω ότι είστε απασχολημένοι, οπότε θα το κρατήσω σύντομο: θα είχατε 10 λεπτά 
       αυτή την εβδομάδα να δείτε κάποιες ιδέες που ετοίμασα; Εντελώς δωρεάν, χωρίς δέσμευση."

[ΑΝ ΔΕΙΧΝΟΥΝ ΕΝΔΙΑΦΕΡΟΝ]

Εσείς: "Τέλεια! Τι σας βολεύει καλύτερα, [αύριο] ή [μεθαύριο];"

[ΚΛΕΙΝΕΤΕ ΤΟ ΡΑΝΤΕΒΟΥ]

Εσείς: "Ωραία! Θα σας στείλω πρόσκληση στο ημερολόγιο. Ανυπομονώ, {owner_name or 'τα λέμε σύντομα'}!"

[ΑΝ ΔΙΣΤΑΣΟΥΝ]

Εσείς: "Το καταλαβαίνω απόλυτα. Να σας πω τι θα κάνω — θα σας στείλω ένα γρήγορο 
       mockup για το πώς θα μπορούσε να μοιάζει η ιστοσελίδα σας. Το κοιτάτε όποτε 
       έχετε χρόνο, κι αν σας αρέσει, μιλάμε. Σας ακούγεται;"

[ΑΝ ΠΟΥΝ ΔΕΝ ΕΝΔΙΑΦΕΡΟΜΑΙ]

Εσείς: "Κανένα πρόβλημα. Αν αλλάξει κάτι, μη διστάσετε να επικοινωνήσετε. 
       Καλή σας μέρα!"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ΣΗΜΕΙΑ ΝΑ ΘΥΜΑΣΤΕ:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Να είστε φιλικοί και χαλαροί
• Μην ακούγεστε σαν να διαβάζετε σενάριο
• Ακολουθήστε την ενέργεια τους
• Πάντα προσφέρετε αξία (δωρεάν mockup) αν διστάζουν
• Ποτέ μην πιέζετε — αφήστε τους να πουν όχι εύκολα
"""
        
        else:
            intro_name = owner_name or "the owner"
            
            script = f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHONE SCRIPT: {business_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[WHEN THEY ANSWER]

You: "Hi, is this {intro_name}?"

[IF YES]

You: "Hey {owner_name or 'there'}, this is {self.your_name} calling from {self.agency_name}. 
     I sent you an email a few days ago about your website. Did you get a chance to see it?"

[IF THEY SAY NO / DON'T REMEMBER]

You: "No worries! I was looking at {business_name}'s website and noticed it 
     {issue_mention}. I work with local {niche_name} to help them 
     get more customers through a modern online presence.
     
     I know you're probably busy, so I'll keep this quick: would you have 10 minutes 
     this week to see some ideas I put together? Completely free, no obligation."

[IF THEY SOUND INTERESTED]

You: "Great! What works better for you, [tomorrow] or [day after]?"

[BOOK THE CALL AND CONFIRM]

You: "Perfect. I'll send you a calendar invite. Looking forward to it, {owner_name or 'talk soon'}!"

[IF THEY'RE HESITANT]

You: "I totally get it. Tell you what—let me send over a quick mockup of what your 
     site could look like. You can check it out whenever you have a minute, and if 
     you like it, we can chat. Sound fair?"

[IF THEY SAY NOT INTERESTED]

You: "No problem at all. If anything changes, feel free to reach out. 
     Have a great day!"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
KEY POINTS TO REMEMBER:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

• Keep it casual and friendly
• Don't sound like you're reading a script
• Mirror their energy level
• If they're short, be short. If they're chatty, chat a bit.
• Always offer value (free mockup) if they hesitate
• Never be pushy—let them say no easily
"""
        
        return GeneratedMessage(
            type="phone_script",
            subject=None,
            body=script,
            personalization_used=[f"niche:{niche}", f"issues:{len(issues) if issues else 0}"],
            language=language
        )
    
    # =========================================================================
    # SMS / WHATSAPP
    # =========================================================================
    
    def generate_sms(
        self,
        business_name: str,
        owner_name: Optional[str] = None,
        message_type: str = "initial",
        language: str = "en",
    ) -> GeneratedMessage:
        """Generate SMS/WhatsApp message in English or Greek."""
        
        if language == "el":
            name = owner_name or ""
            greeting = f"Γεια σας {name}!" if name else "Γεια σας!"
            
            templates = {
                "initial": f"""{greeting} Είμαι ο/η {self.your_name} από το {self.agency_name}. 

Σας έστειλα email για την ιστοσελίδα του {business_name}. Ήθελα να δω αν σας ενδιαφέρει ένα δωρεάν mockup. Χωρίς καμία δέσμευση! 👍""",
                
                "followup": f"""{greeting} Ήθελα να επανέλθω! Θα ήθελα πολύ να σας δείξω κάποιες ιδέες για την ιστοσελίδα του {business_name}. Δωρεάν mockup, χωρίς δέσμευση.

Έχετε 10 λεπτά αυτή την εβδομάδα;""",
                
                "after_call": f"""{greeting} Χάρηκα που μιλήσαμε σήμερα!

Όπως υποσχέθηκα, εδώ είναι ο σύνδεσμος για ραντεβού: {self.calendly}

Τα λέμε!
- {self.your_name}""",
                
                "after_no_answer": f"""{greeting} Προσπάθησα να σας πάρω αλλά δεν σας πρόλαβα! Κανένα πρόβλημα.

Ήθελα να σας δείξω κάποιες ιδέες για την ιστοσελίδα του {business_name}. Απαντήστε εδώ ή κλείστε ραντεβού: {self.calendly}

- {self.your_name}""",
            }
        
        else:
            name = owner_name or "there"
            
            templates = {
                "initial": f"""Hey {name}! This is {self.your_name} from {self.agency_name}. 

I sent an email about {business_name}'s website. Just wanted to follow up and see if you're interested in a free website mockup. No pressure either way! 👍""",
                
                "followup": f"""Hi {name}, just following up! Would love to show you some ideas for {business_name}'s website. Free mockup, no commitment. 

Got 10 min this week?""",
                
                "after_call": f"""Hey {name}! Great chatting today. 

As promised, here's the link to book: {self.calendly}

Talk soon!
- {self.your_name}""",
                
                "after_no_answer": f"""Hey {name}, tried calling but missed you! No worries. 

Just wanted to show you some quick ideas for {business_name}'s website. Reply here or grab time at: {self.calendly}

- {self.your_name}""",
            }
        
        body = templates.get(message_type, templates["initial"])
        
        return GeneratedMessage(
            type=f"sms_{message_type}",
            subject=None,
            body=body,
            personalization_used=[f"sms_type:{message_type}"],
            language=language
        )
    
    # =========================================================================
    # LINKEDIN MESSAGE
    # =========================================================================
    
    def generate_linkedin_message(
        self,
        business_name: str,
        owner_name: Optional[str] = None,
        niche: Optional[str] = None,
        language: str = "en",
    ) -> GeneratedMessage:
        """Generate LinkedIn connection/message."""
        
        niche_name = self._get_niche_name(niche, language)
        
        if language == "el":
            name = owner_name or ""
            greeting = f"Γεια σας {name}!" if name else "Γεια σας!"
            
            body = f"""{greeting} 👋

Είδα το {business_name} και μου άρεσε πολύ αυτό που κάνετε στον χώρο των {niche_name}.

Βοηθάω επιχειρήσεις σαν τη δική σας να αποκτήσουν περισσότερους πελάτες μέσω σύγχρονων ιστοσελίδων που πραγματικά μετατρέπουν. Θα ήθελα να συνδεθούμε και να μοιραστώ κάποιες ιδέες αν σας ενδιαφέρει.

Χωρίς πίεση, απλά κάποιες σκέψεις που μπορεί να βοηθήσουν!

{self.your_name}"""
        
        else:
            name = owner_name or "there"
            
            body = f"""Hi {name}! 👋

I came across {business_name} and really like what you're doing in the {niche_name} space.

I help businesses like yours get more customers through modern websites that actually convert. Would love to connect and share some ideas if you're interested.

No sales pitch, just some thoughts that might help!

{self.your_name}"""
        
        return GeneratedMessage(
            type="linkedin",
            subject=None,
            body=body,
            personalization_used=[f"niche:{niche}"],
            language=language
        )


def generate_all_messages(
    business_name: str,
    owner_name: Optional[str] = None,
    niche: Optional[str] = None,
    issues: Optional[List[str]] = None,
    has_website: bool = True,
    language: str = "en",
) -> Dict[str, GeneratedMessage]:
    """Generate all message types at once."""
    generator = MessageGenerator()
    
    messages = {}
    
    if has_website:
        messages["cold_email"] = generator.generate_cold_email(
            business_name, owner_name, niche, issues, language=language
        )
    else:
        messages["cold_email"] = generator.generate_cold_email_no_website(
            business_name, owner_name, niche, language=language
        )
    
    messages["followup_1"] = generator.generate_followup_email(
        business_name, 1, owner_name, language=language
    )
    messages["followup_2"] = generator.generate_followup_email(
        business_name, 2, owner_name, language=language
    )
    messages["phone"] = generator.generate_phone_script(
        business_name, owner_name, niche, issues, language=language
    )
    messages["sms"] = generator.generate_sms(
        business_name, owner_name, language=language
    )
    messages["linkedin"] = generator.generate_linkedin_message(
        business_name, owner_name, niche, language=language
    )
    
    return messages


if __name__ == "__main__":
    # Test both languages
    gen = MessageGenerator()
    
    print("=" * 60)
    print("ENGLISH EMAIL")
    print("=" * 60)
    msg = gen.generate_cold_email(
        "Joe's Barbershop", 
        "Joe", 
        "barbershop",
        ["no SSL", "not mobile-friendly"]
    )
    print(f"Subject: {msg.subject}")
    print(msg.body)
    
    print("\n" + "=" * 60)
    print("GREEK EMAIL (ΕΛΛΗΝΙΚΑ)")
    print("=" * 60)
    msg = gen.generate_cold_email(
        "Κουρείο του Γιάννη", 
        "Γιάννη", 
        "barbershop",
        ["no SSL", "not mobile-friendly"],
        language="el"
    )
    print(f"Subject: {msg.subject}")
    print(msg.body)
