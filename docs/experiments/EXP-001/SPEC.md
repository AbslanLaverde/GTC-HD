\# EXP-001 — Passive PPU Observation



\*\*Project:\*\* GTC-HD

\*\*Status:\*\* PLANNED

\*\*Date:\*\* September 18, 2026

\*\*Research Target:\*\* bsnes

\*\*Baseline Revision:\*\* `7d5aa1e656b9171524d01b1b22917197d8121cb4`

\*\*Target PPU:\*\* Accurate / cycle PPU

\*\*Production Architecture Impact:\*\* None



\## 1. Purpose



Determine whether meaningful SNES rendering provenance can be observed from the bsnes cycle PPU without changing native SNES execution or native rendered output.



This is a research experiment.



It does not select bsnes as the GTC-HD foundation.



It does not establish a final GTC-HD graphics interface.



It does not implement the GTC-HD renderer.



\## 2. Background



The bsnes architecture audit identified several important facts.



The cycle PPU performs rendering work that is intertwined with emulation-visible PPU behavior. Rendering operations can affect internal OAM and CGRAM latches and other state observable by SNES software.



Therefore GTC-HD should not assume that native PPU rendering can simply be removed and replaced by another renderer.



The audit also identified that useful source provenance exists transiently during rendering.



For normal tiled backgrounds, information such as tilemap lookup, character information, palette, priority, flips, and source position exists during the background fetch pipeline but becomes progressively unavailable as pixels move through composition.



This experiment tests whether that information can be observed passively.



\## 3. Research Question



> Can the bsnes cycle PPU emit useful background-rendering provenance while continuing to produce exactly the same native emulation behavior and reference rendering?



\## 4. Hypothesis



\*\*HYPOTHESIS\*\*



A bounded observational side channel can record selected BG fetch provenance from the cycle PPU without altering SNES-visible execution or native framebuffer output.



If supported, this would provide evidence that GTC-HD may be able to use bsnes as the authoritative PPU while receiving additional semantic information for enhancement.



\## 5. Scope



EXP-001 intentionally observes only a small portion of the rendering pipeline.



The initial target is:



\*\*normal tiled background fetch provenance in the cycle PPU\*\*



Mode 7, OBJ/sprites, windows, color math, independent rendering, GPU output, enhanced resolution, scene reconstruction, and persistent game-object identity are outside this experiment.



\## 6. Experimental Repository



Do not modify the pristine research checkout at:



`upstream/bsnes`



Create a separate experimental worktree from the audited revision.



Recommended branch:



`gtc-hd/exp-001-passive-ppu-observation`



Recommended worktree:



`experiments/bsnes-exp-001`



All bsnes code changes for this experiment must remain on that experimental branch/worktree.



\## 7. Baseline



The baseline is the unmodified bsnes source at:



`7d5aa1e656b9171524d01b1b22917197d8121cb4`



The experiment must confirm that its branch begins from this exact revision.



The pristine checkout remains the source reference for the audit.



\## 8. Observation Target



Begin from the cycle PPU background-fetch path identified by the architecture audit.



Relevant source areas include:



`bsnes/sfc/ppu/background.cpp`



particularly the normal tiled-background fetch path around:



`Background::fetchNameTable()`



and related character-fetch/consumption logic where necessary.



Codex must inspect the actual source before choosing instrumentation locations.



Do not assume line numbers remain valid after experimental edits.



\## 9. Minimum Provenance Record



For each selected BG fetch, attempt to record the information that is naturally and safely available at that point.



Candidate fields include:



\* frame identifier;

\* field identifier where relevant;

\* PPU vertical timing position;

\* PPU horizontal timing position;

\* background identity;

\* tilemap address or equivalent source-map location;

\* raw tilemap entry where available;

\* character/tile identifier;

\* character-row VRAM address where available;

\* source X/Y information where available;

\* palette group/index information;

\* priority;

\* horizontal flip;

\* vertical flip;

\* relevant BG mode;

