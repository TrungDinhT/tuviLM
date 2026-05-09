# View Model

This document records the implemented view/exchange layer for the refactored
chart model.

## Purpose

`LaSoView` and `CungView` are immutable Pydantic snapshots for frontends and
external services. They sit outside the placement core:

- `LaSo`, `TinhBan`, and `Cung` stay query-oriented and lightweight.
- `LaSoView` and `CungView` are frozen, serializable DTOs.
- View construction enriches placement ids with complete catalog components.

The view layer lives in `src/refactored/view/`.

## Snapshot Scope

`build_laso_view(la_so, study_year)` builds one snapshot for one studied year.
It materializes:

- natal/static components
- `TIEU_HAN` for the studied year
- `DAI_HAN` for the studied year
- `LUU_NIEN_DAI_HAN` for the studied year

`TU_HOA_PHAI` overlays are not part of this snapshot. Their stable chart query
API is still tracked in `../plan/01_remaining_work.md`.

## Models

`view/models.py` defines frozen Pydantic models:

- `LayeredComponentView`: `layer_kind` plus a catalog `Component`
- `CungView`: structural Cung metadata plus layered component views
- `TieuHanFocusView`: year `DiaChi` to focus position
- `DaiHanFocusView`: age range to focus position
- `LaSoView`: prior metadata, studied year, focus maps, and all Cung views

The top-level `LaSoView` is flat except for repeated `CungView` entries.
`CungView.components` contains full catalog components rather than component
ids.

## Builder

`view/builder.py` owns DTO construction so the Pydantic models stay pure data
objects.

`build_laso_view(...)`:

1. Builds the three period layers through `LaSo.period_layer(...)`.
2. Queries each `Cung` with natal plus period layer ids.
3. Enriches Cung structure and components through `ComponentCatalog`.
4. Adds static Tiểu Hạn and Đại Hạn focus maps.

Each `LayeredComponentView` keeps only `LayerKind`, not the full `LayerId`,
because a snapshot contains at most one layer of each period kind for its
studied year.

## Streamlit Adapter

`view/streamlit_adapter.py` is a rendering compatibility layer. It converts a
`LaSoView` into small Streamlit-oriented payload models and HTML:

- `StreamlitComponentLine`
- `StreamlitCungCell`
- `StreamlitLaSoPayload`

The adapter groups rendered lines by layer kind and includes the snapshot focus
maps in the center chart cell. These rendering shapes do not leak back into the
core `LaSoView` / `CungView` exchange model.
