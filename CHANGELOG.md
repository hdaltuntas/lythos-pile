# Changelog

## Unreleased

- The licence changes from MIT to the GNU Affero General Public License, version 3
  (`AGPL-3.0-only`). Versions already published keep the MIT licence they were released under.

## 0.1.0

First release: axial capacity, group action and settlement of piles, and rock sockets,
built on the architecture of the other Lythos programs (local HTTP server + browser
interface, schema-driven forms, the same theme and fonts, bilingual English / Turkish
throughout, PDF / HTML / DOCX reports, `.pile` project files, command line, parametric /
reliability studies).

- Layered ground with a water table; effective stresses down the shaft.
- Shaft friction: α methods (API RP 2A, Kulhawy & Phoon, Sladen), β method (Burland) and λ
  method (Vijayvergiya & Focht) in clay; K·σ′v·tan δ in sand, K from the installation, with
  Meyerhof's critical depth; Meyerhof's SPT rule.
- Base resistance: Meyerhof (with its limit), Vesić (rigidity index), Janbu; 9·cu and
  Vesić's and Janbu's Nc\* in clay; Meyerhof's SPT rule. Every shaft method against every
  base method in one table.
- The pile's weight, buoyant below the water table, taken off: Qult,net = Qs + Qb − W.
- Groups: Converse–Labarre, Los Angeles Group, Seiler–Keeney and Feld efficiencies, block
  failure; the group capacity is the smaller.
- The required pile length, and the capacity against length.
- Settlement: a single pile by Vesić; the group by the equivalent raft (consolidation and
  elastic compression), Vesić's √(Bg/D) rule and Meyerhof's SPT rule.
- Rock sockets: twelve side shear correlations, six base methods, the socket length each
  correlation needs and a design length, the rock mass modulus from RQD or GSI, and the
  elastic settlement by Randolph & Wroth and by Vesić.
- Figures: section, stresses and shaft friction with depth, methods, capacity against
  length, group plan and efficiency, settlement; socket section, side shear, socket length,
  settlement against socket length.
- Studies: one-at-a-time, Latin hypercube, Monte Carlo; statistics, probability of failure
  of the pile, the group and the settlement with 95 % CI and β, Spearman sensitivities,
  CSV / XLSX export.
