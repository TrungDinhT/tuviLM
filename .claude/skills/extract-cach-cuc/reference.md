# Cach Cuc Extraction — Reference Playbook

Domain knowledge for the `extract-cach-cuc` skill: vocabulary, schema, scopes, priority,
special cases, merge rule. (`SKILL.md` owns the procedure.) Run `scripts/cc_tools.py vocab`
for live canonical ids.

## Sources
- Language spec: `src/refactored/docs/cach_cuc_condition_language.md`
- Schema (source of truth, validate against this): `support_tool/cach_cuc/condition_models.py`
- Book pages: `data/tuvitanbien/page_NNN.md`
- Output: `cach_cuc_reviewed.yaml` (keep the `groups:` block at top)

## Record shape
```yaml
- id: string          # snake_case, unique
  name: string        # original VN name, verbatim from book
  page: integer       # source page
  priority: integer   # optional, default 0
  meaning: string     # short, faithful to text
  evidence: string    # optional, raw source text (TBD: include?)
  conditions: Condition
```

## Leaf conditions
- `can_match` — heavenly stem in list `can: [...]` (also formulated as "tuổi" or "năm sinh", which is just a way to talk about "Can")
- `can_exclude` — heavenly stem NOT in list `can: [...]` (also formulated as "age", implicitly having "Can" in list ...)
- `gender_match` — `gender: male | female`
- `cung_than_at_palace` — `palace: role`  (Cung Than located at palace role)
- `palace_at` — `palace: role`, `chi: [...]`  (palace at earthly branch)
- `only_chinh_tinh` — `palace: role`, `star: name`  (palace has ONLY that main star)
- `star_brightness` — `stars: [...]`, `brightness: [...]`  (ALL listed stars have one of listed brightness)
- `star_with_palace` — `palace: role`, `scope: enum` (required), `stars: [...]` and/or group.
  `stars_matching_logic: any | all` (optional, **default `any`**) — applies to the `stars` list
  only; ignored/nulled when `group_name` set. **`any` = at least one listed star; `all` = every
  listed star.** Pick deliberately: the book naming several stars together usually means `all`
  (every one present); listing alternatives means `any`.
- `star_at_chi` — `stars: [...]`, `at_chi: [...]` (ALL stars at exact chi) and/or group
- `stars_meeting` — `stars: [...]`, `scope: enum` and/or group.
  Same `stars_matching_logic: any | all` (optional, **default `any`**) as `star_with_palace`.

## Combinators (nestable)
- `all:` — every child must hold (text requires every phrase)
- `any:` — at least one child (text gives alternatives)
- `not:` — negate single condition (accepts nested all/any)

## Group support (only on star_with_palace / star_at_chi / stars_meeting)
- `group_name: <GroupName>` + EITHER `mode: any|all` OR `at_least: N`
- mode/at_least ONLY valid when group_name set; group_name REQUIRES mode or at_least
- GroupNames: luc_sat, sat_tinh, luc_cat, cat_tinh, tu_hoa, tam_hoa

```
groups:
  luc_sat:
    stars:
    - kinh_duong
    - da_la
    - dia_khong
    - dia_kiep
    - linh_tinh
    - hoa_tinh
  sat_tinh:
    stars:
    - kinh_duong
    - da_la
    - dia_khong
    - dia_kiep
    - linh_tinh
    - hoa_tinh
  luc_cat:
    stars:
    - ta_phu
    - huu_bat
    - thien_khoi
    - thien_viet
    - van_xuong
    - van_khuc
  cat_tinh:
    stars:
    - ta_phu
    - huu_bat
    - thien_khoi
    - thien_viet
    - van_xuong
    - van_khuc
  tu_hoa:
    stars:
    - hoa_khoa
    - hoa_quyen
    - hoa_loc
    - hoa_ky
  tam_hoa:
    stars:
    - hoa_khoa
    - hoa_quyen
    - hoa_loc
```

