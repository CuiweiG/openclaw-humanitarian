"""Tests for the verification and source checking system."""

import pytest
from src.verification.source_checker import SourceChecker
from src.verification.cross_reference import CrossReferencer
from src.verification.disclaimer_generator import DisclaimerGenerator

class TestSourceChecker:
    def setup_method(self):
        self.checker = SourceChecker()

    def test_tier1_source(self):
        result = self.checker.check("OCHA")
        assert result['tier'] == 'tier_1_un_agency'
        assert result['credibility'] == 1.0
        assert not result['requires_review']

    def test_tier2_source(self):
        result = self.checker.check("Reuters")
        assert result['tier'] == 'tier_2_established'
        assert result['credibility'] >= 0.8

    def test_unknown_source(self):
        result = self.checker.check("Random Blog")
        assert result['tier'] == 'unverified'
        assert result['requires_review']

class TestCrossReferencer:
    def setup_method(self):
        self.xref = CrossReferencer()
        self.sources = [
            {'text': 'WFP provides food to 33000 Afghan refugees in Iran', 'source': 'WFP'},
            {'text': 'Around 33,000 Afghan refugees receive food assistance in Iranian settlements', 'source': 'UNHCR'},
            {'text': 'Food aid reaches Afghan refugee communities in Iran', 'source': 'OCHA'},
        ]

    def test_cross_verified(self):
        result = self.xref.check_claim("food assistance to Afghan refugees in Iran", self.sources)
        assert result['supporting_sources'] >= 2

    def test_number_consistency(self):
        numbers = [
            {'value': 33000, 'source': 'WFP'},
            {'value': 33500, 'source': 'UNHCR'},
        ]
        result = self.xref.check_number_consistency(numbers)
        assert result['consistent']  # Within 20% threshold

class TestDisclaimerGenerator:
    def setup_method(self):
        self.gen = DisclaimerGenerator()

    def test_verified_disclaimer(self):
        result = self.gen.generate({
            'verification_level': 'cross_verified',
            'supporting_sources': 3,
        })
        assert '✅' in result

    def test_unverified_disclaimer(self):
        result = self.gen.generate({'verification_level': 'unverified'})
        assert '❌' in result
