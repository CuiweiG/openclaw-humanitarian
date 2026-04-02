"""
test_mesh.py — Unit tests for the offline mesh transport layer.

Covers:
  - Bulletin compression and decompression
  - Meshtastic fragmentation (230-byte limit)
  - Wire format serialisation round-trip
  - Briar payload preparation and truncation
  - MeshDispatcher with no transports available
"""

import unittest

from src.offline.mesh import (
    MESHTASTIC_MAX_PAYLOAD,
    HEADER_SIZE,
    HASH_PREFIX_LEN,
    MeshMessage,
    MeshDispatcher,
    Priority,
    compress_bulletin,
    decompress_bulletin,
    fragment_for_meshtastic,
    prepare_for_briar,
)


class TestCompression(unittest.TestCase):
    """Verify zlib compression round-trip integrity."""

    def test_round_trip_ascii(self):
        text = "WFP: 33,000 Afghan refugees receiving food assistance in Iran"
        compressed = compress_bulletin(text)
        self.assertIsInstance(compressed, bytes)
        self.assertEqual(decompress_bulletin(compressed), text)

    def test_round_trip_persian(self):
        text = "سرپناه‌های موجود در بیروت — ظرفیت ۲۰۰ نفر"
        compressed = compress_bulletin(text)
        self.assertEqual(decompress_bulletin(compressed), text)

    def test_round_trip_arabic(self):
        text = "ناس مهجّرين من جنوب لبنان — وقف نار مؤقّت"
        compressed = compress_bulletin(text)
        self.assertEqual(decompress_bulletin(compressed), text)

    def test_compression_reduces_size(self):
        """Repeated text should compress well."""
        text = "evacuation route " * 100
        compressed = compress_bulletin(text)
        self.assertLess(len(compressed), len(text.encode("utf-8")))


class TestFragmentation(unittest.TestCase):
    """Verify Meshtastic fragmentation respects packet limits."""

    def test_short_message_single_fragment(self):
        text = "Short alert: seek shelter now"
        fragments = fragment_for_meshtastic(text, "en")
        self.assertEqual(len(fragments), 1)
        self.assertEqual(fragments[0].fragment_index, 0)
        self.assertEqual(fragments[0].fragment_total, 1)

    def test_fragment_wire_size_within_limit(self):
        text = "Emergency bulletin content. " * 50  # ~1400 chars
        fragments = fragment_for_meshtastic(text, "ar", Priority.LIFE_SAFETY)
        for frag in fragments:
            wire = frag.to_wire()
            self.assertLessEqual(
                len(wire),
                MESHTASTIC_MAX_PAYLOAD,
                f"Fragment {frag.fragment_index} exceeds {MESHTASTIC_MAX_PAYLOAD}B: {len(wire)}B",
            )

    def test_fragments_ordered_and_complete(self):
        text = "A" * 2000  # forces multiple fragments
        fragments = fragment_for_meshtastic(text, "fa")
        self.assertGreater(len(fragments), 1)
        for i, frag in enumerate(fragments):
            self.assertEqual(frag.fragment_index, i)
            self.assertEqual(frag.fragment_total, len(fragments))

    def test_all_fragments_same_hash(self):
        text = "Bulletin with consistent hash across fragments " * 20
        fragments = fragment_for_meshtastic(text, "dar")
        hashes = {f.bulletin_hash for f in fragments}
        self.assertEqual(len(hashes), 1, "All fragments should share the same bulletin hash")

    def test_priority_preserved(self):
        text = "CRITICAL: active strikes in region"
        fragments = fragment_for_meshtastic(text, "en", Priority.LIFE_SAFETY)
        for frag in fragments:
            self.assertEqual(frag.priority, Priority.LIFE_SAFETY)


class TestWireFormat(unittest.TestCase):
    """Verify wire format serialisation round-trip."""

    def test_round_trip(self):
        original = MeshMessage(
            payload=b"\x78\x9c" + b"\x00" * 20,
            language="fa",
            priority=Priority.URGENT,
            fragment_index=2,
            fragment_total=5,
            bulletin_hash="abcdef0123456789abcdef",
        )
        wire = original.to_wire()
        restored = MeshMessage.from_wire(wire)

        self.assertEqual(restored.language, original.language)
        self.assertEqual(restored.priority, original.priority)
        self.assertEqual(restored.fragment_index, original.fragment_index)
        self.assertEqual(restored.fragment_total, original.fragment_total)
        self.assertEqual(restored.payload, original.payload)

    def test_wire_header_size(self):
        """Header should be exactly 4 bytes."""
        msg = MeshMessage(
            payload=b"test",
            language="en",
            bulletin_hash="0" * 16,
        )
        wire = msg.to_wire()
        # 4 (header) + 4 (payload) + 8 (hash)
        self.assertEqual(len(wire), HEADER_SIZE + 4 + HASH_PREFIX_LEN)


class TestBriarPreparation(unittest.TestCase):
    """Verify Briar message preparation."""

    def test_normal_message(self):
        text = "Shelter update: 200 spots available in Beirut"
        msg = prepare_for_briar(text, "en")
        self.assertEqual(msg.fragment_total, 1)
        self.assertEqual(msg.language, "en")
        # Should decompress back
        self.assertEqual(decompress_bulletin(msg.payload), text)

    def test_long_message_truncated(self):
        text = "Very long bulletin. " * 500  # ~10KB
        msg = prepare_for_briar(text, "ar")
        self.assertLessEqual(len(msg.payload), 2048)

    def test_priority_propagated(self):
        text = "Active strikes near Beirut — seek shelter"
        msg = prepare_for_briar(text, "apc", Priority.LIFE_SAFETY)
        self.assertEqual(msg.priority, Priority.LIFE_SAFETY)


class TestDispatcher(unittest.TestCase):
    """Verify MeshDispatcher with no backends available."""

    def test_no_transports_available(self):
        """All transports should fail gracefully when unconfigured."""
        dispatcher = MeshDispatcher()
        results = dispatcher.broadcast(
            "Test bulletin",
            "en",
            region="tehran",
        )
        # No env vars set → all transports unavailable
        for name, success in results.items():
            self.assertFalse(success, f"{name} should not succeed without config")

    def test_delivery_log_populated(self):
        dispatcher = MeshDispatcher()
        dispatcher.broadcast("Test", "en")
        log = dispatcher.get_delivery_log()
        self.assertEqual(len(log), 1)
        self.assertIn("results", log[0])
        self.assertIn("language", log[0])

    def test_status_returns_all_transports(self):
        dispatcher = MeshDispatcher()
        status = dispatcher.get_status()
        self.assertEqual(len(status), 3)  # Briar, Meshtastic, D2C
        transport_names = {s["transport"] for s in status}
        self.assertIn("briar", transport_names)
        self.assertIn("meshtastic", transport_names)
        self.assertIn("d2c_satellite", transport_names)


if __name__ == "__main__":
    unittest.main()
