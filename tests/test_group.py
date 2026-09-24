"""Group efficiency, checked against hand calculations of the published formulas."""
import math

import pytest

from lythospile import group


def test_converse_labarre_three_by_three():
    theta = math.degrees(math.atan(0.8 / 2.4))
    expected = 1 - theta * (2 * 3 + 2 * 3) / (90 * 9)
    assert group.converse_labarre(3, 3, 2.4, 0.8) == pytest.approx(expected)
    assert group.converse_labarre(3, 3, 2.4, 0.8) == pytest.approx(0.727, abs=1e-3)


def test_los_angeles_three_by_three():
    expected = 1 - 0.8 / (math.pi * 2.4 * 9) * (3 * 2 + 3 * 2 + math.sqrt(2) * 4)
    assert group.los_angeles(3, 3, 2.4, 0.8) == pytest.approx(expected)


def test_seiler_keeney_with_spacing_in_metres():
    expected = 1 - 36 * 2.4 / (75 * 2.4 ** 2 - 7) * 4 / 5 + 0.3 / 6
    assert group.seiler_keeney(3, 3, 2.4) == pytest.approx(expected)
    assert math.isnan(group.seiler_keeney(3, 3, 0.2))


def test_feld_counts_the_neighbours():
    # a 3 × 3 group: 4 corners with 3 neighbours, 4 edges with 5, the centre with 8
    assert group.feld(3, 3) == pytest.approx(1 - (4 * 3 + 4 * 5 + 8) / (16 * 9))
    assert group.feld(2, 1) == pytest.approx(1 - 2 / 32)


def test_one_pile_is_its_own_group():
    assert all(value == 1.0 for value in group.efficiencies(1, 1, 3.0, 3.0, 1.0).values())


def test_efficiencies_are_capped_at_one():
    got = group.efficiencies(2, 2, 20.0, 20.0, 0.5)
    assert all(0 <= value <= 1 for value in got.values())


def test_outline_and_positions():
    assert group.outline(3, 2, 2.0, 3.0, 0.6) == (pytest.approx(3.6), pytest.approx(4.6))
    points = group.positions(3, 2, 2.0, 3.0)
    assert len(points) == 6
    assert sum(x for x, _ in points) == pytest.approx(0.0)


def test_skempton_nc_of_a_deep_block():
    assert group.skempton_nc(4.0, 4.0, 20.0) == pytest.approx(5 * 1.2 * 1.5)
    assert group.skempton_nc(4.0, 8.0, 2.0) == pytest.approx(5 * 1.1 * 1.1)
