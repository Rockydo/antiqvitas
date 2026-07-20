# M5 Melos alum anchor

## Evidence

The plan includes alum among the ancient goods to retain and emphasize. The
reviewed *Journal of Roman Studies* synthesis identifies Melos as an ancient
alum and sulphur island, reports a dramatic Roman-period increase in mineral
extraction and processing sites, and places Italian-controlled alum systems
across the first through third centuries AD. Its export evidence reaches back
to the last decades of the first century BC, securely covering the AD 1 start.
It does not quantify output at a particular mine or establish the ownership of
every extraction cluster on 1 January.

## Engine representation

The installed `milos` location is the direct island match and already uses the
installed vanilla `alum` good. M5 adds a secure source-qualified anchor to the
RGO ledger without changing that correct raw-material value. This retains a
reviewable antiquity rationale for an existing game surface while avoiding an
invented production volume or a new good.

## Verification

`tools/generate_rgo_remap.py --write` retains the unchanged `milos = alum`
template entry and the 328 independently altered RGO corrections. `make
validate` passed. The runtime-effect limitation for map-template RGO data
remains separately documented in `BLOCKERS.md`.

Sources: `CAM-MELOS-ALUM`; P12.1.
