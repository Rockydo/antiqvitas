# M12 AD 1 country-history agendas

## Coverage

- Exact-name selector override: 157 unique roster/engine tags plus one ancient
  fallback.
- Localization: 157 nonempty contexts in all 11 clients; 61 Tier-1 entries name
  their polity directly.
- Source/confidence ledger: `docs/m12/country_history_agendas.csv`, inheriting
  each polity's reviewed roster source.
- Player-visible scan: zero Renaissance, feudal, gunpowder, colonial,
  absolutist, revolutionary, Enlightenment, rifle, Redcoat, or Grenzer terms.

## Rapid runtime probe

One mounted debug session opened Agenda and changed the player tag in place:

- `M12_country_history/rome_agenda.png`: Augustus, Principate, provinces,
  clients, legions, and succession.
- `M12_country_history/han_agenda.png`: Emperor Ping, Wang Mang, commanderies,
  grain, rivers, court, and frontier commands.
- `M12_country_history/parthia_agenda.png`: Arsacid court, noble houses,
  sub-kings, routes, and the Roman frontier.
- `M12_country_history/marcomanni_agenda.png`: Maroboduus, Bohemia, negotiated
  Germanic leadership, and Roman influence.
- `M12_country_history/atrebates_agenda.png`: the closest valid Belgic/Celtic
  playable probe. No independent Gallic tag exists in the AD 1 roster because
  Gaul is under Rome.
- `M12_country_history/kush_agenda.png`: Meroe, Nile agriculture, royal and
  temple institutions, exchange, and Roman Egypt.
- `M12_country_history/teotihuacan_agenda.png`: bounded Mesoamerican urban,
  agricultural, exchange, and water-management context.

The Oceanian tag attempted from the old AD 44 autosave was no longer present;
the American capture satisfies that acceptance branch. Static validation covers
all 157 AD 1 starts. No country-history or missing-localization error appeared.
The old save emitted unrelated installed HRE-action invalid-IO errors; the clean
smoke gate did not.

## Gates

- `make validate`: PASS (70/70).
- `make smoke`: PASS, zero new mod-only error lines.

Result: PASS.
