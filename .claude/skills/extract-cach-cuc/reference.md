# Cach Cuc Extraction — Reference Playbook

Domain knowledge for the `extract-cach-cuc` skill — the things the tooling does NOT print.
For the condition model shape (record fields, leaf types, combinators, model rules) run
`scripts/cc_tools.py schema`; for canonical ids run `scripts/cc_tools.py vocab`. This file is the
complement: leaf semantics, scopes, group members, priority, special cases, merge rule. (`SKILL.md`
owns the procedure.)

## Sources
- Schema (source of truth): `support_tool/cach_cuc/condition_models.py` — read it only to change the
  model; for extraction use `cc_tools.py schema`, which is auto-derived from it and never stale.
- Language spec (prose + worked examples): `src/refactored/docs/cach_cuc_condition_language.md`
- Book pages: `data/tuvitanbien/page_NNN.md`
- Output: `cach_cuc_reviewed.yaml` (keep the `groups:` block at top)

## Ids (run `cc_tools.py vocab`)
- Stars, roles, chi, can, brightness, scopes, group_names, modes — use only the ids it prints.
- Tuần / Triệt ids are `tuan` / `triet`. Palaces use role `id`s; `cung_than` is the Thân palace role.

## Leaf semantics (notes `schema` can't show)
- `can_match` / `can_exclude` — "Can" = heavenly stem; also phrased as **tuổi** / **năm sinh**
  (match), or as **age** implying the stem is in the list (exclude is the negation).
- `only_chinh_tinh` — palace has **ONLY** that main star.
- `star_brightness` — **ALL** listed stars must hold one of the listed brightnesses.
- `star_at_chi` — **ALL** listed stars at the exact chi.
- `cung_than_at_palace` — Cung Thân located at the palace role.
- `stars_matching_logic` (on `star_with_palace` / `stars_meeting`) — applies to the `stars` list only;
  `any` = at least one listed star, `all` = every listed star. Default `any`; auto-nulled when
  `group_name` is set. Pick deliberately: several stars named together usually = `all`; alternatives
  = `any`.
- Group support (`group_name` + `mode`/`at_least`): see model rules in `cc_tools.py schema`.

## Scopes — meaning of each enum value
- `tam_hop` — trong tam hợp
- `hoi_hop` — trong tam hợp và cung chiếu
- `dong_hoac_xung` — đồng cung hoặc xung chiếu
- `dong_cung` — đồng cung
- `nhi_hop` — đối xứng qua trục giữa
- `xung_chieu` — xung chiếu
- `giap` — nằm sát bên cạnh

## Group members
Star membership behind each `group_name` (names live in `vocab.group_names`; composition here).
Mirror these in the `groups:` block at the top of `cach_cuc_reviewed.yaml`.

| group | stars |
|---|---|
| `luc_sat` / `sat_tinh` | kinh_duong, da_la, dia_khong, dia_kiep, linh_tinh, hoa_tinh |
| `luc_cat` / `cat_tinh` | ta_phu, huu_bat, thien_khoi, thien_viet, van_xuong, van_khuc |
| `tu_hoa` | hoa_khoa, hoa_quyen, hoa_loc, hoa_ky |
| `tam_hoa` | hoa_khoa, hoa_quyen, hoa_loc |
| `xuong_khuc_khoa_tue_tau` | van_xuong, van_khuc, hoa_khoa, thai_tue, tau_thu |

## Priority
- WITH explicit name, WITH chính tinh → 3 (e.g. quần thần khánh hội)
- WITHOUT explicit name, WITH chính tinh → 2 (e.g. dịch mã)
- WITH explicit name, WITHOUT chính tinh → 1 (e.g. bình hình tướng ấn)
- WITHOUT explicit name, WITHOUT chính tinh → 0 (e.g. thiên diêu gặp long phượng)

## Extraction rules
- Preserve original `name` verbatim; keep `meaning` short and faithful, keep only the essential meaning, do not repeat the cach_cuc condition; include a very concise `evidence` (raw source text) per record only if it doesn't repeat the cach_cuc condition or the meaning.
- Explicit `stars` when the book names stars; `group_name` when it names a category.
- `all` = every phrase must hold; `any` = alternatives; nest `any` of `all` for pattern alternatives.
- Do NOT invent conditions unsupported by the source page. If a condition can't be represented, add a
  note outside the model rather than overloading a leaf type.
- Notes:
  - **Too general cach_cuc**: The cach_cucs contain only the principal star at the menh palace and are only about characteristics or appearance should be ignored.
  - **Tuần / Triệt:** the book usually names both, but EITHER one is enough — model as `any` of the
    two (and across both Mệnh and Thân when the text says "Mệnh hay Thân").
  - **Meeting the main star(s):** when stars meet the main star the cách cục is about, prefer
    `star_with_palace` (anchor `menh`) over `stars_meeting` — the palace is the anchor for the meeting.
  - **Vague quantity** — "nhiều Sát tinh", "nhiều cát tinh" — map to the matching group (`sat_tinh` / `cat_tinh`) with `at_least: 2`
    ("nhiều" = several, so ≥2), NOT `mode: any`. When the book also names example stars ("nhất là Tử
    Vi, Tướng…"), keep `group_name` + `at_least: 2` as the core and add named stars in `stars` only if
    they sharpen the rule.
  - **Vague condition** - "nhiều sao sáng sủa", "nhiều sao mờ ám xấu xa" - we don't know yet how to correctly express those conditions, so skip cach_cuc like that. On the other hand, if the book mentions that, and also mentions special cases with specific stars or group, then only extract the cach_cuc for such special cases.

## Dedup — merge rule
Different cách cục can carry different names + meanings but the EXACT same conditions; they must
collapse into ONE record. `cc_tools.py check` detects these collisions (every tmp record vs the other
tmp records AND vs every record already in `cach_cuc_reviewed.yaml`). When it reports a group, merge:
- `id`: prefer the explicit câu-phú variant's id; else keep the existing reviewed id.
- `name`: distinct names joined ` / `.  `meaning`: distinct meanings joined `; `.
- `evidence`: concatenate, tagging each page `(tr.74) ... (tr.75) ...`.
- `page`: the câu-phú source page if any, else the first.
- `priority`: RECOMPUTE — gaining an explicit name bumps it (e.g. 2 → 3).
- `conditions`: unchanged.
- If a variant already lives in `cach_cuc_reviewed.yaml`: update it there, drop the duplicate from tmp.

Collapse ONLY when conditions are truly identical. An extra leaf (a `can_match` year clause, an
`any[tuan/triet]` caveat) makes records DISTINCT — keep separate.
