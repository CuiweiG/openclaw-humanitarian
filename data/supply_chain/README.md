# Supply Chain Status Data

Humanitarian supply chain tracking data for coordinators (B2B/NGO audience).

## Data Sources (Planned)

- **WFP Logistics Cluster** — Weekly operational updates
- **OCHA Humanitarian Access** — Access constraints and route status
- **Port authorities** — Operational status for Port Sudan, Beirut, Bandar Abbas
- **UNHAS** — Humanitarian air service flight schedules

## Files

| File | Description |
|------|-------------|
| `critical_routes.json` | Static definitions of monitored supply routes |
| `port_status.json` | Last-known port operational status (updated by scraper) |

## Update Frequency

- Port status: daily (automated when scraper is operational)
- Route assessments: weekly (manual until API integration complete)

## Privacy

This data layer is **not civilian-facing**. It serves humanitarian coordinators
and logistics officers planning aid delivery operations.
