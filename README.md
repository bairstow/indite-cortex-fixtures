# indite-cortex-fixtures

Binary calibration and validation data for `indite-cortex-v2`. v2 pins a commit of this repository in its `fixtures.edn` and its tests read from a sibling checkout (`../indite-cortex-fixtures`, or the path in `INDITE_FIXTURES`).

## Layout

| Path | What |
|---|---|
| `calibration/<profile>/profile.edn` | Display, panel descriptors, click profile and thresholds for one display setup |
| `calibration/<profile>/templates/` | Empty-slot templates, panel landmarks, the stash tab pointer |
| `calibration/<profile>/gallery/<group>/` | Item-art gallery used for identity matching |
| `calibration/<profile>/digit-atlas/`, `digit-atlas-italic/` | Digit glyphs for stack and value reading |
| `calibration/<profile>/minimap/` | Minimap markers, HSV presets, minimap-to-screen projection |
| `validation/<set>/` | Recorded frames and text with ground-truth labels and v1 golden outputs |

The first profile is `lenovo-3440x1440`: a 3440×1440 ultrawide with Path of Exile fullscreen at the virtual-screen origin, transcribed from v1 at commit `f3354a4`.

## Rules

- Every directory has a `manifest.edn` listing its files, each file's role and its v1 source path. v2's tests check that every listed file exists.
- Files are added, never overwritten in place. A changed reference image gets a new name and the manifest points to it, so a pinned commit always means the same data.
- Text under `validation/text/` keeps its exact bytes (`.gitattributes` disables normalisation there): PoE's clipboard output mixes line endings.
- No secrets or personal data: no account config, cookies, or screenshots that show chat or account details.
