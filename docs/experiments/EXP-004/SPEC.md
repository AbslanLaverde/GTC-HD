\# EXP-004 — Color Math and Native Sample Provenance



Date: September 22, 2026.



\*\*Status:\*\* PROPOSED / INVESTIGATING  

\*\*Research target:\*\* bsnes cycle PPU  

\*\*Experimental dependency:\*\* EXP-003 composition provenance  

\*\*Proposed source baseline:\*\* EXP-003 implementation commit `76bdb9250`  

\*\*Production architecture impact:\*\* None — experimental research only



\---



\## 1. Purpose



EXP-001 demonstrated preservation of tiled-background provenance.



EXP-002 demonstrated preservation of OBJ provenance through native sprite overlap.



EXP-003 demonstrated preservation of native main- and sub-screen composition winners.



Those experiments establish an increasingly useful semantic chain:



```text

BG provenance ───────┐

&#x20;                    │

OBJ provenance ──────┤

&#x20;                    ↓

&#x20;             native candidates

&#x20;                    ↓

&#x20;           main/sub composition

&#x20;              ↙           ↘

&#x20;       MAIN winner     SUB winner

```



The next unresolved boundary is how those winners participate in native SNES color processing and become the samples written by the cycle PPU.



EXP-004 asks:



> Can GTC-HD preserve the native color-math decisions, operands, operations, and resulting native PPU samples while retaining the source provenance established by EXP-003 and without replacing or disturbing authoritative PPU execution?



\---



\## 2. Why this matters to GTC-HD



A main-screen winner and sub-screen winner are still not necessarily equivalent to the color ultimately produced by the SNES PPU.



Native color processing may:



\- allow or suppress color math for the selected main source;

\- clip the primary operand;

\- use the sub-screen source;

\- substitute fixed color;

\- add two colors;

\- subtract one color from another;

\- halve the result;

\- apply display brightness;

\- produce different left/right samples in hires or pseudo-hires modes.



A framebuffer-only enhancement renderer sees only the result.



That loses information about how the result was produced.



For example, two visually similar pixels may have completely different native histories:



```text

BG1 directly displayed

```



versus:



```text

BG1 + SUB BG2

```



versus:



```text

OBJ - fixed color

```



versus:



```text

clipped main + sub

```



For future GTC-HD features such as lighting, material treatment, transparency-like enhancement, replacement assets, spatial interpretation, or renderer debugging, these distinctions may matter.



EXP-004 therefore investigates whether GTC-HD can preserve:



> not merely the color the SNES produced, but the native semantic path that produced it.



These future features are not implemented by this experiment.



\---



\## 3. Source-grounded starting point



The experiment must begin from the actual bsnes cycle-PPU behavior rather than from a simplified model of SNES color math.



At audited upstream commit:



```text

7d5aa1e656b9171524d01b1b22917197d8121cb4

```



the relevant implementation is primarily:



```text

bsnes/sfc/ppu/screen.cpp

bsnes/sfc/ppu/screen.hpp

bsnes/sfc/ppu/window.cpp

bsnes/sfc/ppu/io.cpp

bsnes/sfc/ppu/serialization.cpp

```



EXP-004 starts experimentally from the frozen EXP-003 implementation:



```text

76bdb9250

```



because EXP-004 needs the main/sub source provenance that EXP-003 already preserves.



This dependency does not make EXP-003 instrumentation production architecture.



\---



\## 4. Native color-path observations to preserve



\### 4.1 Below is evaluated before above



`Screen::run()` performs:



```text

below(hires)

above()

brightness/output

```



in that order.



That ordering is semantically important.



EXP-004 must not model the two paths as if they were evaluated simultaneously.



\---



\### 4.2 Composition color is not yet final output



EXP-003 preserves the selected main/sub sources and their resolved pre-math colors.



After those selections, the native screen path can still apply:



\- source-specific color-math eligibility;

\- color-window controls;

\- fixed-color substitution;

\- add/subtract;

\- halving;

\- brightness.



EXP-004 must preserve the distinction between:



```text

source color

```



and:



```text

post-math color

```



and:



```text

brightness-adjusted native PPU output sample

```



\---



\### 4.3 Color-math eligibility follows the selected main source



The native main winner influences whether color math is enabled.



The relevant source classes include:



```text

BG1

BG2

BG3

BG4

OBJ

Backdrop

```



OBJ has an additional native palette restriction in the current bsnes implementation.



