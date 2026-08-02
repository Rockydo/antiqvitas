# Public release privacy audit

Date: 2026-08-02

## Scope

- All advertised branches, milestone tags, commit/tag identities, current tracked
  files, generated manifests, and unique reachable historical blobs.
- Ignored runtime configuration and both sanitized local stash entries were checked
  separately; stashes are not published.

## Remediation

- Replaced private author/committer/tagger metadata with the repository's GitHub
  noreply identity across reachable history.
- Removed `config/local_paths.json` from history; retained only the tokenized
  `config/local_paths.example.json` and ignored runtime file.
- Replaced machine-local repository, game, user-data, Documents, and Steam-library
  values in historical text while preserving the current tree byte-for-byte.
- Rewrote every production branch and milestone tag behind exact remote leases;
  deleted all temporary transfer refs and pruned the pre-rewrite local graph.

## Proof

- Rewritten current tree: unchanged tree object before and after sanitation.
- Independent network mirror: complete; `git fsck --full --no-reflogs` passes.
- Deep guard: `PASS (11282 tracked files and reachable object history; no local
  identity/path leakage)`.
- Full repository validation: `PASS` (159/159 commands).
- Public refs: main, two retained audit branches, and M0-M12 tags only; no temporary
  transfer ref remains.
- Local preservation: two rewritten stash entries remain; all three sampled old
  production tips are absent after targeted reflog expiry and reachability repack.

## Permanent gate

`make validate` runs the current-tree and identity guard. Before any public release,
also run:

```text
python tools/public_release_guard.py --history
```
