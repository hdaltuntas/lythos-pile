"""The pile analysis as a whole: hand calculations of simple cases, and the refusals."""
import copy
import math

import pytest

from lythospile.config import CLAY_METHODS, DEFAULT_CONFIG, PA, TIP_METHODS
from lythospile.engine import PileAnalysis, analyse
from lythospile.errors import PileError


def one_layer(behaviour="cohesive", **layer):
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    base = {"name": "Uniform", "thickness": 40.0, "behaviour": behaviour, "gamma": 18.0,
            "gamma_sat": 19.0, "phi": 30.0, "cu": 50.0, "OCR": 1.0, "N60": 0.0, "E": 30.0,
            "nu": 0.3, "Cc": 0.0, "Cr": 0.0, "e0": 0.0}
    base.update(layer)
    cfg["soil_profile"] = [base]
    cfg["groundwater"]["depth"] = 100.0
    cfg["group"].update(nx=1, ny=1)
    cfg["pile"].update(D=0.6, L=15.0, top=0.0)
    cfg["loading"]["Q"] = 500.0
    return cfg


def test_a_clay_pile_by_hand():
    cfg = one_layer()
    cfg["options"]["clay_method"] = "alpha_kulhawy"
    a = analyse(cfg)
    res = a.results
    alpha = 0.21 + 0.26 * PA / 50.0
    perimeter, area = math.pi * 0.6, math.pi * 0.09
    assert res["Qs"] == pytest.approx(alpha * 50.0 * perimeter * 15.0)
    assert res["Qb"] == pytest.approx(9 * 50.0 * area)
    assert res["W"] == pytest.approx(25.0 * area * 15.0)
    assert res["Q_ult_net"] == pytest.approx(res["Qs"] + res["Qb"] - res["W"])
    assert res["Q_all"] == pytest.approx(res["Q_ult_net"] / 2.5)
    assert res["FS"] == pytest.approx(res["Q_ult_net"] / 500.0)


def test_a_sand_pile_by_hand_without_the_critical_depth():
    cfg = one_layer("granular", phi=30.0)
    cfg["options"].update(critical_depth=False, K_ratio=1.0, delta_ratio=0.75)
    res = analyse(cfg).results
    K = 1 - math.sin(math.radians(30.0))
    tan_d = math.tan(math.radians(22.5))
    expected = K * tan_d * math.pi * 0.6 * 18.0 * 15.0 ** 2 / 2
    assert res["Qs"] == pytest.approx(expected, rel=1e-9)


def test_the_critical_depth_caps_the_sand():
    cfg = one_layer("granular", phi=30.0)
    capped = analyse(cfg).results
    cfg["options"]["critical_depth"] = False
    free = analyse(cfg).results
    assert capped["Qs"] < free["Qs"]
    assert any(w[0] == "warn_critical_depth" for w in capped["warnings"])


def test_the_water_table_lowers_the_capacity_in_sand():
    cfg = one_layer("granular")
    cfg["options"]["critical_depth"] = False
    dry = analyse(cfg).results
    cfg["groundwater"]["depth"] = 0.0
    wet = analyse(cfg).results
    assert wet["Qs"] < dry["Qs"] and wet["Qb"] <= dry["Qb"]
    assert wet["W"] == pytest.approx(math.pi * 0.09 * 15.0 * (25.0 - 9.81))


def test_the_weight_is_subtracted_only_when_asked():
    cfg = one_layer()
    cfg["options"]["subtract_weight"] = False
    res = analyse(cfg).results
    assert res["Q_ult_net"] == pytest.approx(res["Q_ult"])
    assert res["W"] > 0


def test_every_method_combination_is_reported():
    a = analyse(DEFAULT_CONFIG)
    assert len(a.results["combos"]) == len(CLAY_METHODS) * len(TIP_METHODS)
    for clay in CLAY_METHODS:
        for tip in TIP_METHODS:
            combo = a.results["combos"][f"{clay}|{tip}"]
            assert combo["Q_ult"] == pytest.approx(a.results["shaft"]["Qs"][clay]
                                                   + a.results["base"]["methods"][tip]["Qb"])


def test_the_group_takes_the_smaller_of_efficiency_and_block():
    res = analyse(DEFAULT_CONFIG).results
    group = res["group"]
    assert group["Q_ult"] == pytest.approx(min(group["Q_eff"], group["block"]["Q_ult"]))
    assert group["Q_ult_net"] == pytest.approx(group["Q_ult"] - 9 * res["W"])


def test_a_close_group_in_soft_clay_fails_as_a_block():
    cfg = one_layer(cu=20.0)
    cfg["group"].update(nx=5, ny=5, sx=0.9, sy=0.9, efficiency="unity")
    cfg["loading"]["Q"] = 1000.0
    res = analyse(cfg).results
    assert res["group"]["governing"] == "block"
    assert any(w[0] == "warn_spacing" for w in res["warnings"])


def test_the_required_length_is_the_first_that_passes():
    cfg = one_layer()
    cfg["loading"]["Q"] = 800.0
    a = analyse(cfg)
    L = a.results["required_length"]
    assert math.isfinite(L)
    curve = {round(p["L"], 6): p for p in a.results["length_curve"]}
    assert curve[round(L, 6)]["utilisation"] <= 1.0
    assert curve[round(L - a.L_step, 6)]["utilisation"] > 1.0
    trial = copy.deepcopy(cfg)
    trial["pile"]["L"] = L
    assert PileAnalysis(trial).run(with_length=False)["utilisation"] <= 1.0


def test_no_length_is_reported_as_such():
    cfg = one_layer(cu=5.0)
    cfg["loading"]["Q"] = 50_000.0
    res = analyse(cfg).results
    assert math.isnan(res["required_length"])
    assert any(w[0] == "warn_no_length" for w in res["warnings"])


def test_a_group_settles_more_than_one_pile():
    st = analyse(DEFAULT_CONFIG).results["settlement"]
    assert st["vesic"] > st["single"]["s"]
    assert st["raft"]["total"] == pytest.approx(st["raft"]["s"] + st["raft"]["shortening"])
    assert st["raft"]["consolidation"] > 0 and st["raft"]["elastic"] > 0
    assert st["meyerhof"] is not None


def test_a_weaker_layer_under_the_tip_is_flagged():
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    cfg["pile"]["L"] = 12.5                    # tip at 14.0 m, stiff clay from 15 m
    res = analyse(cfg).results
    assert any(w[0] == "warn_weak_below" for w in res["warnings"])


@pytest.mark.parametrize("section, key, value, error", [
    ("pile", "D", 0.0, "err_dimensions"),
    ("pile", "L", 100.0, "err_tip_below"),
    ("pile", "top", -1.0, "err_top"),
    ("loading", "Q", 0.0, "err_load"),
    ("group", "sx", 0.3, "err_group_spacing"),
    ("group", "nx", 0, "err_group_count"),
])
def test_impossible_inputs_are_refused(section, key, value, error):
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    cfg[section][key] = value
    with pytest.raises(PileError) as caught:
        PileAnalysis(cfg)
    assert caught.value.key == error


def test_a_clay_without_cu_is_refused():
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    cfg["soil_profile"][1]["cu"] = 0.0
    with pytest.raises(PileError) as caught:
        PileAnalysis(cfg)
    assert caught.value.key == "err_cu"


def test_the_study_run_leaves_the_length_out():
    res = PileAnalysis(DEFAULT_CONFIG).run(with_length=False)
    assert res["length_curve"] == [] and math.isnan(res["required_length"])