EXP-004 must preserve the effective native decision rather than independently re-derive it later.



\---



\### 4.4 Color-window controls are distinct from layer-window controls



EXP-003 investigated layer windows that suppress BG or OBJ composition candidates.



EXP-004 concerns the separate color-window outputs used later in screen/color processing.



These mechanisms must not be conflated.



A source may successfully win main composition and still have its color treated differently by the later color-window path.



\---



\### 4.5 The second color-math operand is conditional



The native path can use either:



```text

sub-screen color

```



or:



```text

fixed color

```



as the second operand.



The effective operand is not always determined solely by the global fixed/sub configuration.



In the inspected cycle PPU, a transparent sub-screen result can alter the effective blend behavior.



EXP-004 must preserve the \*\*effective operand actually used\*\*, not merely the configured preference.



\---



\### 4.6 Native arithmetic must remain authoritative



The cycle PPU implements saturated SNES 15-bit color arithmetic for:



```text

add

subtract

add + halve

subtract + halve

```



EXP-004 must not introduce a second independently authoritative implementation into the observer.



The experiment should observe:



```text

native operands

native operation

native result

```



rather than recomputing the result and treating the recomputation as truth.



Independent arithmetic may be used in tests as a validation oracle, but not as the runtime source of provenance.



\---



\### 4.7 Brightness occurs after color math



`Screen::run()` applies the native display-brightness table after `below()` and `above()` return.



EXP-004 should therefore distinguish:



```text

pre-brightness native result

```



from:



```text

sample actually written to the native PPU framebuffer

```



This gives the future renderer both semantic arithmetic information and an exact native reference sample.



\---



\## 5. Critical hires / pseudo-hires complication



The ordinary low-resolution path is not the entire problem.



In hires or pseudo-hires operation, `below()` can use screen-math state that existed before the current `above()` call.



Therefore the left/native-below sample can have a temporal dependency on the preceding main-screen math state.



Conceptually:



```text

previous main/math state ─────┐

&#x20;                             │

current sub selection ────────┤

&#x20;                             ↓

&#x20;                      hires left sample



current main selection ───────┐

current sub selection ────────┤

&#x20;                             ↓

&#x20;                      current right sample

```



This means a record containing only the current main and current sub winner is potentially insufficient to explain every hires sample.



EXP-004 must either:



1\. preserve the required previous-pixel provenance explicitly; or

2\. mark that provenance unknown where it cannot be established safely.



It must never silently attach the current main winner to a sample that actually depends on previous-pixel state.



The native source also notes uncertainty about exact first-hires-pixel scanline initialization.



EXP-004 must preserve that limitation rather than claim hardware verification that does not exist.



\---



\## 6. Hypothesis



\*\*HYPOTHESIS:\*\*



The bsnes cycle PPU contains observation points where GTC-HD can preserve the native color-math operands, controls, effective operation, pre-brightness result, and native framebuffer samples while retaining main/sub source provenance and without changing native execution.



If supported, EXP-004 would extend the semantic chain to:



```text

BG / OBJ provenance

&#x20;       ↓

main/sub composition

&#x20;       ↓

native math operands

&#x20;       ↓

color-window / eligibility

&#x20;       ↓

fixed color or sub source

&#x20;       ↓

add / subtract / halve

&#x20;       ↓

brightness

&#x20;       ↓

native PPU sample

```



This would still be experimental evidence, not an accepted production interface.



\---



\## 7. Primary research questions



EXP-004 must answer:



1\. Can the current main winner remain linked to its provenance through color math?



2\. Can the current sub winner remain linked to its provenance when the sub screen actually participates as an operand?



3\. Can fixed color be represented explicitly when it replaces the sub-screen operand?



4\. Can the observer distinguish:

&#x20;  - color math disabled;

&#x20;  - main color clipped;

&#x20;  - sub-screen operand;

&#x20;  - fixed-color operand;

&#x20;  - add;

&#x20;  - subtract;

&#x20;  - halved result;

&#x20;  - unhalved result?



5\. Can the exact native pre-brightness result be captured without rerunning native math?



6\. Can the exact brightness-adjusted PPU sample be captured without changing framebuffer output?



7\. Can hires/pseudo-hires temporal dependencies be represented without falsely attributing current-pixel provenance?



8\. Can all of this remain passive under deterministic native-framebuffer comparison?



\---



\## 8. Required semantic information



The exact implementation and record layout are left to repository-aware investigation, but EXP-004 should preserve enough information to answer the research question.