\* any additional information required to interpret the record correctly.



These fields are experimental requirements, not assumptions about existing bsnes structures.



If a requested field is not naturally available at the proposed observation point, do not reconstruct it from later live state merely to satisfy the list.



Instead document:



\* where it actually exists;

\* why it is unavailable at the selected point;

\* and whether carrying it forward would require additional instrumentation.



\## 10. Observation Design Constraints



The observer must be observational.



It must not:



\* replace native BG rendering;

\* bypass native PPU operations;

\* alter register semantics;

\* change VRAM, CGRAM, or OAM behavior;

\* alter PPU timing;

\* change candidate selection;

\* change windows;

\* change color math;

\* alter native framebuffer generation;

\* introduce game-specific rendering behavior.



The normal bsnes PPU must remain authoritative.



Avoid calling existing helpers merely to extract information if those helpers have rendering or latch side effects.



Prefer recording values already being computed by the native execution path.



\## 11. Buffering



Do not use per-fetch console output as the primary capture mechanism.



Logging directly from high-frequency PPU code may cause excessive host overhead and makes the experiment harder to reason about.



Prefer a bounded in-memory observation mechanism.



The implementation should:



\* preserve record order;

\* have explicit capacity behavior;

\* detect/report overflow rather than silently corrupt records;

\* avoid ownership of live pointers whose contents may later change;

\* store values required for the record at observation time.



The exact container and implementation remain repository-level implementation decisions for Codex.



\## 12. Enable / Disable Control



Instrumentation must be independently enableable.



When disabled, the experimental build should follow the ordinary cycle-PPU code path with minimal additional work.



The experiment must clearly distinguish:



\*\*Observer Disabled\*\*



from



\*\*Observer Enabled\*\*



so their behavior can be compared.



The mechanism may be compile-time or runtime depending on what is least invasive in the actual repository.



Codex should document the choice.



\## 13. Test Procedure



Use identical emulator configuration and deterministic starting conditions for baseline and experimental comparisons.



Three configurations are required:



\*\*A — Baseline\*\*



Unmodified audited bsnes revision.



\*\*B — Experimental build, observer disabled\*\*



Experiment branch compiled with observation functionality present but disabled.



\*\*C — Experimental build, observer enabled\*\*



Same experimental build with provenance recording enabled.



For the same deterministic execution sequence, compare native rendering and emulator state between A, B, and C.



\## 14. Test Content



Start with a simple legally available SNES ROM or test ROM that visibly exercises normal tiled backgrounds.



Do not select the eventual GTC-HD showcase game based on this experiment.



The test should preferably contain:



\* scrolling;

\* multiple background tiles;

\* palette variation;

\* tile flipping if conveniently available.



More adversarial raster-effect testing belongs in later experiments.



Record the exact ROM/test identifier and hash used so the run is reproducible.



Do not store or commit commercial ROM images in the GTC-HD workspace.



\## 15. Native Output Comparison



Native bsnes rendering remains the reference output.



At minimum, compare native framebuffer results over the deterministic test sequence.



Prefer machine-comparable frame hashes or equivalent exact comparison rather than visual inspection alone.



Record:



\* number of frames compared;

\* comparison stage;

\* dimensions;

\* relevant rendering configuration;

\* any framebuffer normalization needed before hashing.



A visual match alone is insufficient evidence of passivity.



\## 16. Execution-State Comparison



The experiment must investigate whether an additional deterministic state comparison can be made between observer-disabled and observer-enabled execution.



Potential evidence could include serialized emulator state or targeted PPU-state checks at defined boundaries.



Codex must first verify that the proposed state representation is suitable for deterministic comparison.



Do not assume serialization is a valid checksum merely because serialization exists.



If no trustworthy state-level comparison can be established in this experiment, document that limitation explicitly.



Native framebuffer equality remains necessary but is not automatically sufficient to prove every CPU-visible PPU side effect is unchanged.



\## 17. Provenance Validation



Inspect captured records and verify that they correspond plausibly to actual background fetch activity.



