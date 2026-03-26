"""Tests for Mental Health & Psychosocial Support module."""
import pytest
from src.mhpss.helplines import get_helplines, CRISIS_HELPLINES
from src.mhpss.self_help import get_breathing_exercise, get_grounding_exercise, BREATHING_EXERCISE
from src.mhpss.referral import ReferralEngine


class TestHelplines:
    def test_iran_helplines(self):
        results = get_helplines("ir", "fa")
        assert len(results) > 0
        assert any("123" in str(h.get("number", "")) for h in results)

    def test_lebanon_helplines(self):
        results = get_helplines("lb", "ar")
        assert len(results) > 0

    def test_international_always_included(self):
        results = get_helplines("ir")
        orgs = [h["name"] for h in results]
        assert any("ICRC" in o for o in orgs)

    def test_all_countries_have_data(self):
        for code in ["ir", "lb", "af", "sy"]:
            assert code in CRISIS_HELPLINES


class TestSelfHelp:
    def test_breathing_all_languages(self):
        for lang in ["en", "fa", "dar", "ar", "zh", "fr", "es", "ru", "tr"]:
            steps = get_breathing_exercise(lang)
            assert len(steps) == 5, f"Language {lang} has {len(steps)} steps"

    def test_grounding_all_languages(self):
        for lang in ["en", "fa", "dar", "ar", "zh", "fr", "es", "ru", "tr"]:
            text = get_grounding_exercise(lang)
            assert len(text) > 50, f"Language {lang} grounding too short"


class TestReferral:
    def test_crisis_detection(self):
        engine = ReferralEngine()
        assert engine.assess_urgency("I want to kill myself") == "crisis"

    def test_high_urgency(self):
        engine = ReferralEngine()
        assert engine.assess_urgency("I feel hopeless and can't go on") == "high"

    def test_crisis_referral(self):
        engine = ReferralEngine()
        ref = engine.get_referral("crisis", "lb", "ar")
        assert ref["urgency"] == "crisis"
        assert "IMMEDIATE" in ref["action"]
        assert len(ref["resources"]) > 0