Useful record information is expected to include:



\### Position and rendering context



\- capture-relative frame;

\- X/Y;

\- PPU H/V counter;

\- field;

\- BG mode;

\- hires/pseudo-hires state;

\- display brightness;

\- forced blank / skipped state where relevant.



\### Current source provenance



\- current main source category;

\- current main provenance where known;

\- current sub source category;

\- current sub provenance where known;

\- current main pre-math color;

\- current sub pre-math color.



The experiment should reuse or extend the proven EXP-003 provenance mechanism rather than reconstruct these sources from final colors.



\### Native eligibility and window state



\- selected-source color-math eligibility;

\- relevant color-window outputs;

\- effective math-enable state;

\- whether the primary operand was passed or clipped to zero.



\### Second operand



The record must distinguish at least:



```text

none

sub-screen source

fixed color

```



and preserve the actual operand color.



If configured sub-screen blending falls back to fixed color because of native transparent-sub behavior, that reason should remain distinguishable.



\### Arithmetic operation



The observer should identify the effective native operation:



```text

no color math / passthrough

add

subtract

add + halve

subtract + halve

```



If additional semantic cases are required by the real native implementation, they should be represented explicitly rather than forced into an inaccurate category.



\### Result



Preserve:



\- native result before brightness;

\- display-brightness level;

\- actual native PPU framebuffer sample after brightness.



\### Hires history



Where a native sample depends on earlier math state, preserve enough information to identify that dependency.



Possible representations include:



\- previous record linkage;

\- copied previous-main source/provenance;

\- an explicit diagnostic history token;

\- an explicit unknown/scanline-seed state.



The implementation should choose the smallest representation that is correct.



\---



\## 9. Two native output samples must not be conflated



`Screen::run()` writes two native samples per composition position.



In ordinary low-resolution output, both normally represent the current above result after brightness.



In hires/pseudo-hires output, the first sample can represent the below/temporal path while the second represents the current above path.



EXP-004 should therefore preserve the relationship between the composition position and both emitted native samples.



A suggested conceptual representation is:



```text

composition position

&#x20;  │

&#x20;  ├── sample A provenance/result

&#x20;  │

&#x20;  └── sample B provenance/result

```



The exact record schema is an implementation question.



The semantic distinction is required.



\---



\## 10. Passivity constraints



The native cycle PPU must remain authoritative.



EXP-004 must not:



\- replace native color math;

\- skip native palette lookup;

\- perform additional stateful palette lookup;

\- rerun native winner selection;

\- rerun color-window tests for runtime truth;

\- reread VRAM, OAM, or CGRAM to reconstruct operands;

\- change native timing steps;

\- change framebuffer write order;

\- change native serializer payload;

\- introduce file I/O inside PPU rendering hooks;

\- retain live pointers to mutable native PPU state.



In particular, `paletteColor()` is not a harmless query: it updates the native CGRAM address latch.



The observer must capture values produced by the authoritative execution rather than invoke stateful helpers a second time.



Where practical, the observer should capture the actual native returned/result values rather than recomputing them.



\---



\## 11. Observer lifecycle



As with the earlier experiments:



\- observer disabled by default;

\- bounded memory;

\- no per-pixel file I/O;

\- explicit dropped-record counter;

\- explicit overflow state;

\- copied/owned record data;

\- export only after emulation execution has returned;

\- reset/power/load invalidate diagnostic history;

\- discontinuities must not silently retain stale provenance.



Hires history makes discontinuity handling especially important.



If required predecessor provenance is unavailable following:



\- observer activation;

\- reset;

\- state load;

\- rewind;

\- other discontinuity;



the result must be marked unknown rather than inferred.



\---



\## 12. Experimental branch strategy



EXP-004 should branch from the frozen EXP-003 implementation:



```text

76bdb9250

```



Proposed worktree:



```text

experiments/bsnes-exp-004

```



Proposed branch:



```text

gtc-hd/exp-004-color-math-provenance

```



Reason:



EXP-004 begins at the semantic boundary EXP-003 already established.



Reimplementing BG, OBJ, and composition provenance independently would add duplicate code and another possible source of disagreement without answering a new research question.



This is an experimental dependency only.



It does not establish the eventual production architecture.



\---



\## 13. Focused host-test requirements



Before any real-ROM conclusion, focused tests should exercise the real native screen/color-math methods.



At minimum:



\### No-math path