At minimum demonstrate that:



\* records are produced for active tiled BG rendering;

\* timing/order is internally consistent;

\* tile/map information changes when scrolling encounters different source content;

\* palette/priority/flip fields correspond to the values consumed by the native fetch path;

\* records preserve their values after subsequent VRAM/register activity.



The goal is not merely to prove that data can be printed.



The goal is to prove that useful fetch-time provenance can be captured.



\## 18. Performance Measurement



Performance optimization is not the purpose of EXP-001.



However, record enough information to detect pathological observation cost.



Measure at least:



\* approximate record count per frame;

\* approximate bytes per frame;

\* whether observation causes obvious queue/buffer pressure;

\* whether overflow occurs.



Do not optimize the architecture based on this first measurement.



\## 19. Success Criteria



EXP-001 is successful only if all of the following are supported by evidence:



1\. The experiment runs from the audited bsnes baseline revision.

2\. The normal cycle PPU remains responsible for native rendering and execution-visible behavior.

3\. Useful tiled-BG provenance records are produced.

4\. Records retain fetch-time values rather than relying on later mutable state.

5\. The observation mechanism does not intentionally bypass or alter native PPU operations.

6\. Observer-disabled output matches the baseline for the tested deterministic sequence.

7\. Observer-enabled native output matches observer-disabled output exactly for the tested sequence.

8\. No record-buffer corruption or silent overflow occurs.

9\. Any state-level comparison attempted is documented with its limitations.

10\. All experimental limitations and unresolved questions are recorded.



Passing EXP-001 demonstrates feasibility only for the tested observation slice.



It does not prove that all required GTC-HD semantics can be exported passively.



\## 20. Failure Conditions



The experiment should be considered unsupported or failed if:



\* instrumentation changes native output;

\* instrumentation requires bypassing PPU behavior;

\* useful provenance cannot be captured without reconstructing it from later mutable state;

\* observer activity changes execution-visible PPU behavior;

\* records cannot be ordered reliably;

\* buffering cannot preserve data safely;

\* the result depends on modifying the semantics of the native renderer.



A failed result is valuable research evidence.



Do not hide or engineer around a failure merely to make the hypothesis appear successful.



\## 21. Non-Goals



EXP-001 does NOT attempt to:



\* select bsnes as GTC-HD's emulator foundation;

\* define the final GTC-HD graphics interface;

\* create a scene representation;

\* create a GPU renderer;

\* create high-resolution rendering;

\* enhance graphics;

\* intercept sprites;

\* intercept Mode 7;

\* reproduce color math;

\* reproduce windows;

\* replace native composition;

\* infer physical depth;

\* identify persistent game entities;

\* implement lighting;

\* implement game profiles;

\* benchmark production performance.



\## 22. Required Experiment Report



After implementation/testing, create:



`docs/experiments/EXP-001/RESULTS.md`



The results must contain:



\* experimental branch;

\* baseline SHA;

\* final experiment commit SHA;

\* files changed in bsnes;

\* instrumentation locations;

\* record schema actually implemented;

\* differences from this plan;

\* build configuration;

\* ROM/test identifier and hash;

\* test procedure;

\* framebuffer comparison method;

\* framebuffer comparison results;

\* state-comparison method/results if performed;

\* sample provenance findings;

\* record counts/data volume;

\* observed performance effects;

\* failures;

\* limitations;

\* unresolved questions;

\* architectural implications;

\* recommended next experiment.



Clearly distinguish source observations, experimental measurements, inference, and hypothesis.



\## 23. Decision Rule



EXP-001 must not automatically produce an architectural decision.



If successful, the result supports this narrower statement:



> Passive semantic observation of at least part of the bsnes cycle-PUU rendering pipeline appears feasible under the tested conditions.



It does not establish that bsnes should be selected or that this observation boundary should become GTC-HD architecture.



If unsuccessful, record which assumption failed and use that evidence when evaluating subsequent interception models and emulator candidates.



