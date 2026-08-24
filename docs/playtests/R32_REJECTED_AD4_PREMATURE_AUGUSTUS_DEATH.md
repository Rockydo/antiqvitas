# R32 rejected at AD 4: premature death of Augustus

R32 was a fresh, non-debug Rome campaign at 1920x1080. It began from the
twice-smoked build fingerprint
`0c377e249a8536493a4c6d98dd2d15a550732b9313ad8960468687868e5117dc`.

The AD 1 character menu confirmed the preceding quarantine and marriage-label
fixes. The campaign then ran at maximum speed with live log monitoring. Its
1 January AD 4 autosave passed the strict runtime audit and still contained the
intended living Augustus, Gaius Caesar, Livia, and Tiberius character records.
By 19 May AD 4, however, Augustus's character panel showed him dead and Rome
had a replacement ruler. The run was therefore rejected immediately; none of
its later evidence can satisfy the final production gate.

The failure coincided with the historical Gaius Caesar transition window that
opens on 21 February AD 4. The generated `antq_m6.2` event removed Gaius's
lifespan guard through his stored character variable, but then passed that
variable directly to `kill_character_silently`. Installed engine scripts pass
saved character scopes to this effect and contain no `var:` target examples.
At runtime the invalid target killed Rome's current ruler, Augustus.

The owning M6 generator now resolves each persisted character variable into a
saved character scope before using `kill_character_silently`,
`set_as_designated_heir`, or ruler-replacement effects. The same unsupported
target pattern was corrected in the contingent AD 9 Varus event. Generator
validation rejects any recurrence of variable targets on these character
effects, and a repository-wide audit contains no remaining occurrence.

Evidence retained from the rejected run:

- `docs/screens/R32_FINAL_PRODUCTION_ROME_AD1_100/R32_AD1_corrected_character_menu.png`
- `docs/screens/R32_FINAL_PRODUCTION_ROME_AD1_100/R32_checkpoint1_paused.png`
- `docs/playtests/R32_CHECKPOINT_AD4.json`
- `G:/antiqvitas_user_data/save games/autosave_7b98ada2-f308-4e53-a3d0-f20e7fba555f.eu5`

The corrected build requires a completely fresh AD 1 campaign. R32 is not
restart evidence and cannot contribute elapsed years to the final AD 100 gate.