\- eligible main source;

\- color math disabled;

\- unclipped main passes through;

\- clipped main becomes the native expected value.



\### Fixed-color arithmetic



\- add fixed color;

\- subtract fixed color;

\- add + halve;

\- subtract + halve;

\- saturation/borrow boundaries;

\- zero and maximum component cases.



\### Sub-screen arithmetic



\- main + sub;

\- main - sub;

\- halved variants;

\- distinct main/sub provenance retained.



\### Transparent sub behavior



Test the native case where sub-screen blending is requested but the selected sub path is transparent/backdrop in the condition that changes effective blend behavior.



The record must report what the native path actually did.



\### Source eligibility



Exercise color-math eligibility for:



\- BG;

\- OBJ;

\- backdrop.



Exercise the native OBJ palette restriction.



\### Color window



Exercise:



\- main color allowed;

\- main color clipped;

\- math allowed;

\- math suppressed;

\- combinations where clipping and arithmetic interact.



\### Brightness



At minimum test:



\- brightness 0;

\- maximum brightness;

\- one intermediate value.



Verify captured native framebuffer samples match actual native writes.



\### Mid-stream control changes



Change relevant native registers between rendered samples and verify records use the controls active at the actual composition/math point rather than a frame-level snapshot.



\### Hires / pseudo-hires



Exercise:



\- low-resolution baseline;

\- true hires mode;

\- pseudo-hires;

\- previous-pixel dependency;

\- scanline start;

\- explicit unknown history where predecessor provenance is unavailable.



\### Passivity



Compare baseline and instrumented native state/output signatures.



Include the CPU-visible CGRAM latch where applicable.



\### Serialization



Verify native serializer layout/payload remains unchanged.



Diagnostic state must not become part of native save-state semantics.



\---



\## 14. Runtime validation plan



Use the established deterministic Super Mario World environment first.



The initial runtime comparison should use:



```text

1,800 native callbacks

```



with a narrow semantic observation window.



\### A — existing reference



Use the preserved EXP-003 1,800-callback framebuffer sequence as an existing deterministic reference where available.



\### B — EXP-004 binary, observer disabled



Run the completed EXP-004 binary for 1,800 callbacks with restored deterministic:



\- ROM;

\- SRAM;

\- settings;

\- input state.



EXP-004 observation disabled.



B should match the existing deterministic reference.



\### C — exact same EXP-004 binary, observer enabled



Restore the same deterministic seeds.



Run the exact same executable for 1,800 callbacks.



Enable EXP-004 semantic capture for one targeted callback, initially:



```text

callback 500

```



Compare all ordered native framebuffer callback hashes:



```text

A == B == C

```



where the A reference is available.



At minimum:



```text

B == C

```



is required.



\---



\## 15. Runtime capture must contain meaningful color-math evidence



A technically complete capture that contains no actual color-math activity is not enough to answer EXP-004.



The selected real-ROM capture should ideally contain at least one actual arithmetic case.



Useful evidence includes:



\- fixed-color use;

\- sub-screen use;

\- addition;

\- subtraction;

\- halving;

\- clipping;

\- brightness other than a trivial identity case;

\- source provenance retained through an actual arithmetic result.



Not all categories need to occur in one callback.



If callback 500 is composition-rich but color-math-poor, choose another deterministic callback.



That is not experiment failure.



If the 1,800-callback no-input title sequence does not provide useful coverage, that is the trigger to use the planned deterministic gameplay-state infrastructure rather than introducing manual nondeterministic input into B/C comparison runs.



\---



\## 16. Runtime evidence summary



The experiment summary should emphasize semantic coverage rather than raw data volume.



Useful aggregate counts may include:



\- records retained;

\- unknown provenance;

\- dropped records;

\- overflow;

\- passthrough samples;

\- clipped samples;

\- fixed-color math;

\- sub-screen math;

\- additions;

\- subtractions;

\- halved operations;

\- brightness levels encountered;

\- hires samples;

\- temporal-history-known samples;

\- temporal-history-unknown samples.



These counts exist to establish what behavior the test actually exercised.



They are not the product result.



\---



\## 17. Verification criteria



EXP-004 can be marked:



\*\*VERIFIED FOR TESTED CONDITIONS\*\*



only if the relevant tested claims are supported by both implementation evidence and runtime evidence.



Minimum requirements:



1\. Focused native-method tests pass.



2\. Supported UCRT64 desktop build succeeds.



