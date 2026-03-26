"""Tests for the NLP crisis information extraction engine."""

import pytest
from src.nlp.extractor import CrisisExtractor
from src.nlp.classifier import SectorClassifier
from src.nlp.summarizer import BulletinSummarizer
from src.nlp.entities import HumanitarianNER

SAMPLE_TEXT = """
Almost a month into the escalation, hostilities continue to intensify 
across multiple fronts. In Iran, WFP continues to provide food and cash 
assistance to around 33,000 Afghan refugees in settlements. In Lebanon, 
evacuation orders widen and displacement accelerates, with humanitarian 
access severely restricted in southern areas. Over 58,000 Syrian returnees 
have been provided with food assistance at border crossings. An estimated 
600,000 to 1 million households have been displaced. At least 1,200 people 
have been killed and 17,000 injured since February 28, 2026.
"""

class TestCrisisExtractor:
    def setup_method(self):
        self.extractor = CrisisExtractor()

    def test_extract_casualties(self):
        result = self.extractor.extract(SAMPLE_TEXT)
        assert result['casualties']['killed'] >= 1200
        assert result['casualties']['injured'] >= 17000

    def test_extract_locations(self):
        result = self.extractor.extract(SAMPLE_TEXT)
        assert 'Iran' in result['locations']
        assert 'Lebanon' in result['locations']
        assert 'Syria' not in result['locations'] or 'Syria' in result['locations']

    def test_classify_needs(self):
        result = self.extractor.extract(SAMPLE_TEXT)
        assert 'food' in result['needs']

    def test_assess_urgency(self):
        result = self.extractor.extract(SAMPLE_TEXT)
        assert result['urgency'] in ['critical', 'high']

class TestSectorClassifier:
    def setup_method(self):
        self.classifier = SectorClassifier()

    def test_classify_food_security(self):
        results = self.classifier.classify(SAMPLE_TEXT, threshold=1)
        sectors = [r['sector'] for r in results]
        assert 'food_security' in sectors

    def test_primary_sector(self):
        result = self.classifier.get_primary_sector(SAMPLE_TEXT)
        assert result is not None
        assert 'sector' in result

class TestSummarizer:
    def setup_method(self):
        self.summarizer = BulletinSummarizer()

    def test_summary_within_limit(self):
        summary = self.summarizer.summarize(SAMPLE_TEXT, max_words=200)
        assert len(summary.split()) <= 200

    def test_summary_not_empty(self):
        summary = self.summarizer.summarize(SAMPLE_TEXT)
        assert len(summary) > 0

class TestNER:
    def setup_method(self):
        self.ner = HumanitarianNER()

    def test_find_organizations(self):
        entities = self.ner.extract_entities(SAMPLE_TEXT)
        orgs = [o['abbreviation'] for o in entities['organizations']]
        assert 'WFP' in orgs

    def test_find_locations(self):
        entities = self.ner.extract_entities(SAMPLE_TEXT)
        locs = [l['name'] for l in entities['locations']]
        assert 'Iran' in locs
        assert 'Lebanon' in locs