## Scopes (use instead of separate together/opposite/giap types)
- `tam_hop` — trong tam hợp
- `hoi_hop` — trong tam hợp và cung chiếu
- `dong_hoac_xung` — đồng cung hoặc xung chiếu
- `dong_cung` — đồng cung
- `nhi_hop` — đối xứng qua trục giữa
- `xung_chieu` — xung chiếu
- `giap` — nằm sát bên cạnh

## Brightness values
`mieu`, `vuong`, `dac`, `binh hoa`, `ham`

## DiaChi
ty, suu, dan, meo, thin, ti, ngo, mui, than, dau, tuat, hoi

## ThienCan
giap, at, binh, dinh, mau, ky, canh, tan, nham, quy

## Palace roles (canonical snake_case)
The exhaustive list of roles stays in `src/refactored/components/data/cung_role.json` with `id` and `name`. We need to use `id` in CachCuc expression.

## Star ids — canonical snake_case
The exhaustive lists of stars stay in folder `src/refactored/components/data`, inside those files: `sao.json`, `tuhoa.json` each has `id` and `name` (and some properties). We need to use `id` for them in CachCuc expression. For "tuần" (resp. "triệt"), the `id` is "tuan" (resp. "triet")

## Priority 
- cach_cuc WITH explicit name, WITH chính tinh => 3 (e.g. quần thần khánh hội)
- cach_cuc WITHOUT explicit name, WITH chính tinh => 2 (e.g. dịch mã)
- cach_cuc WITH explicit name, WITHOUT chính tinh => 1 (e.g. binh hình tướng ấn)
- cach_cuc WITHOUT explicit name, WITHOUT chính tinh => 0 (e.g. thiên diêu gặp long phượng)

## Extraction rules
- Preserve original `name` verbatim.
- `meaning` short + faithful.
- Explicit `stars` when book names stars; `group_name` when book names category.
- Use canonical snake_case for roles
- `all` = every phrase true; `any` = alternatives; nest `any` of `all` for pattern alternatives.
- DO NOT invent conditions unsupported by source page.
- If a condition can't be represented → add note outside the model, don't overload a type.
- Include `evidence` (raw source text) per record, but make it concise.
- Some special cases:
  - when Tuần Triệt is mentioned, the book usually mentions both of them, but it actually means any of Tuần or Triệt is enough to create that cách cục
  - whenever the book mentions the meeting of multiple stars with the main stars that the cách cục is about, prefer `star_with_palace` (`menh` for palace) over `stars_meeting`, because we need an anchor for such meeting, and the palace is the right way to do it.
  - vague quantity phrases — "nhiều Sát tinh", "nhiều cát tinh", "nhiều sao sáng sủa (tốt đẹp)",
    "nhiều sao mờ ám (xấu xa)" — map to the matching group (`sat_tinh` / `cat_tinh`) with
    `at_least: 2` (the "nhiều" = several, so ≥2), NOT `mode: any`. When the book also names specific
    example stars ("nhất là Tử Vi, Tướng…"), keep the `group_name` + `at_least: 2` as the core and
    add the named stars in `stars` only if they sharpen the rule.

## Dedup — merge rule
Different cách cục can carry different names + meanings but the EXACT same conditions; they must
collapse into ONE record. `cc_tools.py check` detects these collisions (it compares every record
in `cach_cuc_reviewed_tmp.yaml` against the others AND against every record in
`cach_cuc_reviewed.yaml`). When it reports a collision group, merge it:
- `id`: prefer the explicit câu-phú variant's id; else keep the existing reviewed id.
- `name`: distinct names joined ` / `.  `meaning`: distinct meanings joined `; `.
- `evidence`: concatenate, tagging each page `(tr.74) ... (tr.75) ...`.
- `page`: the câu-phú source page if any, else the first.
- `priority`: RECOMPUTE — gaining an explicit name bumps it (e.g. 2 → 3).
- `conditions`: unchanged.
- If a variant already lives in `cach_cuc_reviewed.yaml`: update it there, drop the duplicate from tmp.

Collapse ONLY when conditions are truly identical. An extra leaf (a `can_match` year clause, an
`any[tuan/triet/sat]` caveat) makes records DISTINCT — keep separate.