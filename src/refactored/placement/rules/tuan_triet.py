import src.refactored.placement.primitives as pp


TUAN_TRIET_RULES = [
    pp.TuanTrietPosition(
        pair_ids=("triet_1", "triet_2"),
        pair_position_fn=pp.triet_positions_fn,
    ),
    pp.TuanTrietPosition(
        pair_ids=("tuan_1", "tuan_2"),
        pair_position_fn=pp.tuan_positions_fn,
    ),
]
