"""
test_supply_chain.py — Unit tests for the supply chain tracker.

Covers:
  - Route loading from JSON data files
  - Status enum mapping
  - Snapshot generation and digest formatting
  - Route status update persistence
  - Disruption rate calculation
"""

import unittest
from datetime import datetime, timezone

from src.logistics.supply_chain import (
    RouteStatus,
    RouteType,
    SupplyRoute,
    SupplyChainSnapshot,
    get_current_snapshot,
    get_route,
    _generate_summary,
)


class TestRouteStatus(unittest.TestCase):
    """Verify SupplyRoute data model."""

    def test_from_dict(self):
        data = {
            "id": "test_route",
            "name": "Test Route",
            "type": "sea",
            "status": "restricted",
            "last_updated": "2026-04-02",
            "notes": "Testing",
            "alternative": "Fly instead",
            "affected_operations": ["WFP", "UNHCR"],
        }
        route = SupplyRoute.from_dict(data)
        self.assertEqual(route.id, "test_route")
        self.assertEqual(route.route_type, RouteType.SEA)
        self.assertEqual(route.status, RouteStatus.RESTRICTED)
        self.assertTrue(route.is_disrupted)
        self.assertEqual(route.status_emoji, "🟠")

    def test_to_dict_round_trip(self):
        route = SupplyRoute(
            id="hormuz",
            name="Hormuz Strait",
            route_type=RouteType.SEA,
            status=RouteStatus.CLOSED,
        )
        data = route.to_dict()
        restored = SupplyRoute.from_dict(data)
        self.assertEqual(restored.id, route.id)
        self.assertEqual(restored.status, route.status)

    def test_open_route_not_disrupted(self):
        route = SupplyRoute(
            id="bab_hawa",
            name="Bab al-Hawa",
            route_type=RouteType.LAND,
            status=RouteStatus.OPEN,
        )
        self.assertFalse(route.is_disrupted)
        self.assertEqual(route.status_emoji, "🟢")

    def test_closed_route_disrupted(self):
        route = SupplyRoute(
            id="rafah",
            name="Rafah Crossing",
            route_type=RouteType.LAND,
            status=RouteStatus.CLOSED,
        )
        self.assertTrue(route.is_disrupted)
        self.assertEqual(route.status_emoji, "🔴")


class TestSnapshot(unittest.TestCase):
    """Verify SupplyChainSnapshot functionality."""

    def _make_snapshot(self) -> SupplyChainSnapshot:
        routes = [
            SupplyRoute("a", "Route A", RouteType.SEA, RouteStatus.OPEN),
            SupplyRoute("b", "Route B", RouteType.SEA, RouteStatus.CLOSED),
            SupplyRoute("c", "Route C", RouteType.LAND, RouteStatus.RESTRICTED),
            SupplyRoute("d", "Route D", RouteType.AIR, RouteStatus.PARTIAL),
        ]
        return SupplyChainSnapshot(
            timestamp=datetime(2026, 4, 2, tzinfo=timezone.utc),
            routes=routes,
            sources=["test"],
        )

    def test_disruption_rate(self):
        snapshot = self._make_snapshot()
        # 2 disrupted out of 4
        self.assertAlmostEqual(snapshot.disruption_rate, 0.5)

    def test_disrupted_routes(self):
        snapshot = self._make_snapshot()
        disrupted = snapshot.disrupted_routes
        self.assertEqual(len(disrupted), 2)
        ids = {r.id for r in disrupted}
        self.assertIn("b", ids)
        self.assertIn("c", ids)

    def test_format_digest_contains_all_routes(self):
        snapshot = self._make_snapshot()
        digest = snapshot.format_digest()
        self.assertIn("Route A", digest)
        self.assertIn("Route B", digest)
        self.assertIn("Route C", digest)
        self.assertIn("Route D", digest)
        self.assertIn("🔴", digest)  # closed
        self.assertIn("🟢", digest)  # open

    def test_format_digest_shows_alternatives_for_disrupted(self):
        route = SupplyRoute(
            "x", "Test Route", RouteType.SEA,
            RouteStatus.CLOSED,
            alternative="Use airbridge",
        )
        snapshot = SupplyChainSnapshot(
            timestamp=datetime.now(timezone.utc),
            routes=[route],
        )
        digest = snapshot.format_digest()
        self.assertIn("Alt: Use airbridge", digest)

    def test_empty_snapshot(self):
        snapshot = SupplyChainSnapshot(
            timestamp=datetime.now(timezone.utc),
            routes=[],
        )
        self.assertEqual(snapshot.disruption_rate, 0.0)
        self.assertEqual(len(snapshot.disrupted_routes), 0)


class TestDataLoading(unittest.TestCase):
    """Verify loading from data files (integration-level)."""

    def test_get_current_snapshot_returns_routes(self):
        """data/supply_chain/critical_routes.json should exist and load."""
        snapshot = get_current_snapshot(refresh=False)
        self.assertGreater(len(snapshot.routes), 0, "Expected at least one route from data file")

    def test_known_route_exists(self):
        route = get_route("hormuz_strait")
        self.assertIsNotNone(route, "Hormuz Strait route should exist in data")
        self.assertEqual(route.route_type, RouteType.SEA)

    def test_rafah_crossing_closed(self):
        route = get_route("rafah_crossing")
        self.assertIsNotNone(route)
        self.assertEqual(route.status, RouteStatus.CLOSED)


class TestSummary(unittest.TestCase):
    """Verify summary generation."""

    def test_summary_with_mixed_status(self):
        routes = [
            SupplyRoute("a", "A", RouteType.SEA, RouteStatus.OPEN),
            SupplyRoute("b", "B", RouteType.SEA, RouteStatus.CLOSED),
        ]
        summary = _generate_summary(routes)
        self.assertIn("2 routes", summary)
        self.assertIn("1 closed", summary)
        self.assertIn("1 open", summary)

    def test_summary_empty(self):
        summary = _generate_summary([])
        self.assertIn("No supply routes", summary)


if __name__ == "__main__":
    unittest.main()
