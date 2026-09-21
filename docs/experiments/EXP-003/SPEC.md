\# EXP-003 — Main/Sub Composition and Winner Provenance



\*\*Project:\*\* GTC-HD

\*\*Status:\*\* PLANNED

\*\*Research Target:\*\* bsnes cycle PPU

\*\*Predecessors:\*\* EXP-001 BG Provenance, EXP-002 OBJ Provenance

\*\*Production Architecture Impact:\*\* None



\## 1. Purpose



Determine whether GTC-HD can preserve the provenance of the native source that wins SNES main-screen and sub-screen composition at each pixel while leaving the authoritative bsnes cycle PPU unchanged.



EXP-001 demonstrated preservation of normal tiled-background provenance.



EXP-002 demonstrated preservation of OAM → fetched OBJ tile → surviving native OBJ-candidate provenance.



EXP-003 investigates how these source candidates become the main-screen and sub-screen winners used by later SNES color processing.



\## 2. Product Motivation



A future GTC-HD renderer needs more than knowledge that a tile or sprite exists.



It must also understand whether that source is actually participating in the native composed image.



For example:



\* a sprite may be hidden behind a foreground BG;

\* a BG tile may be suppressed by a window;

\* different sources may win the main and sub screens;

\* a source may exist in provenance data but not contribute to the visible result.



Without native composition provenance, a future renderer could incorrectly enhance content that the SNES intended to be occluded or excluded.



EXP-003 therefore begins connecting:



\*\*source provenance\*\*



to



\*\*native visibility and composition semantics\*\*



\## 3. Research Question



> Can GTC-HD preserve which BG or OBJ source wins native main-screen and sub-screen composition, including the priority and window decisions that led to that result, without changing native PPU behavior?



\## 4. Scope



EXP-003 focuses on the cycle-PPU stages responsible for:



\* BG candidate availability;

\* OBJ candidate availability;

\* layer windows;

\* mode-dependent priority comparison;

\* main-screen selection;

\* sub-screen selection;

\* source identity immediately before color math.



Color math itself is outside this experiment and should be investigated separately.



\## 5. Desired Provenance Chain



The experiment should attempt to preserve a relationship conceptually similar to:



BG or OBJ source provenance

→ native candidate

→ window decision

→ priority comparison

→ main-screen winner

→ sub-screen winner



The winner should remain traceable back to its originating source provenance where that provenance is available.



For example:



Main winner:



\* source type: OBJ

\* OBJ provenance ID

\* native priority rank

\* window admitted: true



Sub winner:



\* source type: BG2

\* BG provenance ID

\* native priority rank

\* window admitted: true



The experiment should not infer winners later from framebuffer colors.



\## 6. Candidate Sources



Investigate the native candidates for:



\* BG1

\* BG2

\* BG3

\* BG4

\* OBJ

\* backdrop / fixed native fallback where relevant



Document which sources are eligible in each PPU mode and how bsnes represents their priorities.



\## 7. Priority Semantics



Do not assume raw SNES priority bits directly determine the winner.



Document:



\* raw BG/OBJ priority inputs;

\* bsnes mode-dependent resolved priority ranks;

\* comparison ordering;

\* tie behavior;

\* any source-order implications;

\* differences between OBJ-internal overlap and later OBJ-vs-BG priority.



EXP-002 already demonstrated that intra-OBJ overlap and OBJ-vs-BG priority are separate concepts.



EXP-003 must preserve that distinction.



\## 8. Window Semantics



Investigate and preserve the effects of layer windows.



For relevant candidates determine:



\* whether the source existed before windowing;

\* whether the relevant main-screen window admitted or suppressed it;

\* whether the relevant sub-screen window admitted or suppressed it;

\* which candidate would have existed absent suppression where useful and naturally available.



Do not alter native window logic.



Do not reconstruct window decisions later from final pixels if the native decision can be observed directly.



\## 9. Main and Sub Screens



Preserve the identity of both native winners independently.



Do not collapse them into one "visible source" before color math.



The SNES may use:



\* one source on the main screen;

\* another source on the sub screen;

\* backdrop/fixed color behavior;

\* different window behavior for each.



This distinction is required for the later color-math experiment.



\## 10. Candidate Provenance Linking



Where possible, winner records should link to previously captured provenance.



For BG winners, preserve or link information sufficient to identify the native BG source sample.



For OBJ winners, preserve or link the EXP-002-style OAM/fetched-tile provenance.



The experiment should investigate the cleanest way to establish these relationships without forcing the EXP-001 and EXP-002 diagnostic implementations wholesale into one permanent architecture.



The goal is to learn the required relationship, not yet design the final production schema.



\## 11. Losing Candidates



EXP-003 does not require recording every losing candidate indefinitely.



