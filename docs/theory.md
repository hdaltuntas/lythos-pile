# Lythos Pile — theory

What the program computes, how, and where each expression comes from. Symbols: D the pile
diameter (or side), L its length below the pile head, Ab the base area, p the perimeter, σ′v
the vertical effective stress, cu the undrained shear strength, φ′ the effective friction
angle, pa = 101.325 kPa the atmospheric pressure. Stresses in kPa, forces in kN.

## 1. Stresses

The profile is a stack of layers from the ground surface down; the last one continues below
the profile where a stress is asked for deeper. σv0 = Σ γ·h above the water table and
Σ γsat·h below it; u0 = γw·(z − zw) below the water table; σ′v0 = σv0 − u0. The shaft is cut
into slices no thicker than 0.25 m that never straddle a layer boundary, and every
integral below is the midpoint sum over them.

## 2. Shaft friction

    Qs = Σ fs·p·Δz

### Granular layers

    fs = K·σ′v·tan δ,  K = (K/K0)·K0,  K0 = 1 − sin φ′,  δ = (δ/φ′)·φ′

K/K0 is 1.0 for a bored pile, 1.2 for a driven pile with a small displacement and 1.4 for
one with a large displacement, unless entered (the middle of Das's ranges K0, K0–1.4·K0 and
K0–1.8·K0). With the critical depth switched on, σ′v in sand is held at its value at
zc = (zc/D)·D below the ground surface (Meyerhof 1976; Vesić 1967), 15·D by default.

### Cohesive layers

| method | fs |
|---|---|
| API RP 2A (1987) | α·cu, α = 0.5·ψ^-0.5 (ψ ≤ 1), 0.5·ψ^-0.25 (ψ > 1), ψ = cu/σ′v, α ≤ 1 |
| Kulhawy & Phoon (1993) | α·cu, α = 0.21 + 0.26·pa/cu ≤ 1 (drilled shafts) |
| Sladen (1992) | α·cu, α = C·(σ′v/cu)^0.45 ≤ 1, C = 0.4 bored, 0.5 driven |
| β — Burland (1973), Meyerhof (1976) | (1 − sin φ′)·tan φ′·√OCR·σ′v |
| λ — Vijayvergiya & Focht (1972) | λ·(σ′v + 2cu), λ from the pile's penetration |

The λ table runs from 0.5 at the surface to 0.110 below 70 m (Das). Applied slice by slice
it gives λ·(σ̄′v + 2c̄u) over the clay, the original form.

### SPT (Meyerhof 1976)

fs = 0.02·pa·N60 for a large displacement pile, 0.01·pa·N60 otherwise; clay slices keep the
chosen clay method. It is derived for driven piles, and shown beside the others.

## 3. Base resistance

    Qb = qb·Ab

The tip is in the layer at its depth (the one below, if it sits on a boundary). A weaker
layer within 3·D below it is reported.

### Sand

* **Meyerhof (1976):** qb = σ′v·Nq\* ≤ ql = 0.5·pa·Nq\*·tan φ′, Nq\* from Das's table of
  Meyerhof's values (12.4 at 20°, 56.7 at 30°, 346 at 40°), interpolated logarithmically.
* **Vesić (1977):** qb = σ′o·Nσ\* = σ′v·Nq\*,
  Nq\* = 3/(3 − sin φ′)·e^((π/2 − φ′)tan φ′)·tan²(45 + φ′/2)·Irr^(4 sin φ′/(3(1 + sin φ′))),
  Ir = Es/(2(1 + ν)·σ′v·tan φ′), Irr = Ir/(1 + Ir·Δ), Δ = 0.005·(1 − (φ′ − 25)/20)·σ′v/pa.
* **Janbu (1976):** qb = σ′v·Nq\*, Nq\* = (tan φ′ + √(1 + tan² φ′))²·e^(2η′·tan φ′),
  η′ from 60° (soft) to 105° (dense), 90° by default.

σ′v at the tip is the capped one when the critical depth is on.

### Clay (undrained, net of the overburden)

* Skempton / Meyerhof: qb = 9·cu
* Vesić: qb = Nc\*·cu, Nc\* = 4/3·(ln Ir + 1) + π/2 + 1, Ir = Es/(3·cu)
* Janbu at φ = 0: Nc\* = lim (Nq\* − 1)·cot φ = 2 + 2η′ (5.14 at η′ = 90°)

The overburden term q·Nq = q is left out, as is customary, because it is balanced by the
pile's own weight; the weight is still subtracted if asked (conservative).