3\. EXP-004 observer disabled is deterministic against the established reference.



4\. Observer-enabled and observer-disabled native framebuffer sequences are identical for the complete comparative run.



5\. Targeted real-ROM capture completes successfully.



6\. No dropped records or overflow occur in the claimed capture.



7\. Required provenance is known for the specific real-ROM samples used to support the claim.



8\. The capture contains actual native color-math activity rather than only no-op/pass-through cases.



9\. At least one arithmetic result remains traceable to its contributing source provenance.



10\. Results distinguish what was real-ROM verified from what was only host-tested.



\---



\## 18. Failure / partial-result conditions



The experiment must not be called fully verified merely because the program runs.



Important partial outcomes include:



\### Framebuffer mismatch



If B and C differ:



\*\*PASSIVITY FAILURE\*\*



Stop architectural interpretation until explained.



\### Provenance lost before math



If the native result can be observed but operand source identity cannot be preserved safely:



\*\*SEMANTIC-PRESERVATION LIMIT DISCOVERED\*\*



Document the boundary.



\### Hires history unresolved



If ordinary low-resolution provenance works but hires temporal provenance cannot yet be represented safely:



\*\*LOW-RES RESULT SUPPORTED; HIRES REMAINS INVESTIGATING\*\*



Do not hide the distinction.



\### Uninteresting real-ROM capture



If the chosen callback contains no useful arithmetic:



\*\*VALID CAPTURE, INSUFFICIENT COVERAGE\*\*



Choose a better deterministic test window.



\### Window/math case only host-tested



Record it as:



\*\*IMPLEMENTED / HOST-TESTED, NOT REAL-ROM EXERCISED\*\*



rather than generalizing.



\---



\## 19. Non-goals



EXP-004 does not attempt to:



\- design the production GTC-HD renderer;

\- select a graphics API;

\- implement lighting;

\- implement HDR;

\- implement shaders;

\- implement asset replacement;

\- infer physical depth;

\- infer game-object identity;

\- solve Mode 7 provenance;

\- solve widescreen;

\- implement AI enhancement;

\- select an upscaler;

\- optimize observer performance prematurely;

\- establish universal SNES compatibility;

\- establish hardware truth beyond what the tested bsnes path and evidence support.



The purpose is narrow:



> Preserve and validate the semantic path from EXP-003 main/sub winners through native color math to the native PPU output sample.



\---



\## 20. Expected architectural value



If supported, EXP-004 would materially strengthen the semantic-preservation hypothesis.



The experimental chain would become:



```text

EXP-001

BG provenance

&#x20;       ↓

EXP-002

OBJ provenance

&#x20;       ↓

EXP-003

main/sub composition provenance

&#x20;       ↓

EXP-004

color-math and native-sample provenance

```



At that point, GTC-HD may have evidence that a future renderer can receive a representation closer to:



> This native output sample was produced from this original BG/OBJ source, optionally combined with this sub source or fixed color, under these native color-math conditions, and resulted in this exact native sample.



That is substantially more useful than a flattened framebuffer pixel.



It could eventually provide a semantic bridge between:



```text

what the SNES did

```



and:



```text

what a modern enhancement renderer is allowed to enhance

```



without requiring the enhancement renderer to guess backward from final colors.



\---



\## 21. Architectural status



EXP-004 does not itself accept an architecture.



Even if successful:



\*\*Semantic-preservation layer:\*\* HYPOTHESIS, potentially further supported



\*\*bsnes as GTC-HD foundation:\*\* INVESTIGATING



\*\*Production renderer interface:\*\* UNDECIDED



\*\*Semantic frame format:\*\* UNDECIDED



\*\*Graphics API:\*\* UNDECIDED



\*\*Game-profile format:\*\* UNDECIDED



Important project decisions remain separate from experimental success.



\---



\## 22. Results-document expectation



`RESULTS.md` should not become a raw instrumentation report.



It should answer:



1\. What native semantic problem was investigated?

2\. What did source inspection reveal?

3\. What did focused tests establish?

4\. What did real-ROM execution actually exercise?

5\. Was framebuffer passivity preserved?

6\. Which source-to-result relationships survived?

7\. What limitations remain?

8\. What does the result imply for GTC-HD?

9\. What should be investigated next?



Raw captures remain local by default.



Curated evidence and architectural learning belong in the public repository.



The durable result is not how many records were collected.



The durable result is what GTC-HD learned about preserving native rendering meaning.

