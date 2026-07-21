# M4/M10 Moche chronology correction

Date: 2026-07-21

The master plan requires Moche to form around AD 100. The prior AD 1 Moche
country and Andes-wide Moche population default therefore failed the campaign
chronology. This correction replaces that start tag with a contested
Gallinazo-community SoP at the existing Moche-Valley local-map proxy and uses
a generic, non-uniform Andean scaffold for residual AD 1 populations. Nazca,
Recuay, and early Tiwanaku receive their existing culture profiles rather than
the former Moche default.

The generated AD 100 historical current creates plural-labelled Moche Polities
through the installed `create_country_from_location` contract. Its retained
source/master/BC7 DDS illustration is an unpeopled North Coast river-valley
context, deliberately excluding rulers, flags, later Chan Chan, and a unitary
state claim. Sources and limits are recorded in `ASSUMPTIONS.md` and
`world_1ad/SOURCES.md` under PNAS-VIR, WIL-GAL, JSTOR-MOC, and CAM-MOC.

`make validate` passed: 157 start polities, 165 culture definitions, 19
second-century currents, 84 reviewed event masters, and 416 total M10/M11
source-window events. The enabled-mod smoke reached the rendered menu, held
the post-load dwell, and passed with zero new normalized `error.log` lines.
The established observer-advancement limitation remains documented in
`BLOCKERS.md`; no unchanged third driver retry was made.
