"""Tests for safety education modules."""
import pytest
from src.safety.uxo_guide import get_uxo_guide, get_demining_contact, UXO_SAFETY_RULES
from src.safety.emergency_contacts import get_emergency_contacts
from src.safety.document_protection import get_backup_guide, get_embassy_contacts


class TestUXOGuide:
    def test_all_languages(self):
        for lang in ["en", "fa", "dar", "ar", "zh", "fr", "es", "ru", "tr"]:
            guide = get_uxo_guide(lang)
            assert "recognize" in guide or len(guide) > 0

    def test_has_4_rules(self):
        guide = get_uxo_guide("en")
        assert len(guide) == 4

    def test_demining_contacts(self):
        for code in ["ir", "lb", "af"]:
            contact = get_demining_contact(code)
            assert "org" in contact


class TestEmergencyContacts:
    def test_iran(self):
        contacts = get_emergency_contacts("ir")
        assert len(contacts) > 0
        numbers = [c["number"] for c in contacts]
        assert "110" in numbers  # Police
        assert "115" in numbers  # Ambulance

    def test_lebanon(self):
        contacts = get_emergency_contacts("lb", "ambulance")
        assert len(contacts) > 0

    def test_category_filter(self):
        police = get_emergency_contacts("ir", "police")
        assert all("110" in c["number"] for c in police)


class TestDocumentProtection:
    def test_guide_exists(self):
        for lang in ["en", "fa", "ar"]:
            guide = get_backup_guide(lang)
            assert len(guide) > 100

    def test_embassy_contacts(self):
        for code in ["ir", "lb", "af"]:
            contacts = get_embassy_contacts(code)
            assert len(contacts) > 0