### SPT (Meyerhof 1976)

qb = 0.4·pa·N60·Lb/D ≤ 4·pa·N60, Lb the embedment in the bearing layer.

## 4. Weight, capacity and the check

    W = Ab·[γp·(length above the water table) + (γp − γw)·(length below it)]
    Qult = Qs + Qb,  Qult,net = Qult − W,  Qall = Qult,net / FS

The buoyant weight is used on request (the default); the weight is taken off on request
(the default). The load per pile is Q/n; the pile passes when Q/n ≤ Qall. Every combination
of a shaft method with a base method is reported, and the chosen pair makes the checks.

## 5. Groups

A rectangular group of n1 × n2 piles at spacings sx and sy (s is their mean where both
matter), outline Bg × Lg = [(n1 − 1)sx + D] × [(n2 − 1)sy + D].

| method | η |
|---|---|
| Converse–Labarre | 1 − θ·[(n1 − 1)n2 + (n2 − 1)n1]/(90·n1·n2), θ = arctan(D/s) [°] |
| Los Angeles Group | 1 − D/(π·s·n1·n2)·[n1(n2 − 1) + n2(n1 − 1) + √2(n1 − 1)(n2 − 1)] |
| Seiler–Keeney | 1 − [36s/(75s² − 7)]·(n1 + n2 − 2)/(n1 + n2 − 1) + 0.3/(n1 + n2), s in m |
| Feld | 1 − (number of neighbours, straight and diagonal)/16, averaged over the group |

Each η is capped at 1. **Block failure** takes the group as one block: shaft
2(Bg + Lg)·Σ fs·Δz with fs = cu in clay and K0·σ′v·tan φ′ in sand (soil on soil), base
Bg·Lg·qb with qb = Nc·cu, Nc = 5(1 + 0.2Bg/Lg)(1 + 0.2·z/Bg), z/Bg ≤ 2.5 (Skempton) in clay
and the chosen method's unit base resistance in sand.

    Qg,ult = min(η·n·Qult, Qblock),  Qg,all = (Qg,ult − n·W)/FS,  Q ≤ Qg,all

## 6. Required length

The analysis is repeated for L from the shortest length tried to the foot of the profile, in
the chosen step, every other input held as it is; the required length is the first that
passes both the single-pile and the group check. The capacity against length is drawn from
the same run.

## 7. Settlement

### Single pile — Vesić (1977), as set out by Das

    s1 = (Qwb + ξ·Qws)·L/(Ab·Ep)
    s2 = qwb·D·(1 − ν²)·0.85/Es(tip)
    s3 = Qws/(p·L)·D·(1 − ν²)·(2 + 0.35·√(L/D))/Es(shaft)

ξ = 0.5 for a uniform or parabolic friction, 0.67 triangular. The working load Q/n is shared
between shaft and base in the proportion of Qs and Qb.

### Group

* **Equivalent raft** (Terzaghi & Peck; Tomlinson): the load Q acts on Bg × Lg at
  z = head + (2/3)·L and spreads 2 : 1, Δσ = Q/[(Bg + Δz/2)(Lg + Δz/2)]. Below it, slices
  down to the foot of the profile or to where Δσ < 0.1·σ′v0. A clay with Cc consolidates:
  Cr/(1 + e0)·log(σ′f/σ′0) while σ′f ≤ σ′p = OCR·σ′0, Cr·log(σ′p/σ′0) + Cc·log(σ′f/σ′p)
  above; everything else compresses by Δσ·h/M, M = E(1 − ν)/((1 + ν)(1 − 2ν)). The piles'
  shortening above the raft, (Q/n)·(2/3)L/(Ab·Ep), is added.
* **Vesić (1969):** sg = s·√(Bg/D).
* **Meyerhof (1976), sand:** sg [mm] = 0.96·q·√Bg·I/N60, q = Q/(Bg·Lg), I = 1 − L/(8Bg) ≥ 0.5,
  N60 the mean within Bg below the tip.

## 8. Rock-socketed piles

The socket is analysed on its own: the load Q on one pile, the pile head at `top`, the rock
surface at `rock_depth`, a socket of length Ls and diameter D. The friction of the overburden
is ignored; its share of the pile's weight is not.

### Unit side shear

qu in the correlations is min(qu,rock, f′c): the bond is no stronger than the weaker of the
two materials.

