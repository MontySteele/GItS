"""A Plan line that reaches the packet as a raw res:// sprite path renders as
the pip it draws, like a bracketed sprite tag (Kokomi wave, 2026-10-13)."""
from understudy.blindplay_read import _spaced


def test_two_raw_energy_paths_read_as_two_energy():
    p = "res://images/packed/sprite_fonts/silent_energy_icon.png"
    assert _spaced(f"Gain {p}{p}.") == "Gain 2 Energy."


def test_one_raw_energy_path_after_a_number_is_the_unit():
    p = "res://images/packed/sprite_fonts/kokomi_energy_icon.png"
    assert _spaced(f"Gain 3{p}.") == "Gain 3 Energy."