However, enough evidence should be retained to explain the winner.



Potentially useful information includes:



\* winner source;

\* winner priority;

\* nearest competing source/priority;

\* candidates suppressed by windows;

\* reason no source was eligible.



Capture as much useful information as necessary, not indiscriminately everything.



\## 12. Preserve Native PPU Behavior



The native composition path must remain authoritative.



Observation must not:



\* change BG candidate generation;

\* change OBJ candidate generation;

\* change window state;

\* change window tests;

\* change resolved priority values;

\* change source ordering;

\* change tie behavior;

\* change main/sub enable state;

\* call stateful palette helpers merely for diagnostics;

\* change color-math state;

\* alter PPU timing;

\* alter framebuffer generation.



Prefer copied values already computed by native code.



\## 13. Observation Boundary



Source inspection should determine the smallest useful observation points.



Likely areas include:



\* immediately before layer window suppression;

\* immediately after window suppression;

\* inside or immediately after main/sub winner selection;

\* before color-math operands are consumed.



Do not assume these are separate hooks if repository reality suggests a cleaner solution.



\## 14. Runtime Window



Reuse the deterministic callback-window methodology established by EXP-001 and EXP-002.



The observer should be:



\* armed before the `emulator->run()` call producing the selected callback;

\* disabled after that run returns;

\* exported only while core execution is stopped.



Begin with one native callback.



\## 15. Test Content



Super Mario World may remain the initial deterministic test input.



The initial callback should contain:



\* active BG content;

\* active OBJ content where possible;

\* at least some priority interaction;

\* ideally window activity if available.



If the selected callback lacks useful interaction, choose a different deterministic callback rather than interpreting empty evidence as success.



Later deterministic gameplay input should expand coverage.



\## 16. Runtime Validation



Use:



A — established harness-only reference



B — EXP-003 executable with composition observer disabled



C — same EXP-003 executable with observer enabled



Restore identical:



\* ROM;

\* SRAM seed;

\* settings seed;

\* input conditions.



Require exact equality of the ordered native framebuffer hash sequence for the tested run.



\## 17. Provenance Validation



For captured records, establish that:



\* main winner source is identifiable;

\* sub winner source is identifiable;

\* BG winners can be associated with useful BG source provenance;

\* OBJ winners can be associated with useful OBJ source provenance;

\* native resolved priorities are preserved;

\* window suppression is represented accurately;

\* no winner is reconstructed from later mutable state;

\* main and sub identities remain separate.



Where both BG and OBJ compete, demonstrate at least one concrete native winner relationship.



\## 18. Success Criteria



EXP-003 supports its hypothesis if:



1\. native window/priority/composition behavior remains authoritative;

2\. main-screen winner identity can be preserved;

3\. sub-screen winner identity can be preserved;

4\. winners can be traced to useful BG/OBJ source provenance where applicable;

5\. window suppression can be distinguished from priority loss;

6\. observer-disabled output matches baseline;

7\. observer-enabled output matches observer-disabled output for the tested sequence;

8\. no additional stateful PPU operations are required solely for observation;

9\. capture is bounded with explicit overflow/drop behavior;

10\. limitations are documented.



\## 19. What EXP-003 Does Not Establish



EXP-003 does not yet establish the final framebuffer color.



After main/sub selection, SNES color processing may still apply:



\* CGRAM/direct-color resolution;

\* fixed color;

\* clipping;

\* addition;

\* subtraction;

\* half-color;

\* brightness.



Those should be investigated separately.



\## 20. Product / Architecture Implication



If successful, EXP-003 would connect source provenance to native visibility:



BG provenance



\* OBJ provenance

&#x20; → native composition decisions

&#x20; → main/sub winners



This would move GTC-HD closer to a frame representation that can answer:



> Which original SNES graphical source is actually participating at this screen location, and why?



That information could later help the enhancement renderer respect occlusion, foreground/background relationships, lighting visibility, asset replacement, depth interpretation, and other effects without guessing from flattened pixels.



\## 21. Status Rules



A successful experiment may support:



\*\*Main/sub winner provenance — experimentally supported\*\*



It must not automatically establish:



\* complete final-pixel provenance;

\* color-math provenance;

\* final GTC-HD frame schema;

\* semantic-preservation architecture as ACCEPTED;

\* bsnes as ACCEPTED emulator foundation.



\## 22. Required Results Documentation



Create:



`docs/experiments/EXP-003/RESULTS.md`



The results should emphasize:



\* what native decision was investigated;

\* what provenance survives;

\* how priority actually works;

\* how windows affect candidate survival;

\* how main/sub winners are represented;

\* how this advances the future GTC-HD renderer;

\* what remains for color math and final-pixel provenance;

\* limitations and next steps.



Raw generated captures remain local by default.



