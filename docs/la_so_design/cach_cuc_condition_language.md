# Cach Cuc Condition Language

This document defines the shared YAML language used to describe `cach_cuc`
conditions.

The goal is to make one common representation that can be used by:

- AI extraction from source books
- fixing and normalizing current extracted `cach_cuc`
- manually adding new `cach_cuc`
- validating and checking `cach_cuc` in code

## Condition Model

A `cach_cuc` is described by relations between independent factors in a chart.
The condition language should express those factors directly, then combine them
with `all` and `any`.

Core factors:

- `palace` (`role`): where a rule applies, such as `menh`, `quan_loc`, `tai_bach`.
- `gender`: whether the rule applies to `male` or `female`.
- `star`: one star, several explicit stars, or a named star group.
- `position`: the earthly branch, palace placement, brightness, or meeting scope.
- `thien can`: heavenly stem constraints, included or excluded.

Examples of relations:

- palace role to position: `palace_at`
- Cung Than to palace role: `cung_than_at_palace`
- star to palace role: `star_with_palace`
- star or group to earthly branch: `star_at_chi`
- star to brightness: `star_brightness`
- stars or group to each other by scope: `stars_meeting`
- gender to the whole rule: `gender_match`
- thien can to the whole rule: `can_match` or `can_exclude`

Use leaf conditions for individual relations. Use `all` when several relations
must hold together, and `any` when the text gives alternatives.

## Top-Level Shape

Each YAML file contains optional reusable `groups` and a list of `cach_cuc`
records.

```yaml
groups:
  luc_sat:
    stars:
    - kinh_duong
    - da_la
    - dia_khong
    - dia_kiep
    - linh_tinh
    - hoa_tinh

cach_cuc:
- id: phu_du_ma
  name: Phu Du Ma
  page: 42
  meaning: Tai gioi, thao luoc, uy quyen
  conditions:
    all:
    - type: star_at_chi
      stars:
      - thien_ma
      at_chi:
      - dan
      - than
    - type: stars_meeting
      stars:
      - thien_ma
      - tu_vi
      - thien_phu
      scope: hoi_hop
```

## Cach Cuc Record

Every `cach_cuc` item should use this shape:

```yaml
- id: string
  name: string
  page: integer
  priority: integer
  meaning: string
  conditions: Condition
```

Fields:

- `id`: stable machine-readable identifier, using lowercase snake case.
- `name`: human-readable name from the book.
- `page`: source page number.
- `priority`: optional ordering or review priority. Default is `0`.
- `meaning`: short meaning or result of the configuration.
- `conditions`: one condition, or a nested `all` / `any` block.

## Vocabulary

Use stable ids rather than display names.

### Palaces

Palace ids are role ids. Use lowercase snake case:

```yaml
menh
than
quan_loc
tai_bach
phuc_duc
phu_the
```

Keep palace ids consistent with the checker implementation.

### Groups

Common group ids:

```yaml
luc_sat: [kinh_duong, da_la, dia_khong, dia_kiep, linh_tinh, hoa_tinh]
sat_tinh: [kinh_duong, da_la, dia_khong, dia_kiep, linh_tinh, hoa_tinh]
luc_cat: [ta_phu, huu_bat, thien_khoi, thien_viet, van_xuong, van_khuc]
cat_tinh: [ta_phu, huu_bat, thien_khoi, thien_viet, van_xuong, van_khuc]
tu_hoa: [hoa_khoa, hoa_quyen, hoa_loc, hoa_ky]
tam_hoa: [hoa_khoa, hoa_quyen, hoa_loc]
xuong_khuc_khoa_tue_tau: [van_xuong, van_khuc, hoa_khoa, thai_tue, tau_thu]
```

### Stars

Star ids should be canonical ids such as:

```yaml
thien_co
thien_tuong
thien_phu
thien_dong
thai_duong
thai_am
tu_vi
thien_ma
```

Moving or time-layered stars should include the layer prefix in the id:

```yaml
luu_thien_ma
```

## Condition Blocks

Conditions can be combined with `all` and `any`.

Use `all` when every child condition must be true:

```yaml
conditions:
  all:
  - type: palace_at
    palace: menh
    chi:
    - suu
  - type: star_at_chi
    stars:
    - thai_duong
    at_chi:
    - mui
```

Use `any` when at least one child condition must be true:

```yaml
conditions:
  any:
  - type: star_with_palace
    palace: menh
    stars:
    - thien_ma
  - type: star_with_palace
    palace: than
    stars:
    - thien_ma
```

`all` and `any` may be nested.

Use `not` to negate a single condition:

```yaml
conditions:
  not:
    type: star_with_palace
    palace: menh
    stars:
    - thien_ky
```

`not` accepts any condition, including nested `all` or `any` blocks.


## Leaf Conditions

### `can_match`

Matches when the heavenly stem is any of the listed values.

```yaml
type: can_match
can:
- giap
- at
```

### `can_exclude`

Matches when the heavenly stem is none of the listed values.

```yaml
type: can_exclude
can:
- binh
- dinh
```

### `gender_match`

Matches a gender-specific rule.

```yaml
type: gender_match
gender: male  # or: female
```

### `cung_than_at_palace`

Matches when the specified Cung Than is located at a palace role.

```yaml
type: cung_than_at_palace
<<<<<<< HEAD:docs/la_so_design/cach_cuc_condition_language.md
=======
cung_than: cung_than_name
>>>>>>> 7c568ba (feat: add cung_than_at_palace):src/refactored/docs/cach_cuc_condition_language.md
palace: role_str
```

### `palace_at`

Matches when a palace is located at one of the listed earthly branches.

