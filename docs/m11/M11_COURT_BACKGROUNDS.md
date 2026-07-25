# M11 ancient character scenes

`character_scene` resolves the installed `throne_room` illustration tag.
`in_game/gfx/images/zzz_antq_throne_rooms.txt` adds eleven culture families at
priorities 300-400 and an unconditional ancient fallback at 100; the highest
installed base/DLC priority is 52.

The three four-up source sheets were generated with the built-in image pipeline.
Every request included the actual 15-image EU5 throne-room atlas at
`assets_queue/court_backgrounds/references/vanilla_throne_rooms_contact.png`.
Prompts required text-free, unoccupied, period-material interiors with the EU5
camera, painterly realism, open lower centre, restrained colour, and no yellow
filter. Sheet subjects were:

- Roman / Hellenistic / Celtic / Germanic
- Iranian-steppe / Indic / Han-East Asian / Near Eastern
- African / American / Oceanian / neutral ancient fallback

`tools/m11_court_backgrounds.py --write` crops the reviewed quadrants, creates
1080x440 PNG masters and mipmapped DXT5 DDS textures, and writes the resolver.
`--check` validates the source/master/DDS chain, resolver priorities, graphical
culture uniqueness, and perceptual uniqueness. Historical basis is row-sourced
in `docs/art/court_backgrounds.csv`; the combined review image is
`assets_queue/court_backgrounds/court_backgrounds_contact.png`.
