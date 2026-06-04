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
      - Dan
      - Than
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
    - Suu
  - type: star_at_chi
    stars:
    - thai_duong
    at_chi:
    - Mui
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
- Giap
- At
```

### `can_exclude`

Matches when the heavenly stem is none of the listed values.

```yaml
type: can_exclude
can:
- Binh
- Dinh
```

### `gender_match`

Matches a gender-specific rule.

```yaml
type: gender_match
gender: male  # or: female
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

Matches stars inside a palace, optionally constraining their meeting scope.
Group would follow the mode.

```yaml
type: star_with_palace
palace: role_str
scope: scope_enum  # required; same values as stars_meeting; default dong_cung
stars: [star_name]
group: group_name
mode: [any, all]
```


### `star_at_chi`

Matches **ALL** stars at an exact position. Group would follow the mode.

```yaml
type: star_at_chi
stars: [star_name]
at_chi: [chi_str]
group: group_name
mode: [any, all]
```


### `stars_meeting`

Matches explicit stars, group members, or both meeting under a specified scope.

```yaml
type: stars_meeting
stars: [star_name]
scope: scope_enum
group: group_name
mode: [any, all]
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
      - Ty
      - Ngo
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
      - Ngo
    - type: stars_meeting
      stars:
      - thien_dong
      - thai_am
      scope: dong_cung
    - type: stars_in_palace
      palace: menh
      stars:
        - thien_dong
        - thai_am
    - type: stars_meeting
      stars:
      - thien_dong
      scope: hoi_hop
      group: sat_tinh
      mode: any
```

Reasoning:

- `Cung Mệnh an tại Ngọ` becomes `palace_at`.
- `Đồng, Nguyệt tọa thủ đồng cung` becomes `stars_meeting` and `stars_in_palace`
- `gặp Sát tinh hội hợp` becomes `stars_meeting` with group `sat_tinh` and mode `any`

Open issue:

`gặp nhiều Sát tinh hội hợp` literally means meeting many malefic stars. The
current language can express meeting the group with `mode: any` or `mode: all`,
but it cannot yet express a threshold such as "at least two stars from this
group". Keep this as an unresolved precision gap until a threshold field is
added.



## Extraction Rules

When extracting from a book page:

- Preserve the original `name` as written in the source.
- Keep `meaning` short and faithful to the text.
- Prefer explicit stars in `stars` when the book names the stars directly.
- Prefer `group` when the book names a category, such as sat tinh or luc cat.
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
- star ids and group ids are canonical.
- alternatives are represented with `any`.
- required combinations are represented with `all`.
- generated YAML can be loaded by the Pydantic model.
