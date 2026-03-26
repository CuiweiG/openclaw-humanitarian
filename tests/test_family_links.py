"""Tests for Family Links tracing system."""
import pytest
from src.family_links.registry import FamilyLinkRequest, FamilyLinkRegistry
from src.family_links.matcher import FuzzyMatcher
from src.family_links.privacy import PrivacyGuard


class TestFamilyLinkRequest:
    def test_create_request(self):
        req = FamilyLinkRequest("Ahmad Hassan", "Tehran", "@user123", "fa")
        assert req.request_id
        assert req.status == "active"
        assert len(req.request_id) == 12

    def test_public_view_anonymizes(self):
        req = FamilyLinkRequest("Ahmad Hassan", "Tehran", "@secret", "fa")
        public = req.public_view()
        assert "@secret" not in str(public)
        assert public["seeking"] == "A***"


class TestRegistry:
    def test_submit_and_search(self):
        reg = FamilyLinkRegistry()
        req = FamilyLinkRequest("Ahmad", "Tehran", "@user", "fa")
        reg.submit_request(req)
        results = reg.search("Ahmad")
        assert len(results) == 1

    def test_expire_old(self):
        reg = FamilyLinkRegistry()
        req = FamilyLinkRequest("Test", "Test", "@test", "en")
        from datetime import datetime, timedelta
        req.created_at = datetime.utcnow() - timedelta(days=31)
        reg.submit_request(req)
        expired = reg.expire_old_requests(days=30)
        assert expired == 1


class TestFuzzyMatcher:
    def test_exact_match(self):
        m = FuzzyMatcher()
        assert m.match_score("Ahmad", "Ahmad") == 1.0

    def test_prefix_normalization(self):
        m = FuzzyMatcher()
        assert m.normalize_name("al-Hassan") == "hassan"

    def test_location_alias(self):
        m = FuzzyMatcher()
        assert m.location_match("Tehran", "\u062a\u0647\u0631\u0627\u0646")


class TestPrivacy:
    def test_anonymize(self):
        guard = PrivacyGuard()
        req = FamilyLinkRequest("Ahmad", "Tehran", "@secret", "fa")
        anon = guard.anonymize_request(req)
        assert anon["seeking"] == "A***"
        assert "secret" not in str(anon)

    def test_gdpr_delete(self):
        guard = PrivacyGuard()
        reg = FamilyLinkRegistry()
        req = FamilyLinkRequest("Test", "Test", "@test", "en")
        reg.submit_request(req)
        assert guard.gdpr_delete(reg, req.request_id)
        assert reg.active_count == 0