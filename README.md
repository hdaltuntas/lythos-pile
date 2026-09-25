**English** | [Türkçe](https://github.com/hdaltuntas/lythos-pile/blob/main/README.tr.md)

# Lythos Pile

[![Tests](https://github.com/hdaltuntas/lythos-pile/actions/workflows/tests.yml/badge.svg)](https://github.com/hdaltuntas/lythos-pile/actions/workflows/tests.yml)

Axial capacity, group action and settlement of piles in layered ground, and the length of a
rock socket, driven from your browser. A circular or square pile — bored, or driven with a
small or a large displacement — alone or in a rectangular group under a cap, is checked by
**every method an engineer is likely to be asked for**, side by side:

1. **Shaft friction** in clay by the **α methods** of API RP 2A, Kulhawy & Phoon and Sladen,
   the **β method** (Burland) and the **λ method** (Vijayvergiya & Focht); in sand by
   **K·σ′v·tan δ**, with Meyerhof's **critical depth**; and Meyerhof's **SPT** rule.
2. **Base resistance** by **Meyerhof**, **Vesić** (rigidity index) and **Janbu**; 9·cu,
   Vesić's and Janbu's Nc\* in clay; Meyerhof's SPT rule.
3. **The pile's weight** — buoyant below the **water table** — taken off the ultimate
   capacity: Qult,net = Qs + Qb − W, Qall = Qult,net / FS. All stresses are effective.
4. **Group action** — the efficiency of **Converse–Labarre**, **Los Angeles Group**,
   **Seiler–Keeney** and **Feld**, and **block failure**; the group capacity is the smaller.
5. **Required length** — the shortest pile that passes both the single-pile and the group
   check, with the capacity drawn against the length.
6. **Settlement** — a single pile by **Vesić**; the group by the **equivalent raft** at 2/3·L
   (clays consolidate with Cc, Cr, e0 and OCR, the rest compress elastically), by **Vesić's**
   √(Bg/D) rule and by **Meyerhof's** SPT rule.
7. **Rock-socketed piles**, on their own — the unit side shear of **twelve published
   correlations** (Rosenberg & Journeaux, Horvath & Kenney, Meigh & Wolski, Williams et al.,
   Reynolds & Kaderabek, Gupton & Logan, Rowe & Armitage, Carter & Kulhawy, Toh et al., Zhang
   & Einstein, O'Neill & Reese / AASHTO, Kulhawy et al.), the base resistance of six more, the
   **socket length each of them needs**, a design length from their mean, median, bounds or
   any one of them, and the **elastic settlement** of the socket by **Randolph & Wroth** (with
   and without the base) and by Vesić.

On top of it, a **parametric or reliability study** sweeps any input — a range, or a
distribution — and reports sensitivities and the probability that the pile, the group or
the settlement fails, with a confidence interval and the reliability index β.

The whole program — every label, result text, figure and report — is bilingual in
**English and Turkish**, switchable while it runs.

The interface is a small HTTP server on your own machine, driven from a browser. That
keeps the program usable over a remote session or inside a container, where a desktop
toolkit would need a display it does not have, and it costs no dependency beyond the
standard library.

> This is the sibling of [LythosFEA](https://github.com/hdaltuntas/lythos),
> [Lythos Bearing](https://github.com/hdaltuntas/lythos-bearing),
> [Lythos Settle](https://github.com/hdaltuntas/lythos-settle),
> [Lythos MSEW](https://github.com/hdaltuntas/lythos-msew),
> [Lythos Kinematic](https://github.com/hdaltuntas/lythoskinematic),
> [Lythos SPWA](https://github.com/hdaltuntas/lythosspwa) and
> [LythosLE](https://github.com/hdaltuntas/lythosle), and follows the same architecture,
> theme and fonts.

## Screenshots

| Pile group, summary | Rock socket, summary |
|---|---|
| ![Pile summary](https://raw.githubusercontent.com/hdaltuntas/lythos-pile/main/screenshots/pile_summary.png) | ![Socket summary](https://raw.githubusercontent.com/hdaltuntas/lythos-pile/main/screenshots/socket_summary.png) |

| Stresses and shaft friction, dark theme, Turkish | Capacity against length |
|---|---|
| ![Profile](https://raw.githubusercontent.com/hdaltuntas/lythos-pile/main/screenshots/pile_profile_dark_tr.png) | ![Length](https://raw.githubusercontent.com/hdaltuntas/lythos-pile/main/screenshots/pile_length.png) |

| Group plan and efficiency | Socket length by correlation |
|---|---|
| ![Group](https://raw.githubusercontent.com/hdaltuntas/lythos-pile/main/screenshots/pile_group.png) | ![Socket](https://raw.githubusercontent.com/hdaltuntas/lythos-pile/main/screenshots/socket_length.png) |

## Install & run

```bash
pip install numpy matplotlib reportlab
python main.py                     # opens the interface in your browser
```

or install the clone itself with `pip install .` and run `lythos-pile`. Word reports need
`python-docx` and the spreadsheet export of a study needs `openpyxl`; both are extras:
`pip install ".[docx,xlsx]"`. Python 3.10+ is required. `main.py` puts its own directory
first on the import path, so the clone's code is what runs even when `lythospile` is also
installed.

## Command line

```bash
lythos-pile                                   # web interface (the default)
lythos-pile web --port 9000 --lang tr --no-browser
lythos-pile example -o project.pile           # a starter project file
lythos-pile run project.pile -o report.pdf    # the pile and its group, and a report
lythos-pile run project.pile --socket -o report.pdf   # … with the rock socket as well
lythos-pile socket project.pile -o socket.pdf # the rock socket alone
lythos-pile study project.pile -o samples.csv
```

`run`, `socket` and `study` read the same `.pile` file the interface saves, so a case set
up in the browser can be re-run unattended. The interface listens on port 8783 by default.

## Inputs

* **Pile:** circular or square, D, L, depth of the pile head (underside of the cap),
  installation (bored / CFA, driven with a small or a large displacement), γp, Ep.
* **Load:** the vertical load on the group at the underside of the cap.
* **Group:** piles along B and L, spacings, the efficiency method, block failure on / off
  (1 × 1 is a single pile).
* **Groundwater:** depth of the water table, γw.
* **Soil profile**, from the surface down, one row per layer: thickness, granular or cohesive,
  γ, γsat, φ′, cu, OCR, N60, E, ν, Cc, Cr, e0.
* **Methods:** the clay method, the base method, K/K0 and δ/φ′ in sand, the critical depth,
  Janbu's η′, Sladen's C, the SPT rule; the pile weight subtracted and buoyant or not.
* **Settlement:** the group method for the check, the depth of the equivalent raft, the load
  spread, the distribution of the shaft friction.
* **Criteria:** factor of safety, allowable settlement, the length search.
* **Rock socket:** socket diameter and length, pile head and rock surface depths, the load;
  qu, the rock mass modulus (from RQD, from GSI, or entered), GSI, mi, D, ν, the modulus
  below the base, joint spacing and aperture; f′c, Ec, the unit weight of the concrete; the
  design statistic, the design base resistance, the two factors of safety, the minimum
  length and the weak rock limit.

## What it computes

| quantity | method |
|---|---|
| stresses | σv0, u0 (hydrostatic below the water table), σ′v0, layer by layer |
| shaft friction, clay | α: API RP 2A 0.5ψ^-0.5 / 0.5ψ^-0.25; Kulhawy & Phoon 0.21 + 0.26·pa/cu; Sladen C·(σ′v/cu)^0.45 · β: (1 − sin φ′)·tan φ′·√OCR · λ: λ·(σ′v + 2cu) |
| shaft friction, sand | K·σ′v·tan δ, K = (K/K0)·(1 − sin φ′); σ′v constant below zc = 15·D (on request) |
| base, sand | Meyerhof σ′v·Nq\* ≤ 0.5·pa·Nq\*·tan φ′; Vesić σ′v·Nq\*(Irr); Janbu σ′v·Nq\*(η′) |
| base, clay | 9·cu; Vesić 4/3·(ln Ir + 1) + π/2 + 1; Janbu 2 + 2η′ |
| SPT | Meyerhof: fs = 0.01–0.02·pa·N60, qb = 0.4·pa·N60·Lb/D ≤ 4·pa·N60 |
| weight | W = γp·Ab·L, γp − γw below the water table; Qult,net = Qs + Qb − W |
| group | Converse–Labarre, Los Angeles, Seiler–Keeney, Feld; block failure (Skempton's Nc in clay) |
| required length | the shortest pile that passes the single-pile and the group check |
| settlement, pile | Vesić: s1 + s2 + s3 |
| settlement, group | equivalent raft at 2/3·L, 2 : 1, consolidation / elastic; Vesić s·√(Bg/D); Meyerhof SPT |
| rock socket, side | twelve correlations; qu ≤ f′c; the weak rock rules left out above a limit |
| rock socket, base | Coates, Rowe & Armitage, Carter & Kulhawy (Hoek–Brown), Zhang & Einstein, AASHTO, CFEM |
| socket length | Qs/FSside + Qb/FSbase − W = Q, by bisection, per correlation and for the design |
| socket settlement | Randolph & Wroth with and without the base; Vesić; plus the overburden's shortening |

The expressions, their sources and their limits are in
[docs/theory.md](https://github.com/hdaltuntas/lythos-pile/blob/main/docs/theory.md).

## Figures

Section through the group with the critical depth and the equivalent raft · σ′v, u0, the
unit shaft friction of every method and the load down the shaft · shaft and base resistance
by method · capacity against length with the required length · plan of the group and the
efficiency of every method · the stresses under the raft and the settlement by method.
Rock socket: section · side shear by correlation · socket length by correlation · head
settlement against socket length. Study figures: one-at-a-time sweep, histogram, scatter,
tornado.

## Reports

Choose PDF, self-contained HTML or Word in the header and press *Export report…*. The
report carries whatever has been analysed — the pile and its group, the rock socket, the
study — with the inputs, every method's result, the checks, the required length, the
figures, the warnings and the method notes, in whichever language the interface is in. All
three formats are assembled from one place, so they say the same thing.

## Project files (`.pile`)

JSON. *Save* writes the inputs, the rock socket and the study definition; *Open…* reads them
back. Missing entries keep their defaults.

## Modules

| file | content |
|---|---|
| `lythospile/profile.py` | The layered column and its stresses, slices and averages |
| `lythospile/axial.py` | Unit shaft friction and base resistance, per method |
| `lythospile/group.py` | Group layout, efficiencies, Skempton's Nc of the block |
| `lythospile/settlement.py` | Vesić's single-pile settlement, the equivalent raft, the group rules |
| `lythospile/socket.py` | Rock sockets: correlations, base, length, Randolph & Wroth |
| `lythospile/engine.py` | The pile analysis: shaft, base, weight, group, settlement, length |
| `lythospile/study.py`, `study_plots.py` | Parametric and reliability studies, P of failure with 95 % CI and β, Spearman sensitivities, CSV / XLSX |
| `lythospile/plotting.py`, `plot_style.py`, `render.py` | Matplotlib figures, theme-aware, off-screen |
| `lythospile/report.py`, `pdf.py` | Calculation report: one HTML assembly, exported as PDF, HTML or DOCX |
| `lythospile/forms.py` | Input schema and readers, with the conditions under which each field applies |
| `lythospile/summary.py` | The results as cards and as text, for the browser and the command line alike |
| `lythospile/i18n.py` | Every text, English and Turkish, written side by side |
| `lythospile/web/` | The local HTTP server, the session, and the browser interface |

## Development

```bash
pip install -e ".[dev]"
pytest -q                 # formulas by hand, engine, socket, group, settlement, study, report, web, packaging
ruff check .
```

The tests check every formula against a hand calculation (the α, β and λ methods, Meyerhof's
table and limit, Vesić's and Janbu's factors, the four efficiencies, Feld's count, Vesić's
settlement term by term, the consolidation of a clay, the equivalent raft, each of the
twelve socket correlations and the six base methods, Randolph & Wroth's rigid limits), the
engine on simple cases worked by hand (a clay pile, a sand pile, the weight, the water
table, a block failure, the required length), the refusals, the report in all three
formats, the input schema and its round trips, and the interface itself — the session and
the HTTP layer both, so the browser is exercised without a browser.

Releasing to PyPI is described in [docs/releasing.md](https://github.com/hdaltuntas/lythos-pile/blob/main/docs/releasing.md);
`tools/upload_to_pypi.py` does it from an editor, without a terminal.

## License

Copyright © 2026 Hasan Deniz Altuntaş

Lythos Pile is free software: you can redistribute it and/or modify it under the terms of the
[GNU Affero General Public License, version 3](https://github.com/hdaltuntas/lythos-pile/blob/main/LICENSE) as published by the Free Software
Foundation. It is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

Whoever runs a modified version for users over a network must offer them the source of that
version (section 13 of the licence). Versions published before this change were released
under the MIT licence and remain available under it.
