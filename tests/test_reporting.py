"""Tests for the automated situation report generator."""

import pytest
from src.reporting.auto_sitrep import AutoSitrepGenerator
from src.reporting.quality_scorer import QualityScorer

SAMPLE_DOCS = [
    {
        'title': 'WFP Report',
        'text': 'WFP provides food assistance to 33,000 Afghan refugees. Evacuation orders widen in Lebanon.',
        'source': 'WFP',
        'url': 'https://reliefweb.int/example1',
        'date': '2026-03-26',
    },
    {
        'title': 'OCHA Update',
        'text': '600,000 households displaced in Iran. Humanitarian access restricted in southern Lebanon.',
        'source': 'OCHA',
        'url': 'https://reliefweb.int/example2',
        'date': '2026-03-26',
    },
]

class TestAutoSitrep:
    def setup_method(self):
        self.gen = AutoSitrepGenerator()

    def test_generate_report(self):
        report = self.gen.generate(SAMPLE_DOCS)
        assert report['source_documents'] == 2
        assert 'sections' in report

    def test_markdown_output(self):
        report = self.gen.generate(SAMPLE_DOCS)
        md = self.gen.to_markdown(report)
        assert '# Situation Report' in md

class TestQualityScorer:
    def setup_method(self):
        self.scorer = QualityScorer()
        self.gen = AutoSitrepGenerator()

    def test_score_report(self):
        report = self.gen.generate(SAMPLE_DOCS)
        score = self.scorer.score(report)
        assert 0 <= score['overall'] <= 1
        assert score['grade'] in ['A', 'B', 'C', 'D', 'F']