```yaml
type: palace_at
palace: role_str
chi: [chi_str]

```

### `only_chinh_tinh`

Matches when the palace has only the specified main star.

```yaml
type: only_chinh_tinh
palace: role_str
star: star_name
```

### `star_brightness`

Matches when the **ALL** listed stars have one of the listed brightness states.

```yaml
type: star_brightness
stars: [star_name]
brightness: [star_brightness]
```

### `star_with_palace`

Matches stars and an **anchor** palace whose positions are constrained by a meeting scope.
Group would follow the mode.

```yaml
type: star_with_palace
palace: role_str
scope: scope_enum  # required; same values as stars_meeting
stars: [star_name]
stars_matching_logic: [any, all]  # optional; default is any. Used only when group_name is not set.
group_name: group_name  # optional
mode: [any, all]  # provide mode or at_least; used only when group_name is set
at_least: integer  # used only when group_name is set
```


### `star_at_chi`

Matches **ALL** stars at an exact position. Group would follow the mode.

```yaml
type: star_at_chi
stars: [star_name]
at_chi: [chi_str]
group_name: group_name
mode: [any, all]  # provide mode or at_least
at_least: integer
```


### `stars_meeting`

Matches explicit stars, group members, or both meeting under a specified scope.

```yaml
type: stars_meeting
stars: [star_name]
scope: scope_enum
stars_matching_logic: [any, all]  # optional; default is any. Used only when group_name is not set.
group_name: group_name  # optional
mode: [any, all]  # provide mode or at_least; used only when group_name is set
at_least: integer  # used only when group_name is set
```


Allowed scopes:

```yaml
tam_hop: trong tam hợp
hoi_hop: trong tam hợp và cung chiếu
dong_hoac_xung: đồng cung hoặc xung chiếu
dong_cung: đồng cung
nhi_hop: đối xứng qua trục ở giữa
xung_chieu: xung chiếu
giap: nằm sát bên cạnh
```

Use these scopes instead of creating separate condition types for together,
opposite, or giap relationships.


## Worked Examples

### Khốc, Hư, Tý, Ngọ, tiền bần hậu phú

Source:

```text
Khốc, Hư, Tý, Ngọ, tiền bần hậu phú
Cung Mệnh an tại Tý Ngọ có Khốc, Hu tọa thủ đồng cung, nên lúc thiếu
thời nghèo túng, từ ngoài 30 tuổi trở đi mới khá giả, về già mới thật giàu có
```

Extraction:

```yaml
- id: khoc_hu_ty_ngo_tien_ban_hau_phu
  name: Khốc, Hư, Tý, Ngọ, tiền bần hậu phú
  page: 123
  meaning: Thuở thiếu thời nghèo túng, từ ngoài 30 tuổi trở đi mới khá giả, về già sung sướng
  conditions:
    all:
    - type: palace_at
      palace: menh
      chi:
      - ty
      - ngo
    - type: star_with_palace
      palace: menh
      stars:
      - thien_hu
    - type: stars_meeting
      stars:
      - thien_khoc
      - thien_hu
      scope: dong_cung
```

Reasoning:

- `Cung Menh an tai Ty Ngo` becomes `palace_at`.
- `Khoc, Hu toa thu` means both stars are in `menh`.
- `dong cung` becomes `stars_meeting` with `scope: dong_cung`.

### Đồng, Nguyệt hãm cung gia Sát

Source:

```text
Đồng, Nguyệt hãm cung gia Sát, trọng kỹ nghệ doanh thương
Cung Mệnh an tại Ngọ có Đồng, Nguyệt tọa thủ đồng cung, gặp Sát tinh hội hợp, là người chuyên về kỹ nghệ, hay kinh doanh, buôn bán.
```

Extraction:

```yaml
- id: dong_nguyet_ngo_sat
  name: Đồng, Nguyệt hãm cung gia Sát
  page: 64
  meaning: Người chuyên về kỹ nghệ, hoặc kinh doanh buôn bán
  conditions:
    all:
    - type: palace_at
      palace: menh
      chi:
      - ngo
    - type: star_with_palace
      palace: menh
      scope: dong_cung
      stars:
      - thien_dong
      - thai_am
    - type: stars_meeting
      scope: hoi_hop
      group_name: sat_tinh
      mode: any
```

Reasoning:

- `Cung Mệnh an tại Ngọ` becomes `palace_at`.
- `Đồng, Nguyệt tọa thủ đồng cung` becomes `star_with_palace` anchored at `menh` with `scope: dong_cung` (both stars in the palace).
- `gặp Sát tinh hội hợp` becomes `stars_meeting` with `group_name: sat_tinh` and `mode: any`.

Use `at_least` when the text specifies a minimum number of members from a
group, for example `at_least: 2`. A grouped condition must provide at least one
of `mode` or `at_least`.



## Extraction Rules

When extracting from a book page:

- Preserve the original `name` as written in the source.
- Keep `meaning` short and faithful to the text.
- Prefer explicit stars in `stars` when the book names the stars directly.
- Prefer `group_name` when the book names a category, such as sat tinh or luc cat.
- Use `all` when the text requires every phrase to be true.
- Use `any` when the text gives alternatives.
- Use nested `any` of `all` blocks for pattern alternatives.
- Do not invent conditions that are not supported by the source page.
- If a condition cannot be represented, add a note outside the condition model
  rather than overloading an existing condition type.

## Manual Authoring Checklist

Before adding or editing a `cach_cuc`, check:

- `id` is unique and snake case.
- every condition has a valid `type`.
- star ids and `group_name` values are canonical.
- alternatives are represented with `any`.
- required combinations are represented with `all`.
- generated YAML can be loaded by the Pydantic model.
