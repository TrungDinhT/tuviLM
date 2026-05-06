# La So Tu Vi

Lá Số Tử Vi is a position-based chart built from a person's birth time. The chart is used both for personal-trait interpretation and for future-period guidance through vận hạn (tiểu hạn, đại hạn and lưu niên đại hạn).

Its static layer places components such as sao, cung roles, tràng sinh, tứ hóa, tuần/triệt, thiên can, and địa chi onto the 12 Cung positions. The important dynamic layers are TIEU_HAN, DAI_HAN, and LUU_NIEN_DAI_HAN. These layers can add or move dynamic components and cung roles without changing the natal/static chart.

The model should make various questions easy:
- What components are in this Cung?
- In which Cung (with which position and role) does a component stay?
- What are the DiaChiEntity, ThienCanEntity, and static role of a Cung?
- What appears in related positions such as tam hợp, xung chiếu, nhị hợp, and lục hại?
- What dynamic components or roles appear for a selected vận hạn period?
- How do dynamic placements interact with static placements?

The core invariant is that static chart data stays stable while selected dynamic period data is replaceable per layer.


# Organization

There are 2 main aspects of a La So Tu Vi:
- the placement: where a component is placed (which DiaChi, which Cung)
- the data: all the properties about a component


# Placement ruleset

There are placement rules for every entities in a La So Tu Vi:
- Dia Chi, Thien Can
- Menh, Cuc
- Sao
- Cung role

Placement rules are the functions, used to compute the position of the components in the placement map of a La So Tu Vi, based on an input, which we call the context.

There are different kinds of context: natal context always applied, alongside with some among periodic and Tu Hoa Phai contexts, resulting in a multi-layer placement map where each layer corresponding to a specific context. !!IMPORTANT: for each layer, there is only 1 and unique presence of a component.


## Natal context

Natal context includes the birth time (hour, day, month, year) and some information derived from that. The components placed with natal context result in the natal placement part/layer of the placement map.

## *Dynamic* periodic context (Van Han)

There are 3 kinds: TIEU_HAN, DAI_HAN, and LUU_NIEN_DAI_HAN. Those contexts vary by the year in which we want to study.

With those contexts, we can compute the placement of a subset of components, resulting overlay layers on the placement map. It means that at the same position, we can have multiple "presence" of the same components, one placed with natal context, and others placed with periodic context.

For each kind of periodic context, there is a specific rule to compute the focus position - the position on the placement chart (i.e. the position of the Cung) in which we should focus on to give prediction for such period.

### Tieu Han

To compute focus_position for Tieu Han, the steps are:

1. Use the Dia Chi of birth year to compute the anchor position
    - If Dia Chi of birth year is Dan / Ngo / Tuat -> anchor at Thin
    - If Dia Chi of birth year is Than / Ty / Thin -> anchor at Tuat
    - If Dia Chi of birth year is Ti / Dau / Suu -> anchor at Mui
    - If Dia Chi of birth year is Hoi / Mao / Mui -> anchor at Suu
2. At the anchor position, assign the anchor value to the Dia Chi of birth year
3. Following van direction, place other Dia Chi following the cycle of Dia Chi => Obtain a map of [DiaChi -> DiaChi], which is the DiaChi of Tieu Han year mapped to position of Cung
4. Use the DiaChi of year to xem Tieu Han, query the map and get the position of the Cung => focus_position

From the steps above, we can see that step 1 -> 3 are always static. The result is a map (i.e. lookup table) so that we can find focus_position from the Dia Chi of Tieu Han year. Step 4 is the part where we get focus_position from that lookup table with the Dia Chi of Tieu Han year

### Dai Han

To compute focus_position for Dai Han, the steps are:

1. From cuc number, we have a tuple of class that represents a range of 10 years. Having "x" is the value of cuc number, the tuple contains 12 elements: (TenYearRange(since=x), TenYearRange(since=x+10), ...)
2. With menh_position (DiaChi), create a maping between that class and the position (DiaChi), starting from menh_position, following van direction to place the every next 10 years.
3. From the current year, compute the current age, then check in that map to get the DiaChi position => focus_position

In a similar way with Tieu Han, step 1 and 2 are always static. The result is a map of each period of 10 years and the focus_position. Step 3 is derived from current age to find focus_position.

### Luu Nien Dai Han

To compute focus_position for Luu Nien Dai Han, the steps are:

1. Get the focus_position from Dai Han
2. Subtract current age to the minimum age of that Dai Han period:
   a. if it's 0 (current age == minimum age Dai Han) => focus_position = Dai Han focus_position
   b. if it's 1 => focus_position = xung_chieu(Dai Han focus_position)
   c. if it's >= 2 => focus_position = xung_chieu(Dai Han focus_position) + (current_age - minimum_age_dai_han - 3) * van_direction


## Tu Hoa Phai context

Tu Hoa Phai is another category of context, which is not dynamic like periodic context, but also contributes to the overlay layers of the placement map. It only applies for Tu Hoa, in which the ThienCan of each Cung can be used to compute the placement for Tu Hoa on the whole placement. Therefore, it results into 12 additional placement layers for Tu Hoa.
