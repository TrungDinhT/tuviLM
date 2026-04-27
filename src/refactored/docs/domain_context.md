# La So Tu Vi

Lá Số Tử Vi is a position-based chart built from a person's birth time. The chart is used both for personal-trait interpretation and for future-period guidance through vận hạn (tiểu hạn, đại hạn and lưu niên đại hạn).

Its static layer places components such as sao, cung roles, tràng sinh, tứ hóa, tuần/triệt, thiên can, and địa chi onto the 12 Cung positions. The important dynamic layers are TIEU_HAN, DAI_HAN, and LUU_NIEN_DAI_HAN. These layers can add or move dynamic components and role meanings without changing the natal/static chart.

The model should make various questions easy:
- What components are in this Cung?
- In which Cung (with which position and role) does a component stay?
- What are the DiaChiEntity, ThienCanEntity, and static role of a Cung?
- What appears in related positions such as tam hợp, xung chiếu, nhị hợp, and lục hại?
- What dynamic components or roles appear for a selected vận hạn period?
- How do dynamic placements interact with static placements?

The core invariant is that static chart data stays stable while selected dynamic period data is replaceable per layer.


# Placement ruleset

There are placement rules for every entities in a La So Tu Vi:
- Dia Chi, Thien Can
- Menh, Cuc
- Sao
- Cung role

The same rule set apply for the placement of those entities in both:
- static / natal layer of entities
- dynamic layers of entities depending on Van Han

