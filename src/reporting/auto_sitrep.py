"""
Automated Situation Report Generator
Generates structured humanitarian situation reports from multiple source documents.

Methodology based on:
- arXiv:2512.19475 (Dec 2025) "A Large-Language-Model Framework for
  Automated Humanitarian Situation Reporting"

Pipeline: Documents → Semantic Clustering → Question Generation → 
          RAG Answer Extraction → Structured Report
"""

import json
import re
from datetime import datetime
from collections import defaultdict
from typing import Optional

# OCHA standard situation report sections
SITREP_SECTIONS = [
    'overview',           # General situation overview
    'displacement',       # Population movement and displacement
    'casualties',         # Casualties and injuries
    'humanitarian_access',# Access constraints
    'food_security',      # Food and nutrition
    'health',            # Health and medical
    'wash',              # Water, sanitation, hygiene
    'shelter',           # Shelter and NFI
    'protection',        # Protection concerns
    'response',          # Humanitarian response activities
    'funding',           # Funding status
    'outlook',           # Forward-looking assessment
]

# Auto-generated questions per section
SECTION_QUESTIONS = {
    'displacement': [
        "How many people have been displaced?",
        "What are the main areas of displacement?",
        "Are displacement numbers increasing or decreasing?",
    ],
    'casualties': [
        "How many people have been killed or injured?",
        "Are civilian casualties being reported?",
    ],
    'humanitarian_access': [
        "Are there access constraints for humanitarian workers?",
        "Which areas are hardest to reach?",
    ],
    'food_security': [
        "How many people are food insecure?",
        "Is food assistance being distributed?",
    ],
    'health': [
        "Are medical facilities operational?",
        "Are there disease outbreaks?",
    ],
    'shelter': [
        "How many shelters are available?",
        "What is the shelter occupancy rate?",
    ],
    'protection': [
        "Are there reports of protection violations?",
        "Are children and women particularly affected?",
    ],
}

class AutoSitrepGenerator:
    """Generate structured situation reports from multiple source documents."""
    
    def generate(self, documents: list, date: str = None) -> dict:
        """Generate a situation report from multiple documents.
        
        Args:
            documents: List of dicts with 'title', 'text', 'source', 'url', 'date'
            date: Report date (defaults to today)
            
        Returns:
            Structured situation report dict
        """
        date = date or datetime.utcnow().strftime('%Y-%m-%d')
        
        # Step 1: Cluster documents by theme
        clusters = self._cluster_by_theme(documents)
        
        # Step 2: Extract answers to standard questions
        sections = {}
        for section_id in SITREP_SECTIONS:
            questions = SECTION_QUESTIONS.get(section_id, [])
            answers = []
            for q in questions:
                answer = self._extract_answer(q, documents)
                if answer['text']:
                    answers.append(answer)
            
            sections[section_id] = {
                'title': section_id.replace('_', ' ').title(),
                'findings': answers,
                'source_count': len(set(
                    a['source'] for a in answers if a.get('source')
                )),
            }
        
        # Step 3: Generate overview
        overview = self._generate_overview(documents, sections)
        sections['overview'] = {
            'title': 'Situation Overview',
            'findings': [{'text': overview, 'source': 'synthesis', 'confidence': 0.8}],
            'source_count': len(documents),
        }
        
        return {
            'report_type': 'situation_report',
            'date': date,
            'generated_at': datetime.utcnow().isoformat(),
            'generator': 'crisisbridge/auto_sitrep',
            'methodology': 'Based on arXiv:2512.19475',
            'source_documents': len(documents),
            'sections': sections,
            'sources': [
                {'title': d.get('title', ''), 'url': d.get('url', ''), 'org': d.get('source', '')}
                for d in documents
            ],
        }
    
    def _cluster_by_theme(self, documents: list) -> dict:
        """Simple keyword-based thematic clustering."""
        clusters = defaultdict(list)
        theme_keywords = {
            'displacement': ['displaced', 'IDP', 'refugee', 'evacuation', 'fled'],
            'health': ['medical', 'hospital', 'health', 'injury', 'WHO'],
            'food': ['food', 'hunger', 'WFP', 'nutrition', 'ration'],
            'shelter': ['shelter', 'housing', 'camp', 'collective'],
            'access': ['access', 'restricted', 'blocked', 'corridor'],
        }
        for doc in documents:
            text = (doc.get('text', '') + ' ' + doc.get('title', '')).lower()
            for theme, keywords in theme_keywords.items():
                if any(kw in text for kw in keywords):
                    clusters[theme].append(doc)
        return dict(clusters)
    
    def _extract_answer(self, question: str, documents: list) -> dict:
        """Extract answer to a question from documents (keyword matching)."""
        q_keywords = set(question.lower().split()) - {'how', 'many', 'are', 'there', 'the', 'is', 'have', 'been', 'what'}
        
        best_match = {'text': '', 'source': '', 'url': '', 'confidence': 0.0}
        
        for doc in documents:
            sentences = re.split(r'[.!?]+', doc.get('text', ''))
            for sent in sentences:
                sent = sent.strip()
                if len(sent) < 20:
                    continue
                sent_words = set(sent.lower().split())
                overlap = len(q_keywords & sent_words)
                # Bonus for sentences with numbers
                has_numbers = bool(re.search(r'\d', sent))
                score = overlap + (2 if has_numbers else 0)
                
                if score > best_match['confidence']:
                    best_match = {
                        'text': sent,
                        'source': doc.get('source', ''),
                        'url': doc.get('url', ''),
                        'confidence': min(1.0, score / 5),
                    }
        
        return best_match
    
    def _generate_overview(self, documents: list, sections: dict) -> str:
        """Generate a synthesis overview from all sections."""
        parts = []
        parts.append(f"Based on {len(documents)} source documents:")
        
        for section_id, section in sections.items():
            if section_id == 'overview':
                continue
            findings = section.get('findings', [])
            if findings:
                top = findings[0]
                if top.get('text'):
                    parts.append(f"- {section['title']}: {top['text'][:150]}")
        
        return ' '.join(parts[:8])

    def to_markdown(self, report: dict) -> str:
        """Convert structured report to readable Markdown."""
        lines = []
        lines.append(f"# Situation Report — {report['date']}")
        lines.append(f"*Generated: {report['generated_at']}*")
        lines.append(f"*Sources: {report['source_documents']} documents*")
        lines.append("")
        
        for section_id in SITREP_SECTIONS:
            section = report['sections'].get(section_id, {})
            if not section.get('findings'):
                continue
            lines.append(f"## {section['title']}")
            for finding in section['findings']:
                text = finding.get('text', '')
                source = finding.get('source', '')
                if text:
                    lines.append(f"- {text}")
                    if source:
                        lines.append(f"  *Source: {source}*")
            lines.append("")
        
        lines.append("## Sources")
        for src in report.get('sources', []):
            lines.append(f"- [{src.get('title', 'Untitled')}]({src.get('url', '#')}) — {src.get('org', '')}")
        
        return '\n'.join(lines)
