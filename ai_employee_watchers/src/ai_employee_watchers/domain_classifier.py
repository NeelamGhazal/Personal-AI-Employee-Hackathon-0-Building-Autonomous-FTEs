# domain_classifier.py - Classifies items as Personal or Business domain
import re
from typing import Literal
from pathlib import Path

Domain = Literal['personal', 'business']

# Keywords that indicate business context
BUSINESS_KEYWORDS = [
    # Financial
    'invoice', 'payment', 'billing', 'receipt', 'quote', 'estimate',
    'budget', 'expense', 'revenue', 'profit', 'loss', 'accounting',
    'tax', 'payroll', 'salary', 'bonus', 'commission',

    # Business operations
    'client', 'customer', 'vendor', 'supplier', 'contractor',
    'project', 'deadline', 'milestone', 'deliverable', 'proposal',
    'contract', 'agreement', 'nda', 'sow', 'scope',

    # Marketing/Sales
    'marketing', 'campaign', 'social media', 'facebook', 'instagram',
    'twitter', 'linkedin', 'promotion', 'advertisement', 'ad',
    'lead', 'prospect', 'deal', 'sales', 'crm',

    # Business communication
    'meeting', 'conference', 'presentation', 'report', 'quarterly',
    'annual', 'board', 'stakeholder', 'investor', 'partnership',

    # Technical/Professional
    'api', 'integration', 'deployment', 'production', 'development',
    'sprint', 'jira', 'github', 'repository', 'codebase',
]

# Keywords that indicate personal context
PERSONAL_KEYWORDS = [
    # Personal life
    'family', 'friend', 'birthday', 'anniversary', 'vacation',
    'holiday', 'weekend', 'personal', 'private', 'home',

    # Health/Wellness
    'doctor', 'appointment', 'health', 'gym', 'workout',
    'medication', 'prescription', 'hospital', 'clinic',

    # Personal finance (not business)
    'bank statement', 'credit card', 'mortgage', 'rent', 'utilities',
    'subscription', 'netflix', 'spotify', 'amazon prime',

    # Personal communication
    'how are you', 'whats up', 'hey', 'hi there', 'miss you',
    'love', 'dinner', 'lunch', 'coffee', 'hangout',
]

# Email domains that are typically business
BUSINESS_DOMAINS = [
    '.com', '.io', '.co', '.ai', '.tech', '.dev',
    'company', 'corp', 'inc', 'ltd', 'llc',
]

# Personal email providers
PERSONAL_PROVIDERS = [
    'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
    'icloud.com', 'aol.com', 'protonmail.com', 'live.com',
]


class DomainClassifier:
    """Classifies incoming items as Personal or Business domain"""

    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.personal_path = self.vault_path / 'Personal'
        self.business_path = self.vault_path / 'Business'

        # Ensure domain folders exist
        for subfolder in ['Inbox', 'Needs_Action', 'Done']:
            (self.personal_path / subfolder).mkdir(parents=True, exist_ok=True)
            (self.business_path / subfolder).mkdir(parents=True, exist_ok=True)

    def classify(self,
                 content: str,
                 sender: str = '',
                 subject: str = '',
                 source: str = '') -> Domain:
        """
        Classify content as personal or business

        Args:
            content: The main content/body text
            sender: Email address or contact name
            subject: Subject line if applicable
            source: Source type (email, whatsapp, file, etc.)

        Returns:
            'personal' or 'business'
        """
        # Combine all text for analysis
        full_text = f"{subject} {content} {sender}".lower()

        # Count keyword matches
        business_score = sum(1 for kw in BUSINESS_KEYWORDS if kw in full_text)
        personal_score = sum(1 for kw in PERSONAL_KEYWORDS if kw in full_text)

        # Check sender domain
        if sender:
            sender_lower = sender.lower()
            # Business email domain
            if any(domain in sender_lower for domain in BUSINESS_DOMAINS):
                if not any(provider in sender_lower for provider in PERSONAL_PROVIDERS):
                    business_score += 2
            # Personal email provider
            if any(provider in sender_lower for provider in PERSONAL_PROVIDERS):
                personal_score += 1

        # WhatsApp messages default to personal unless business keywords
        if source == 'whatsapp':
            personal_score += 1

        # Emails with formal subject lines lean business
        if subject:
            subject_lower = subject.lower()
            if any(word in subject_lower for word in ['re:', 'fwd:', 'urgent:', 'action required']):
                business_score += 1

        # Return classification
        if business_score > personal_score:
            return 'business'
        return 'personal'

    def get_target_folder(self, domain: Domain, folder: str = 'Needs_Action') -> Path:
        """Get the target folder path for a domain"""
        if domain == 'business':
            return self.business_path / folder
        return self.personal_path / folder

    def classify_and_route(self,
                          content: str,
                          sender: str = '',
                          subject: str = '',
                          source: str = '') -> tuple[Domain, Path]:
        """Classify content and return domain with target folder"""
        domain = self.classify(content, sender, subject, source)
        target = self.get_target_folder(domain, 'Needs_Action')
        return domain, target


# Convenience function for quick classification
def classify_item(content: str, sender: str = '', subject: str = '', source: str = '') -> Domain:
    """Quick classification without instantiating classifier"""
    full_text = f"{subject} {content} {sender}".lower()

    business_score = sum(1 for kw in BUSINESS_KEYWORDS if kw in full_text)
    personal_score = sum(1 for kw in PERSONAL_KEYWORDS if kw in full_text)

    if source == 'whatsapp':
        personal_score += 1

    return 'business' if business_score > personal_score else 'personal'


if __name__ == '__main__':
    # Test the classifier
    classifier = DomainClassifier('/tmp/test_vault')

    test_cases = [
        {'content': 'Hey, how are you doing? Want to grab coffee?', 'source': 'whatsapp'},
        {'content': 'Invoice #1234 is due. Please process payment ASAP.', 'source': 'email'},
        {'content': 'Project deadline reminder: Sprint 5 ends Friday', 'sender': 'pm@company.io'},
        {'content': 'Happy Birthday! Wishing you a great day!', 'source': 'whatsapp'},
        {'content': 'Q4 Revenue Report - Board Meeting Prep', 'sender': 'cfo@acme.com'},
        {'content': "Don't forget doctor appointment tomorrow at 3pm", 'source': 'whatsapp'},
    ]

    print("Domain Classification Tests:")
    print("=" * 60)
    for case in test_cases:
        domain = classifier.classify(**case)
        print(f"[{domain.upper():8}] {case.get('content', '')[:50]}...")
    print("=" * 60)