| correlation | fs [MPa] |
|---|---|
| Rosenberg & Journeaux (1976) | 0.375·qu^0.515 |
| Horvath & Kenney (1979) | 0.21·qu^0.5 |
| Meigh & Wolski (1979) | 0.22·qu^0.6 |
| Williams, Johnston & Donald (1980) | 0.44·qu^0.36 |
| Reynolds & Kaderabek (1980) | 0.30·qu (weak rock) |
| Gupton & Logan (1984) | 0.20·qu (weak rock) |
| Rowe & Armitage (1987) | 0.45·qu^0.5 |
| Carter & Kulhawy (1988) | 0.20·qu^0.5 (= 0.63·pa·√(qu/pa)) |
| Toh et al. (1989) | 0.25·qu (weak rock) |
| Zhang & Einstein (1998) | 0.40·qu^0.5 (smooth sockets; 0.8 for rough) |
| O'Neill & Reese (1999), AASHTO LRFD | 0.65·αE·pa·(qu/pa)^0.5 ≤ 7.8·pa·(f′c/pa)^0.5 |
| Kulhawy, Prakoso & Akbas (2005) | 1.0·pa·(qu/pa)^0.5 |

The three linear rules were fitted to weak rock. Above the weak rock limit (5 MPa by
default) they are still listed, marked, but left out of the statistics. αE is O'Neill &
Reese's joint modification factor, 1.0 at Em/Ei = 1, 0.8 at 0.5, 0.7 at 0.3, 0.55 at 0.1 and
0.45 at 0.05 and below.

### Unit base resistance

| method | qb [MPa] |
|---|---|
| Coates (1967) | 3·qu |
| Rowe & Armitage (1987) | 2.7·qu |
| Carter & Kulhawy (1988) | [√s + √(m√s + s)]·qu, m and s of the Hoek–Brown mass (2002) |
| Zhang & Einstein (1998) | 4.83·qu^0.51 |
| AASHTO / O'Neill & Reese | 2.5·qu (intact or tightly jointed rock below the base) |
| CFEM, Ladanyi & Roy (1971) | 3·Ksp·d·qu, Ksp = (3 + c/D)/(10√(1 + 300δ/c)), d = 1 + 0.4·Ls/D ≤ 3 |

The CFEM rule gives an allowable pressure with a factor of about 3, so it is multiplied by 3
here; it holds for 0.05 < c/D < 2 and δ/c < 0.02. The design base resistance is none, the
lowest, the mean, or one method. A base resistance above f′c is flagged.

### Socket length

    Qall(Ls) = π·D·Ls·fs/FSside + Ab·qb/FSbase − W(Ls) = Q

is solved by bisection for every correlation and for the design side shear (the mean,
median, lowest or highest of the correlations in range, or one by name). The design length
is at least (min Ls/D)·D. The socket at the length entered (or at the design length when 0
is entered) is checked and its settlement worked out.

### Rock mass modulus

Em = Ei·(0.0231·RQD − 1.32), at least 0.15·Ei (Gardner 1987); or
Em = Ei·[0.02 + (1 − D/2)/(1 + e^((60 + 15D − GSI)/11))] (Hoek & Diederichs 2006); or entered.

### Elastic settlement

Randolph & Wroth (1978), for a compressible pile of radius r0 and length Ls in an elastic
medium of shear modulus G = Em/(2(1 + ν)) along the socket and Gb below the base:

    Pt/(G·r0·wt) = [4η/((1 − ν)ξ) + (2πρ/ζ)·(tanh μL/μL)·(L/r0)]
                   / [1 + (1/(πλ))·(4η/((1 − ν)ξ))·(tanh μL/μL)·(L/r0)]

ξ = G/Gb, λ = Ec/G, ρ = 1, η = 1, ζ = ln(rm/r0), rm = {0.25 + ξ[2.5ρ(1 − ν) − 0.25]}·L (kept
at 2·r0 or more), μL = √(2/(ζλ))·(L/r0). The share of the load reaching the base is
(4η/((1 − ν)ξ))/[cosh μL·(4η/((1 − ν)ξ) + (2πρ/ζ)(tanh μL/μL)(L/r0))]. The side-only
variant drops the base term. Vesić's three-part expression of §7 is given beside it, with
Em for the soil. The elastic shortening of the pile through the overburden, Q·Lo/(Ab·Ec), is
added to each.

## 9. Studies

