# Remaining Work

This note tracks design topics that are still intentionally unfinished. Domain
rules remain grounded in `../domain_context.md`.

## View Models

`LaSoView` and `CungView` are not designed yet.

Open questions:

- how UI-facing Cung groups should be derived from `Cung`
- how catalog data should be joined into display rows
- which compatibility shape is needed for old `src/tuvi` callers

## Tu Hoa Phai Query API

`TuHoaPhaiContext` and layer assembly exist, but `LaSo` does not yet expose a
stable query API for building or caching `TU_HOA_PHAI` overlay layers.

Open questions:

- whether callers ask by source `DiaChi`, source `CungId`, or a higher-level
  query
- whether `TU_HOA_PHAI` overlays should share the same `overlay_layers` storage
  without participating in the period LRU cache
- whether one layer or many related layers should be returned for a query

## Catalog-Enriched Queries

The core model intentionally stores placement ids only. Higher-level queries
that return catalog-enriched components are still pending.

Open questions:

- whether enrichment belongs directly on `LaSo` or in a separate view/query
  service
- which query results should stay lightweight ids versus full component data

## Related-Position Queries

The domain needs queries for related positions such as tam hợp, xung chiếu,
nhị hợp, and lục hại. The placement transforms exist, but no `LaSo`/`TinhBan`
query API has been finalized.

Open questions:

- return positions only, `Cung` results, or catalog-enriched results
- whether the API should accept selected layer ids

