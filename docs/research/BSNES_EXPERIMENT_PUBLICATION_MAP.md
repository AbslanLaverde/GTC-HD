# bsnes experiment source: historical and public identities

The [public bsnes research fork](https://github.com/AbslanLaverde/bsnes) provides sanitized publication equivalents of GTC-HD's experimental instrumentation and tests. Research questions, specifications, evidence and conclusions remain in GTC-HD-Lab. This is research code; bsnes has not been selected as the GTC-HD foundation, and these branches are neither production GTC-HD nor upstream bsnes releases.

## Why two commit identities are retained

**Historical implementation commits** identify the original research source. Dated reports also preserve earlier HEADs, uncommitted-source fingerprints and the precise context of each implementation/build/run. Historical executable hashes, captured outputs and ROM validation remain attached to those original commits/builds.

**Public research equivalents** preserve native experiment semantics while correcting author/committer identity, machine-specific test/tool paths, rewritten baseline pins and the EXP-004-P0 committed-tip reproduction policy. These corrections and changed parent IDs produce new commit SHAs. They do not mean that public rebuilds produced the historical evidence.

## Published branches and baseline comparisons

Branch tips were checked against these public commits on September 23, 2026. Branch links can move; exact commit and comparison links below identify the published revisions.

| Research source branch | Historical implementation | Public research equivalent | Public baseline comparison |
| --- | --- | --- | --- |
| [Runtime harness](https://github.com/AbslanLaverde/bsnes/tree/gtc-hd/exp-001-runtime-harness) | `906f74b6e5f4f2f4e62bb960d01aa68c9f55f919` | [ac488fe85289642bfedc6b5001146cc3effe6d8a](https://github.com/AbslanLaverde/bsnes/commit/ac488fe85289642bfedc6b5001146cc3effe6d8a) | [U → public H](https://github.com/AbslanLaverde/bsnes/compare/7d5aa1e656b9171524d01b1b22917197d8121cb4...ac488fe85289642bfedc6b5001146cc3effe6d8a) |
| [EXP-001 BG observer](https://github.com/AbslanLaverde/bsnes/tree/gtc-hd/exp-001-passive-ppu-observation) | `ba148bedc74892722de93633ce08190dda406bf7` | [5ba4d2a8b12a82a09db1f76640e659303aef7e22](https://github.com/AbslanLaverde/bsnes/commit/5ba4d2a8b12a82a09db1f76640e659303aef7e22) | [U → public observer tip](https://github.com/AbslanLaverde/bsnes/compare/7d5aa1e656b9171524d01b1b22917197d8121cb4...5ba4d2a8b12a82a09db1f76640e659303aef7e22) |
| [EXP-002 OBJ observer](https://github.com/AbslanLaverde/bsnes/tree/gtc-hd/exp-002-obj-provenance) | `f0f90ee799969b735ca90b6dd9491219f0b9cc92` | [0977750530fb94efb8ddfcec6f27bde8d530ccbc](https://github.com/AbslanLaverde/bsnes/commit/0977750530fb94efb8ddfcec6f27bde8d530ccbc) | [Public H → public EXP-002](https://github.com/AbslanLaverde/bsnes/compare/ac488fe85289642bfedc6b5001146cc3effe6d8a...0977750530fb94efb8ddfcec6f27bde8d530ccbc) |
| [EXP-003 composition observer](https://github.com/AbslanLaverde/bsnes/tree/gtc-hd/exp-003-composition-provenance) | `76bdb9250befa62fcbf23fcff2ef962fe2f58215` | [f4a45d47797d4af0918768005b481f95e5ef4635](https://github.com/AbslanLaverde/bsnes/commit/f4a45d47797d4af0918768005b481f95e5ef4635) | [Public H → public EXP-003](https://github.com/AbslanLaverde/bsnes/compare/ac488fe85289642bfedc6b5001146cc3effe6d8a...f4a45d47797d4af0918768005b481f95e5ef4635) |
| [EXP-004 P0 tests](https://github.com/AbslanLaverde/bsnes/tree/gtc-hd/exp-004-color-math-provenance) | `94e12628b6dc9580e61fc3322be4a011328b0fe5` | [52cd72078fdc06a51ddeaa51efe943550dec795e](https://github.com/AbslanLaverde/bsnes/commit/52cd72078fdc06a51ddeaa51efe943550dec795e) | [Public C → public P0 tip](https://github.com/AbslanLaverde/bsnes/compare/f4a45d47797d4af0918768005b481f95e5ef4635...52cd72078fdc06a51ddeaa51efe943550dec795e) |

The unchanged upstream baseline **U** is [7d5aa1e656b9171524d01b1b22917197d8121cb4](https://github.com/AbslanLaverde/bsnes/commit/7d5aa1e656b9171524d01b1b22917197d8121cb4); it and all its ancestors retain their original identities. **H** is the shared runtime-harness baseline for EXP-002/003. **C** is the EXP-003 composition baseline for P0. Each comparison uses public baseline and tip IDs; the EXP-001 comparison includes its complete observer/harness/window-control changes from U.

Two earlier EXP-001 commits complete the historical/public ancestry mapping:

| Historical stage | Historical commit | Public equivalent |
| --- | --- | --- |
| Initial BG observer B | `0f946d112f045d5cf29a9e09876b15a592180b62` | [13e99b86e635389653ffac69606cb7736a4c798c](https://github.com/AbslanLaverde/bsnes/commit/13e99b86e635389653ffac69606cb7736a4c798c) |
| Harness on observer line H-observer | `2e0eeaa1580487f277e60f6ef55b9c74ca1026ae` | [2bea7467a611352233e271d6440133c4bef24ab0](https://github.com/AbslanLaverde/bsnes/commit/2bea7467a611352233e271d6440133c4bef24ab0) |

H and H-observer remain distinct commits: the observer line is U → B → H-observer → observer tip; the other line is U → H, with EXP-002 and EXP-003 as separate children, and P0 above EXP-003.

## Evidence and limits

Focused publication validation passed for the harness, EXP-001 observer/runtime controls, EXP-002 OBJ runner, EXP-003 composition runner and P0 at its public committed tip. It used Windows Python 3.12.9 and MSYS2 UCRT64 GCC 16.2.0. The checks covered host fixtures, relevant desktop builds and CLI rejection paths; no ROM was executed during publication validation. P0's four O0/O3 fixture runs agreed; ASan/UBSan libraries were unavailable. Native source matched each corresponding historical experiment tree.

This validation is separate from historical ROM validation and does not change any experiment's verification status. Read the original scope, results and remaining limitations in [EXP-001 results](../experiments/EXP-001/RESULTS.md), [runtime-harness results](../experiments/EXP-001/RUNTIME_HARNESS_RESULTS.md), [EXP-002 results](../experiments/EXP-002/RESULTS.md), [EXP-003 results](../experiments/EXP-003/RESULTS.md) and the [EXP-004-P0 report](../experiments/EXP-004/P0_OUTPUT_BOUNDS_REPORT.md).

**EXP-004: P0 bounds investigation only / implementation blocked.** The public branch contains the sanitized EXP-003 foundation plus P0 investigation tests. It does not contain color-math provenance implementation or a native bounds repair. The corrected P0 runner requires public C to be an ancestor of HEAD on the expected branch and checks both committed and working native source against C, allowing test/publication-only descendants.

The [EXP-004 specification gate](../experiments/EXP-004/SPEC.md) remains in force: the separate native-baseline investigation must be completed, its disposition documented, and implementation explicitly re-authorized. P0's disposition remains **STOP FOR SEPARATE NATIVE-BASELINE INVESTIGATION**.