As in the other Lythos programs: one-at-a-time sweeps, Latin hypercube or Monte Carlo
sampling of any input by a range or by a normal, lognormal or uniform distribution; every
sample is a whole pile analysis without the length search. The probability of failure of
the single pile (Q/n > Qall), of the group (Q > Qg,all) and of the settlement (s > sallow)
comes with Wilson's 95 % interval and the reliability index β = −Φ⁻¹(P).

## References

API (1987, 2000) RP 2A, *Recommended practice for planning, designing and constructing fixed
offshore platforms*. · Burland, J.B. (1973) Shaft friction of piles in clay. *Ground
Engineering* 6(3). · Carter, J.P. & Kulhawy, F.H. (1988) *Analysis and design of drilled
shaft foundations socketed into rock*, EPRI EL-5918. · Coates, D.F. (1967) *Rock mechanics
principles*, Mines Branch Monograph 874. · Converse, F.J. (1962), Labarre formula, in Moorhouse
& Sheehan. · Das, B.M. *Principles of Foundation Engineering*. · Feld, J. (1943) Discussion,
*Trans. ASCE* 108. · Gardner, W.S. (1987) Design of drilled piers in the Atlantic Piedmont,
ASCE GSP. · Gupton, C. & Logan, T. (1984) Design guidelines for drilled shafts in weak rocks of
South Florida. · Hoek, E., Carranza-Torres, C. & Corkum, B. (2002) Hoek–Brown failure
criterion, 2002 edition. · Hoek, E. & Diederichs, M.S. (2006) Empirical estimation of rock
mass modulus, *IJRMMS* 43. · Horvath, R.G. & Kenney, T.C. (1979) Shaft resistance of rock
socketed drilled piers, ASCE Symposium on Deep Foundations. · Janbu, N. (1976) Static bearing
capacity of friction piles, *Proc. 6th ECSMFE*. · Kulhawy, F.H. & Phoon, K.K. (1993) Drilled
shaft side resistance in clay soil to rock, ASCE GSP 38. · Kulhawy, F.H., Prakoso, W.A. &
Akbas, S.O. (2005) Evaluation of capacity of rock foundation sockets, *40th US Symp. Rock
Mech.* · Ladanyi, B. & Roy, A. (1971) Some aspects of bearing capacity of rock mass, *7th
Canadian Rock Mech. Symp.*; Canadian Foundation Engineering Manual. · Meigh, A.C. & Wolski, W.
(1979) Design parameters for weak rock, *7th ECSMFE*. · Meyerhof, G.G. (1976) Bearing capacity
and settlement of pile foundations, *JGED ASCE* 102(GT3). · O'Neill, M.W. & Reese, L.C. (1999)
*Drilled shafts: construction procedures and design methods*, FHWA-IF-99-025; AASHTO LRFD
Bridge Design Specifications §10.8. · Randolph, M.F. & Wroth, C.P. (1978) Analysis of
deformation of vertically loaded piles, *JGED ASCE* 104(GT12). · Reynolds, R.T. & Kaderabek,
T.J. (1980) Miami limestone foundation design and construction, ASCE. · Rosenberg, P. &
Journeaux, N.L. (1976) Friction and end bearing tests on bedrock for high capacity socket
design, *Can. Geotech. J.* 13. · Rowe, R.K. & Armitage, H.H. (1987) A design method for
drilled piers in soft rock, *Can. Geotech. J.* 24. · Seiler, J.F. & Keeney, W.D. (1944) The
efficiency of piles in groups, *Wood Preserving News* 22. · Skempton, A.W. (1951) The bearing
capacity of clays, *Building Research Congress*. · Sladen, J.A. (1992) The adhesion factor:
applications and limitations, *Can. Geotech. J.* 29. · Terzaghi, K. & Peck, R.B. (1967) *Soil
mechanics in engineering practice*. · Toh, C.T. et al. (1989) Design parameters for bored
piles in a weathered sedimentary formation, *12th ICSMFE*. · Tomlinson, M.J. *Pile design and
construction practice*. · Vesić, A.S. (1969, 1977) *Experiments with instrumented pile
groups in sand*, ASTM STP 444; *Design of pile foundations*, NCHRP Synthesis 42. ·
Vijayvergiya, V.N. & Focht, J.A. (1972) A new way to predict capacity of piles in clay, *OTC*.
· Williams, A.F., Johnston, I.W. & Donald, I.B. (1980) The design of socketed piles in weak
rock, *Int. Conf. Structural Foundations on Rock*. · Zhang, L. & Einstein, H.H. (1998) End
bearing capacity of drilled shafts in rock, *JGGE ASCE* 124(7).
