# Roman civic orders AD 1 adapter

The plan requires distinct Roman adapters for senators, equites, priesthoods,
plebs, and legions. The pre-existing senatorial, annona, and Praetorian
privileges cover the first, fourth, and the available military fallback. This
slice adds **Equestrian Service** and **Priestly Colleges** to the Roman
government profile.

The Oxford Classical Dictionary identifies equites as Rome's second
aristocratic order and a source of military officers and civil administrators
from the limited Augustan state. The Metropolitan Museum's Roman-religion
resource identifies public priestly colleges and Augustus's control of vacant
priestly nominations after the civil wars. These support bounded start-state
adapters (`OCD-EQU` and `MET-PRIEST` in the source ledger), not a personnel
list, an exact office hierarchy, a property-census reconstruction, or a full
Roman cult constitution.

EU5 exposes no safe Rome-only estate definition. The equestrian privilege
therefore uses the already validated `nobles_estate` bucket and the priesthood
privilege uses `clergy_estate`. These are deliberately technical mappings:
equites remain distinct from the senatorial privilege, and Roman public priests
are not classified as Christian clergy. Both use only locally harvested estate
power, satisfaction, and cabinet-efficiency contracts.
