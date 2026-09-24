"""Parametric and reliability studies."""
import copy
import math

import numpy as np
import pytest

from lythospile import study as S
from lythospile import study_plots
from lythospile.config import DEFAULT_CONFIG
from lythospile.i18n import TRANSLATIONS


def variable(path="soil_profile.1.cu", **kw):
    spec = {"path": path, "label": path, "mode": "dist", "dist": "normal", "mean": 35.0,
            "cov": 0.1, "n_points": 5}
    spec.update(kw)
    return S.StudyVariable.from_dict(spec)


def test_paths_read_and_write_the_configuration():
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    assert S.get_value(cfg, "soil_profile.1.cu") == 35.0
    S.set_value(cfg, "loading.Q", 999.0)
    assert cfg["loading"]["Q"] == 999.0


def test_the_spacing_is_offered_only_along_a_row_of_piles():
    cfg = copy.deepcopy(DEFAULT_CONFIG)
    cfg["group"].update(nx=3, ny=1)
    paths = [p for p, _ in S.available_variables(cfg)]
    assert "group.sx" in paths and "group.sy" not in paths


def test_a_one_at_a_time_sweep_varies_one_input_per_row():
    rows = S.sample([variable(mode="range", min=20, max=28, n_points=5),
                     variable("loading.Q", mode="range", min=1000, max=2000, n_points=3)],
                    "oat")
    assert len(rows) == 8
    assert {row["_swept"] for row in rows} == {"soil_profile.1.cu", "loading.Q"}


def test_a_latin_hypercube_fills_every_stratum_once():
    rows = S.sample([variable(mode="range", min=0.0, max=1.0)], "lhs", n=50, seed=3)
    values = sorted(row["soil_profile.1.cu"] for row in rows)
    strata = [int(v * 50) for v in values]
    assert strata == list(range(50))


def test_the_lognormal_draw_has_the_mean_and_spread_asked_for():
    v = variable(dist="lognormal", mean=100.0, cov=0.2)
    u = (np.arange(20000) + 0.5) / 20000
    draws = v.draw(u)
    assert draws.mean() == pytest.approx(100.0, rel=0.01)
    assert draws.std() == pytest.approx(20.0, rel=0.03)


def test_the_same_seed_gives_the_same_study():
    a = S.sample([variable()], "mc", n=20, seed=11)
    b = S.sample([variable()], "mc", n=20, seed=11)
    assert a == b


def test_an_impossible_sample_is_recorded_not_fatal():
    row = S.evaluate(DEFAULT_CONFIG, {"loading.Q": -5.0})
    assert row["error"]
    assert math.isnan(row["FS"])


@pytest.fixture(scope="module")
def reliability_study():
    return S.Study(DEFAULT_CONFIG, [variable("soil_profile.4.phi", mean=36.0, cov=0.08),
                                    variable("loading.Q", dist="lognormal",
                                             mean=10000.0, cov=0.25)],
                   "lhs", 120, seed=5).run()


def test_a_study_reports_statistics_sensitivities_and_probabilities(reliability_study):
    s = reliability_study.summary
    assert s["n_ok"] == 120
    assert set(s["stats"]) >= {"Q_ult", "FS", "utilisation", "settlement"}
    rho = s["spearman"]["FS"]
    assert rho["soil_profile.4.phi"] > 0.2        # a stronger sand at the tip, a safer pile
    assert rho["loading.Q"] < -0.3                # a heavier load, a less safe one
    settle = s["reliability"]["ls_settlement"]
    assert 0 < settle["pf"] < 1
    assert settle["pf_lo"] <= settle["pf"] <= settle["pf_hi"]


def test_the_wilson_interval_behaves_when_nothing_fails():
    got = S.reliability(np.array([0.5] * 100), 1.0)
    assert got["pf"] == 0.0 and got["pf_hi"] > 0 and got["beta"] == float("inf")


def test_failure_can_be_counted_below_the_capacity():
    got = S.reliability(np.array([1.0, 2.0, 3.0, 4.0]), 2.5, failure_above=False)
    assert got["n_fail"] == 2


def test_the_samples_export(tmp_path, reliability_study):
    S.to_csv(reliability_study, tmp_path / "s.csv")
    lines = (tmp_path / "s.csv").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 121
    S.to_xlsx(reliability_study, tmp_path / "s.xlsx")
    assert (tmp_path / "s.xlsx").stat().st_size > 1000


def test_the_study_text_is_complete(reliability_study):
    text = study_plots.summary_text(reliability_study, TRANSLATIONS["en"])
    assert "STUDY RESULTS" in text and "Latin hypercube" in text
    assert "Settlement" in text
