"""Tests for accessibility modules."""
import pytest
from src.accessibility.simplified import SimplifiedLanguage, EMOJI_MAP
from src.accessibility.audio_bulletin import AudioBulletin, StubTTSBackend


class TestSimplifiedLanguage:
    def test_add_emoji(self):
        s = SimplifiedLanguage()
        result = s.add_emoji_markers("food distribution at the shelter")
        assert "\U0001F35E" in result  # food emoji
        assert "\U0001F3E0" in result  # shelter emoji

    def test_simplify_removes_citations(self):
        s = SimplifiedLanguage()
        text = "33,000 refugees received aid. Source: WFP Report #4."
        result = s.simplify(text, target_level="basic")
        assert "Source:" not in result

    def test_emoji_map_complete(self):
        assert "medical" in EMOJI_MAP
        assert "food" in EMOJI_MAP
        assert "water" in EMOJI_MAP
        assert "shelter" in EMOJI_MAP


class TestAudioBulletin:
    def test_stub_returns_bytes(self):
        audio = AudioBulletin()
        result = audio.generate_audio("test", "en")
        assert isinstance(result, bytes)

    def test_short_audio(self):
        audio = AudioBulletin()
        result = audio.generate_short_audio(["Point 1", "Point 2"], "en")
        assert isinstance(result, bytes)