# EXP-003 — Main/Sub Composition and Winner Provenance

Date: September 22, 2026.

**Status:** VERIFIED FOR TESTED EXP-003 CONDITIONS  
**Research target:** bsnes cycle PPU  
**Implementation commit:** `76bdb9250`  
**Production architecture impact:** None — experimental evidence only

EXP-003 is complete for its intended Phase-0 research question.

The experiment provides real-ROM evidence that GTC-HD can preserve which native BG or OBJ source wins main- and sub-screen composition, retain useful source provenance for those winners, and do so without changing the native framebuffer output under the tested conditions.

It does **not** establish universal correctness across all SNES software, complete CPU-visible passivity, final-pixel provenance, an accepted semantic-frame architecture, or selection of bsnes as the GTC-HD emulator foundation.

---

## Public implementation

Public fork: [AbslanLaverde/bsnes](https://github.com/AbslanLaverde/bsnes).

| Identity | Commit / source |
| --- | --- |
| Historical implementation commit | `76bdb9250befa62fcbf23fcff2ef962fe2f58215` |
| Historical baseline H | `906f74b6e5f4f2f4e62bb960d01aa68c9f55f919` |
| Public research equivalent | [f4a45d47797d4af0918768005b481f95e5ef4635](https://github.com/AbslanLaverde/bsnes/commit/f4a45d47797d4af0918768005b481f95e5ef4635) |
| Public baseline H | [ac488fe85289642bfedc6b5001146cc3effe6d8a](https://github.com/AbslanLaverde/bsnes/commit/ac488fe85289642bfedc6b5001146cc3effe6d8a) |
| Public branch | [gtc-hd/exp-003-composition-provenance](https://github.com/AbslanLaverde/bsnes/tree/gtc-hd/exp-003-composition-provenance) |

[Compare public H → public EXP-003](https://github.com/AbslanLaverde/bsnes/compare/ac488fe85289642bfedc6b5001146cc3effe6d8a...f4a45d47797d4af0918768005b481f95e5ef4635). See the [specification](SPEC.md) for scope and the [publication map](../../research/BSNES_EXPERIMENT_PUBLICATION_MAP.md) for rewrite details.

The executable SHA-256 and ROM/framebuffer evidence below remain attributed to the historical implementation commit and build. The public equivalent preserves native experiment semantics; its separate focused publication checks did not produce the historical ROM evidence. **VERIFIED FOR TESTED EXP-003 CONDITIONS** retains exactly the scope and limitations recorded below.

## 1. What EXP-003 investigated

EXP-001 demonstrated that useful tiled-background provenance can be preserved before the native PPU discards it.

EXP-002 demonstrated that useful OBJ provenance can be preserved through OAM evaluation, tile fetch, and native OBJ overlap so that a surviving sprite candidate can still be traced back to its original source.

Those results left an important semantic gap.

Knowing that a BG tile or sprite candidate exists does not establish that it actually participates in the image.

A candidate may:

- exist but be disabled on a screen;
- exist but be suppressed by a layer window;
- survive windowing but lose native priority competition;
- win on the main screen but not the sub screen;
- win on the sub screen but not the main screen;
- lose to another BG or OBJ candidate;
- or fall back to the native backdrop when nothing else survives.

EXP-003 asked:

> Can GTC-HD preserve which original graphical source wins native main- and sub-screen composition, and preserve enough information to understand that decision, while bsnes continues to perform the authoritative native rendering?

This is the transition from knowing **what graphical sources existed** toward knowing **which graphical sources actually survive native composition**.

---

## 2. Why this matters to GTC-HD

Source provenance without visibility information is incomplete.

A future enhancement renderer must not assume that every fetched tile or sprite should be enhanced as visible content.

A sprite may exist but be behind foreground scenery.

A background tile may exist but lose priority competition.

A candidate may exist but be deliberately removed by a window.

Main and sub screens may select entirely different sources at the same native screen position.

Without composition semantics, a modern renderer could incorrectly:

- enhance a sprite the SNES intended to be hidden;
- draw an effect over foreground scenery;
- illuminate occluded content;
- replace an asset that did not survive native composition;
- infer false foreground/background relationships;
- attach depth or spatial effects to content that was not participating in the native image.

EXP-003 therefore begins connecting:

**where graphical content came from**

to:

**whether that graphical content actually survives native composition.**

That distinction is directly relevant to the long-term GTC-HD goal:

> **Enhance the pixel art. Never erase the pixel art.**

A modern effect is much safer when it is driven by native rendering semantics rather than guessed from the final framebuffer.

---

## 3. Key native composition findings

### 3.1 Main and sub are independent composition paths

**SOURCE OBSERVATION:** `Background::Output` and `Object::Output` expose independent candidates for the native main and sub paths.

In bsnes terminology:

- `above` corresponds to the main screen;
- `below` corresponds to the sub screen.

The two screens are composed independently.

A source winning the main screen does not imply that it wins the sub screen.

This distinction later matters because SNES color processing can combine main and sub information.

---

### 3.2 Candidate ordering and strict priority replacement

**SOURCE OBSERVATION:** `Screen::above()` and `Screen::below()` consider candidate sources in this order:

```text
BG1
 ↓
BG2
 ↓
BG3
 ↓
BG4
 ↓
OBJ
```

Each path begins at priority zero.

A later source replaces the current winner only when its resolved native priority is **strictly greater**.

Therefore an earlier source retains the winner on an equal-priority tie.

This means the final composition rule is not simply:

> sprite above background

or:

> larger raw priority wins

Instead, several concepts remain distinct:

- raw BG tile priority;
- raw OBJ priority;
- mode-dependent resolved priority;
- OBJ-vs-OBJ overlap;
- BG-vs-OBJ composition;
- main-screen eligibility;
- sub-screen eligibility;
- window suppression.

EXP-003 preserves the native result rather than attempting to reconstruct it later from framebuffer colors.

---

### 3.3 Mode-dependent resolved priorities

**SOURCE OBSERVATION:** `PPU::updateVideoMode()` maps source priorities into the resolved ranks used for native layer competition.

BG pairs below correspond to raw tile priority 0/1. OBJ quartets correspond to raw OBJ priority 0/1/2/3.

A dash means that BG is inactive in that configuration.

| Mode/configuration | BG1 | BG2 | BG3 | BG4 | OBJ |
|---|---|---|---|---|---|
| 0 | 8,11 | 7,10 | 2,5 | 1,4 | 3,6,9,12 |
| 1, BG priority off | 6,9 | 5,8 | 1,3 | — | 2,4,7,10 |
| 1, BG priority on | 5,8 | 4,7 | 1,10 | — | 2,3,6,9 |
| 2,3,4,5 | 3,7 | 1,5 | — | — | 2,4,6,8 |
| 6 | 2,5 | — | — | — | 1,3,4,6 |
| 7, EXTBG off | 2 | — | — | — | 1,3,4,5 |
| 7, EXTBG on | 3 | 1,5 | — | — | 2,4,6,7 |

This is another reason a future GTC-HD renderer should preserve native decisions instead of attempting to infer visibility from raw priority bits alone.

---

### 3.4 OBJ overlap and BG/OBJ composition are different decisions

**SOURCE OBSERVATION:** OBJ processing first reduces overlapping fetched sprite samples to a single native OBJ candidate.

Within the native fetched-slot traversal used by `Object::run()`, each later covered nontransparent sample overwrites the previous OBJ sample.

That surviving OBJ candidate's raw priority is then mapped through the native OBJ priority table before competing against BG candidates.

Therefore:

```text
OBJ vs OBJ overlap
        ↓
surviving OBJ candidate
        ↓
resolved OBJ priority
        ↓
OBJ vs BG composition
```

These are separate stages.

EXP-002 investigated the first.

EXP-003 investigates the second.

---

### 3.5 Layer windows can remove otherwise valid candidates

**SOURCE OBSERVATION:** the native layer-window path can zero a candidate's priority separately for main and sub composition.

EXP-003 records the candidate immediately before and after this native operation.

A nonzero-to-zero transition can therefore be classified as native window suppression without:

- rerunning the window test;
- rereading PPU memory;
- inferring suppression from framebuffer color.

A pre-window priority of zero is recorded as candidate absence.

A surviving candidate that does not become the winner is recorded as a priority loss.

These are materially different rendering outcomes.

---

### 3.6 Backdrop is a real composition result

When no eligible BG or OBJ candidate survives, the native composition path selects the backdrop.

EXP-003 records backdrop explicitly rather than interpreting it as unknown provenance.

Forced-blank or otherwise skipped composition is also represented separately from backdrop.

This prevents the observer from inventing a winner where native composition never occurred.

---

## 4. Why observation must happen inside the native path

A central lesson from the bsnes audit remains important here:

> Useful rendering semantics disappear progressively during PPU execution.

By the time GTC-HD sees only the completed framebuffer, the renderer can no longer reliably recover:

- which BG produced the pixel;
- which tile fetch produced it;
- which OAM entry contributed a sprite;
- which candidates were suppressed;
- which candidates lost priority competition;
- which source won main;
- which source won sub.

There is also a passivity concern.

**SOURCE OBSERVATION:** palette lookup itself is not necessarily observationally free.

`Screen::paletteColor()` updates the native CGRAM address latch, which participates in CPU-visible PPU behavior.

Therefore an observer must not casually call native rendering helpers a second time merely to reconstruct information.

EXP-003 instead labels the native branches that bsnes already takes and copies values that native execution has already produced.

The native cycle PPU remains authoritative.

---

## 5. Experimental design

EXP-003 uses diagnostic sidecars rather than replacing native PPU structures.

The experiment deliberately avoided:

- replacing the native composition algorithm;
- extending native serialized BG/OBJ pixel state;
- adding observer data to the normal PPU save-state payload;
- rereading VRAM, OAM, or CGRAM during observation;
- rerunning palette lookup;
- rerunning window tests;
- rerunning priority selection;
- deriving winners from final framebuffer colors.

Instead, small diagnostic sidecars follow the lifetimes of native BG and OBJ information.

At composition time, EXP-003 copies enough information to describe:

- candidate presence;
- pre-window priority;
- post-window priority;
- composition outcome;
- selected main source;
- selected sub source;
- resolved priority;
- palette information;
- already-computed pre-math color;
- BG provenance where known;
- OBJ provenance where known.

Unknown provenance remains explicit.

It is never reconstructed later from mutable live state.

---

## 6. Composition outcomes preserved

For each native candidate and screen path, EXP-003 distinguishes:

1. **Absent**  
   No eligible candidate entered composition.

2. **WindowSuppressed**  
   A candidate existed before native layer-window processing and was removed by that processing.

3. **PriorityLost**  
   The candidate survived windowing but did not win native composition.

4. **Won**  
   The candidate became the native main- or sub-screen source.

5. **CompositionSkipped**  
   Native composition did not occur for that path, for example because the screen function returned before ordinary selection.

This is more useful to GTC-HD than a simple visible/not-visible flag because it preserves some of the reason a graphical source did or did not participate.

---

## 7. Winner provenance

Where lineage is known, a selected source carries an owned diagnostic copy of its earlier provenance.

For tiled BG content this can include information such as:

- BG identity;
- map address;
- map entry;
- adjusted character;
- character-row VRAM word address;
- source X/Y within the character;
- tile mode;
- raw priority;
- H flip;
- fetch timing.

For OBJ content this can include information such as:

- original OAM slot;
- adjusted character;
- character-row VRAM word address;
- source subtile X;
- adjusted object-row Y;
- raw OBJ priority;
- H flip;
- fetch timing.

Fetch tokens identify diagnostic fetch lifetimes.

They are **not** persistent game-object identities.

An OAM slot is not automatically "Mario."

A BG layer is not automatically physical depth.

A bright palette value is not automatically a light source.

Those higher-level meanings remain separate research problems.

---

## 8. Main and sub composition remain independent

EXP-003 records separate main and sub winners rather than flattening them into one generic visible source.

Conceptually:

```text
BG provenance ───────┐
                     │
OBJ provenance ──────┤
                     ↓
              native candidates
                     ↓
               layer windows
                     ↓
            priority competition
               ↙           ↘
        MAIN winner     SUB winner
               │           │
               └─────┬─────┘
                     ↓
          later SNES color processing
```

This distinction became especially important during real-ROM validation.

---

## 9. Implementation record

EXP-003 was implemented in:

```text
experiments/bsnes-exp-003
```

Branch:

```text
gtc-hd/exp-003-composition-provenance
```

Implementation commit:

```text
76bdb9250
```

The experiment started from the existing deterministic runtime-harness baseline:

```text
906f74b6e5f4f2f4e62bb960d01aa68c9f55f919
```

The audited upstream bsnes baseline remains:

```text
7d5aa1e656b9171524d01b1b22917197d8121cb4
```

The supported build environment was MSYS2 UCRT64 using GCC/G++ 16.2.0.

A post-commit rebuild succeeded.

The exact executable used for final EXP-003 runtime validation had SHA-256:

```text
3125DFD40FFFDCDC8DB7D6D53EAAF499323372ED585559A47AC7DC6585CE6011
```

This fingerprint supersedes the earlier pre-commit development-build fingerprint.

---

## 10. Focused host-test evidence

Before real-ROM validation, the implementation was exercised using focused fixtures built around the native repository methods.

These tests covered:

- BG beating OBJ;
- OBJ beating BG;
- BG beating BG;
- equal-rank tie behavior;
- main/sub divergence;
- backdrop selection;
- forced-blank/skipped composition;
- native layer-window suppression;
- BG provenance lineage;
- OBJ provenance lineage;
- mosaic behavior;
- OBJ double-buffer lifetime;
- incomplete provenance;
- hires/pseudo-hires sequencing;
- observer reset/disarm behavior;
- bounded storage and overflow;
- output collision handling;
- malformed CLI arguments;
- unchanged frame-hash regression behavior.

The native-method fixture uses actual repository BG/OBJ/window/screen/mosaic code and the actual composition body, with deterministic host substitutes for surrounding emulator state.

It is not a whole-emulator or whole-game test.

Synthetic baseline and instrumented signatures were:

```text
native_composition_signature=f8952120fe226387b07fc3c6f8d1e3c931e0b44a145cc7c37b436e03810dc2f1
native_pipeline_signature=03df6a8c62befa48a4edb6f39dbe72d8c730338aedd10e80469482e698e4fe5b
```

These are host-fixture signatures, not ROM framebuffer hashes.

---

## 11. Runtime validation methodology

Real-ROM validation used the established deterministic Super Mario World test environment.

Authorized ROM:

```text
Super Mario World (U) [!].sfc
```

ROM SHA-256:

```text
D70C9C7716AD12C674FC7DD744736AA48D4D7B4237F58066BE620FDA26024872
```

Deterministic SRAM seed SHA-256:

```text
D0FF1B294B5288D1AE1421EADF5B2D38A8752B76D472FF30BED9028E25B1C5B8
```

Deterministic settings seed SHA-256:

```text
E22FBA1B0E141499C94A25652C6A2FAEBEA27ADB8A11D4EC2E84BEDA43A8FA6B
```

The run used the same deterministic no-input conditions established by the earlier experiments.

The framebuffer comparison window was intentionally increased from the earlier 600-callback runs to:

```text
1,800 native callbacks
```

This gives approximately 30 seconds of NTSC output while retaining deterministic execution.

Detailed composition capture remained deliberately narrow:

```text
full framebuffer validation: 1,800 callbacks
composition observation:      callback 500 only
```

This follows the research rule:

> Long-running framebuffer verification; short targeted semantic captures.

The B run used the EXP-003 binary with composition observation disabled.

The C run used the exact same executable with composition observation enabled only for callback 500.

Settings and SRAM were restored from the deterministic seeds before comparative execution.

No interactive gameplay input was introduced.

---

## 12. Real-ROM framebuffer result

The observer-enabled run exited successfully:

```text
process exit = 0
```

The B and C 1,800-callback frame-hash CSVs were compared after execution.

The comparison reported no differences.

Therefore, under this tested deterministic ROM slice:

> Enabling EXP-003 composition observation for callback 500 did not change the observed native framebuffer sequence across the 1,800-callback run.

This is real-ROM evidence for framebuffer passivity under the tested conditions.

It is not proof of complete execution-state equivalence.

Framebuffer equality alone does not establish that every internal latch, status bit, coroutine state, or CPU-visible side effect is universally unchanged.

---

## 13. Real-ROM composition result

Callback 500 produced a complete native composition capture.

Summary:

```text
requested_start_callback=500
requested_callback_count=1
end_callback_exclusive=501

window_started=true
window_completed=true

observed_callbacks=1
actual_native_callbacks=1800

record_count=61440
capacity=65536
record_bytes=176
retained_bytes=10813440

unknown_provenance_count=0
dropped_count=0
overflow=false

export_succeeded=true
capture_complete=true
reason=window_complete
```

The 61,440 records correspond exactly to:

```text
256 × 240 = 61,440
```

native screen positions.

The capture therefore accounts for one complete 256×240 composition surface.

No selected winner had unknown provenance.

No records were dropped.

The bounded capture did not overflow.

---

## 14. The selected callback contained real BG/OBJ competition

The callback was not a trivial background-only scene.

It contained:

```text
bg_obj_competitions=155
```

and:

```text
main_obj_wins=687
```

This is important.

EXP-003 did not merely record the existence of BG and OBJ candidates separately.

It captured real cases in which both BG and OBJ sources were admitted into native composition and the native PPU had to determine which source survived.

That directly exercises the central research question.

---

## 15. Main-screen composition observed

The 61,440 main-screen selections were:

| Source | Native positions |
|---|---:|
| BG1 | 11,969 |
| BG2 | 0 |
| BG3 | 22,015 |
| BG4 | 0 |
| OBJ | 687 |
| Backdrop | 22,673 |
| Skipped composition | 4,096 |
| **Total** | **61,440** |

The total accounts for the complete captured composition surface.

---

## 16. Sub-screen composition observed

The 61,440 sub-screen selections were:

| Source | Native positions |
|---|---:|
| BG1 | 0 |
| BG2 | 39,087 |
| BG3 | 0 |
| BG4 | 0 |
| OBJ | 0 |
| Backdrop | 18,257 |
| Skipped composition | 4,096 |
| **Total** | **61,440** |

Again, the total accounts for the complete captured composition surface.

---

## 17. Main/sub divergence is not an edge case

The real-ROM callback reported:

```text
main_sub_source_disagreements=47391
```

At 47,391 native positions, the main and sub screens selected different source categories.

This is one of the strongest architectural lessons from EXP-003.

GTC-HD should not prematurely flatten main and sub into one generic "visible source."

Later native color processing can use these separately composed screens.

A future semantic representation will therefore likely need to preserve main and sub composition independently at least until the color-math stage has been understood.

This is an **architectural implication**, not an accepted production design.

---

## 18. What EXP-003 adds to the GTC-HD journey

The first three provenance experiments now form a connected sequence.

### EXP-001 — Background provenance

GTC-HD can preserve:

> where tiled-background content originated.

### EXP-002 — OBJ provenance

GTC-HD can preserve:

> where sprite content originated and which OBJ sample survived native sprite overlap.

### EXP-003 — Main/sub composition provenance

GTC-HD can preserve:

> which of those native sources actually wins main- or sub-screen composition.

Together:

```text
BG source provenance ─────────────┐
                                  │
OBJ source provenance ────────────┤
                                  ↓
                         native candidates
                                  ↓
                           layer windowing
                                  ↓
                       priority competition
                           ↙             ↘
                    MAIN source       SUB source
                           │             │
                           └──────┬──────┘
                                  ↓
                         preserved semantics
                                  ↓
                    future enhancement renderer
```

This is materially closer to the information a future GTC-HD renderer needs.

A framebuffer-only renderer receives something conceptually like:

> Pixel `(x,y)` has color C.

The emerging GTC-HD model may eventually be able to provide something closer to:

> At `(x,y)`, this original BG or OBJ source existed, participated in native composition, survived the relevant native rules, became the main- or sub-screen source, and remains traceable to useful SNES graphical provenance.

That is a fundamentally richer foundation for faithful enhancement.

---

## 19. Product implications

EXP-003 does not implement modern rendering features.

It establishes information that future features may depend upon.

### Occlusion-aware enhancement

An enhancement renderer could avoid applying effects to sprite content that native composition placed behind foreground scenery.

### Visibility-aware lighting

A future light-emitting source could retain its graphical identity while native composition still determines which portions actually participate in the visible image.

### Enhanced or replacement assets

A replacement asset could remain linked to the source SNES tile or sprite while respecting native composition and occlusion.

### Foreground/background reasoning

Native winner relationships can provide evidence for later spatial reasoning without assuming that SNES layer number is equivalent to physical depth.

### Renderer debugging

A future diagnostic view could explain why a source:

- did not exist;
- was window-suppressed;
- lost native priority;
- won main;
- won sub;
- or fell back to backdrop.

This could be extremely useful when validating enhancement behavior against the native reference path.

These capabilities remain future possibilities.

EXP-003 does not claim that they are implemented.

---

## 20. Window provenance status

The EXP-003 implementation can distinguish native layer-window suppression from ordinary priority loss.

Focused native-method tests exercised window suppression successfully.

However, the selected real-ROM callback reported:

```text
candidate_window_suppressions=0
```

Therefore the correct status is:

**Window provenance mechanism:** IMPLEMENTED / HOST-TESTED

**Real-ROM layer-window suppression in this capture:** NOT EXERCISED

This does not invalidate EXP-003.

It identifies a specific coverage gap for later deterministic gameplay, synthetic raster tests, or cross-game validation.

There is no need to delay the primary EXP-003 conclusion solely to manufacture a window-active scene.

---

## 21. Passivity conclusion and limits

### What the experiment supports

Under the tested conditions:

- the observer retained complete selected-source provenance for the captured callback;
- no selected winner was unknown;
- no records were dropped;
- no capture overflow occurred;
- observer-enabled execution completed normally;
- the 1,800-callback native framebuffer comparison reported no differences.

Therefore:

> Native framebuffer passivity is VERIFIED FOR THE TESTED EXP-003 CONDITIONS.

### What it does not establish

EXP-003 does not prove:

- universal zero-overhead observation;
- universal CPU-visible execution equivalence;
- correctness across every SNES game;
- every raster-timing transition;
- every interlace/overscan/PAL case;
- every HDMA pattern;
- arbitrary reset/load/rewind behavior during capture;
- universal hires/pseudo-hires final-pixel provenance.

Those claims require separate evidence.

---

## 22. Hires and temporal limitation

**SOURCE OBSERVATION:** native `Screen::run()` selects the sub source before the main source.

In hires-related processing, native math may depend on persistent color state from the preceding pixel.

EXP-003 preserves the current composition winners and their pre-math operands.

It does **not** preserve the complete provenance of previous-pixel color-math history or final doubled framebuffer samples.

Therefore:

> EXP-003 must not be interpreted as complete hires final-pixel provenance.

The focused fixtures exercised the relevant sequencing, but universal hires correctness is outside this experiment.

---

## 23. EXP-003 stops before color math

Main and sub winners are not yet the final displayed SNES pixel.

After composition, later processing can involve:

- color-window permissions;
- clipping;
- source color eligibility;
- sub-screen color or fixed color;
- addition;
- subtraction;
- half-color behavior;
- brightness;
- hires/pseudo-hires history;
- final sample placement.

Conceptually:

```text
MAIN winner ────────────────┐
                            │
SUB winner / fixed color ───┤
                            ↓
                      color-window logic
                            ↓
                       add / subtract
                            ↓
                         halving
                            ↓
                        brightness
                            ↓
                    final native sample
```

Many of these operations are many-to-one.

Once they have happened, source identity may be difficult or impossible to recover from the final color alone.

This makes the next research boundary clear.

---

## 24. EXP-004 handoff

The next proposed experiment is:

# EXP-004 — Color Math and Final-Color Provenance

The central research question should be:

> Can GTC-HD preserve how the native main source and sub source or fixed color participate in the SNES color-math path, through clipping, eligibility, arithmetic, halving, brightness, and final sample production, without replacing the authoritative native PPU behavior?

Important topics include:

- main operand identity;
- sub operand identity;
- fixed-color substitution;
- source color-math eligibility;
- color-window gating;
- clipping;
- addition;
- subtraction;
- half-color rules;
- brightness;
- previous-pixel history where hires requires it;
- final native sample relationship.

EXP-003 intentionally does not solve these questions.

---

## 25. Emerging Phase-0 architectural finding

EXP-003 provides a third independent result supporting the semantic-preservation hypothesis.

Current experimental progress:

**BG source provenance:** VERIFIED FOR TESTED CONDITIONS

**OBJ source provenance:** VERIFIED FOR TESTED CONDITIONS

**Main/sub composition provenance:** VERIFIED FOR TESTED CONDITIONS

The pattern has now held across multiple distinct stages of the native cycle PPU.

This increasingly supports continued investigation of the following idea:

> If useful SNES rendering semantics will disappear during native PPU processing, preserve the information while the native PPU still knows it and carry that information forward for enhancement.

The emerging conceptual structure is:

```text
Accurate native PPU
 ├─ BG provenance
 ├─ OBJ provenance
 ├─ composition provenance
 ├─ future color-math provenance
 ├─ raster/timing context
 ├─ future Mode 7 provenance
 └─ native reference framebuffer
       ↓
 possible GTC-HD semantic representation
       ↓
 modern enhancement renderer
```

This remains a **HYPOTHESIS**.

It is not yet an accepted GTC-HD architecture.

---

## 26. What this says about bsnes

EXP-003 also adds evidence relevant to the larger Phase-0 emulator question.

The cycle PPU has now provided useful observation points across several distinct rendering stages:

- BG fetch/provenance;
- OBJ evaluation/fetch/provenance;
- main/sub composition.

The experiments so far indicate that useful semantic information can be captured alongside the authoritative cycle PPU rather than replacing its rendering logic.

That is encouraging evidence for bsnes as a possible GTC-HD foundation.

It is not enough to select bsnes yet.

Open questions still include:

- color-math provenance;
- raster and timing behavior;
- Mode 7;
- broader game compatibility;
- performance cost;
- integration ergonomics;
- eventual renderer interface design;
- practical gameplay/recording requirements.

Therefore:

**bsnes as GTC-HD foundation:** INVESTIGATING

No emulator selection is accepted by EXP-003.

---

## 27. Evidence retention

Raw experiment outputs remain local by default.

The public repository should preserve:

- experiment specification;
- implementation identity;
- reproducibility metadata;
- representative measurements;
- conclusions;
- limitations;
- architectural implications.

It should not become a warehouse of raw CSV captures and transient build artifacts.

EXP-003 follows the project evidence principle:

> Capture as much useful information as necessary, not indiscriminately everything.

The durable value of this experiment is not the existence of 61,440 CSV rows.

The durable value is what those rows demonstrate about the feasibility of preserving native composition semantics for a future enhancement renderer.

---

## 28. Current status

**EXP-003 specification:** COMPLETE

**EXP-003 implementation:** IMPLEMENTED

**Implementation commit:** `76bdb9250`

**Supported UCRT64 build:** PASSED

**Focused native-method tests:** PASSED

**Runtime observer window:** PASSED

**1,800-callback native framebuffer comparison:** VERIFIED FOR TESTED CONDITIONS

**BG-vs-OBJ native competition provenance:** VERIFIED FOR TESTED CONDITIONS

**Main-screen winner provenance:** VERIFIED FOR TESTED CONDITIONS

**Sub-screen winner provenance:** VERIFIED FOR TESTED CONDITIONS

**Main/sub source divergence:** VERIFIED FOR TESTED CONDITIONS

**Selected-winner provenance completeness in callback 500:** VERIFIED FOR TESTED CONDITIONS

**Dropped records:** NONE IN TESTED CAPTURE

**Overflow:** NONE IN TESTED CAPTURE

**Real-ROM layer-window suppression:** NOT EXERCISED

**Window suppression mechanism:** IMPLEMENTED / HOST-TESTED

**Complete CPU-visible passivity:** NOT ESTABLISHED

**Color-math provenance:** NOT YET INVESTIGATED

**Complete final-pixel provenance:** NOT YET ESTABLISHED

**Semantic-preservation architecture:** HYPOTHESIS, increasingly supported by experimental evidence

**bsnes as GTC-HD foundation:** INVESTIGATING

No renderer architecture, emulator foundation, graphics API, game-profile format, modern upscaler, or other production architecture is accepted by this experiment.

---

## 29. Durable conclusion

EXP-003 closes an important gap in the GTC-HD research chain.

EXP-001 showed that background source identity can survive beyond the point where the native PPU would normally discard it.

EXP-002 showed the same for sprite provenance and native OBJ overlap.

EXP-003 now shows, under tested conditions, that those source semantics can be carried through another major boundary:

> **native main/sub composition.**

The future renderer does not merely need to know that graphical content existed.

It needs to know what the SNES actually did with that content.

EXP-003 provides evidence that GTC-HD can preserve that distinction while continuing to let the accurate native PPU make the rendering decision.

That is another meaningful step toward a renderer that enhances SNES graphics from native semantic evidence rather than attempting to reconstruct intent from flattened pixels after the fact.

The evidence is increasingly consistent with the project direction:

> **Enhance the pixel art. Never erase the pixel art.**