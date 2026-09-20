\# EXP-002 — OBJ / Sprite Provenance Preservation



\*\*Project:\*\* GTC-HD

\*\*Status:\*\* PLANNED

\*\*Research Target:\*\* bsnes cycle PPU

\*\*Predecessor:\*\* EXP-001 — Passive PPU Observation

\*\*Production Architecture Impact:\*\* None



\## 1. Purpose



Determine whether GTC-HD can preserve useful OBJ/sprite provenance from the accurate bsnes cycle PPU through sprite evaluation, tile fetch, overlap resolution, and native OBJ pixel production without changing native rendering behavior.



EXP-001 demonstrated that normal tiled-background provenance can be captured while the native PPU remains authoritative under the tested conditions.



EXP-002 investigates whether that semantic-preservation pattern extends to sprites.



\## 2. Product Motivation



Sprites are likely to be especially important to future GTC-HD enhancement systems.



Potential sprite-based content includes:



\* player characters;

\* enemies;

\* NPCs;

\* projectiles;

\* particles;

\* torches;

\* lamps;

\* explosions;

\* collectibles;

\* environmental effects;

\* UI elements.



A final framebuffer contains only composed colors.



A future enhancement renderer may instead benefit from knowing that a visible sample originated from:



\* a particular OAM slot;

\* a particular fetched OBJ tile;

\* a particular source row/pixel;

\* a particular palette;

\* a particular OBJ priority;

\* particular flip and size state;

\* a particular screen-space location.



Preserving this information could support later work in asset identity, lighting, enhanced materials, replacement graphics, spatial interpretation, and debugging.



\## 3. Research Question



> Can individual OBJ/OAM provenance be preserved far enough through the bsnes cycle PPU to associate native OBJ pixel candidates with the sprite and source tile that produced them, while leaving native framebuffer output unchanged?



\## 4. Background



The bsnes architecture audit found that OBJ identity is progressively lost.



During OBJ evaluation, bsnes retains an OAM index.



During OBJ tile fetch, the originating OAM item is still known.



The fetched OBJ tile representation does not retain the OAM index.



Later OBJ pixel production therefore no longer contains an explicit association with the originating OAM object.



EXP-002 will test whether an observational provenance path can preserve this association alongside the normal native pipeline.



\## 5. Hypothesis



\*\*HYPOTHESIS\*\*



OBJ provenance can be carried alongside the native bsnes cycle-PPU sprite pipeline without changing the behavior used by the native renderer.



A passive side record can preserve enough information to associate the native OBJ candidate at a screen position with the OAM object and fetched tile that produced it.



\## 6. Scope



EXP-002 focuses on the accurate/cycle PPU OBJ path.



The experiment should investigate:



1\. OBJ evaluation provenance;

2\. OBJ tile-fetch provenance;

3\. preservation of OAM identity through the fetched-tile lifetime;

4\. per-pixel OBJ provenance;

5\. overlap resolution between multiple OBJ tiles;

6\. the native OBJ candidate ultimately supplied to later BG/OBJ composition.



The experiment does not attempt to identify persistent game entities.



\## 7. Desired Provenance Chain



The experiment should attempt to preserve a relationship conceptually similar to:



OAM object

→ selected scanline item

→ fetched OBJ tile row

→ decoded OBJ pixel

→ native OBJ overlap winner

→ OBJ candidate supplied to later PPU composition



The goal is not merely to log each stage independently.



Where technically reasonable, records should make it possible to associate later OBJ output with the earlier source that produced it.



\## 8. Candidate Information to Preserve



Capture useful information that naturally exists in the native pipeline.



Potential fields include:



\### OAM / Object



\* frame or field identifier;

\* PPU timing position;

\* OAM index;

\* sprite X;

\* sprite Y;

\* character number;

\* name-table selection;

\* sprite size;

\* palette;

\* raw OBJ priority;

\* H flip;

\* V flip;

\* priority-rotation context where relevant.



\### Scanline Evaluation



\* whether the object qualified for the current scanline;

\* evaluated item order;

\* range-limit position;

\* selected row within the object;

\* object width/height where relevant.



\### Tile Fetch



\* source OAM index;

\* fetched OBJ tile number;

\* VRAM character-row address;

\* source row;

\* tile-relative X where derivable without reconstructing state;

\* screen X;

\* palette base;

\* resolved priority used by native OBJ output;

\* flip state.



\### Pixel / Candidate



For nontransparent native OBJ samples, attempt to retain:



\* screen X;

\* screen Y or scanline;

\* originating OAM index;

\* originating fetched-tile identity;

\* source pixel position;

\* palette/index information before final CGRAM color resolution where naturally available;

\* resolved OBJ priority;

\* whether this sample became the final native OBJ candidate at that X;

\* information necessary to distinguish an overwritten/losing OBJ sample from the surviving candidate.



Do not fabricate unavailable fields.



Document exact semantics and units for every implemented field.



\## 9. Identity Rules



An OAM index is:



\*\*hardware provenance\*\*



not:



\*\*persistent game-object identity\*\*



Do not describe an OAM slot as a stable character/entity ID.



Games may:



\* reuse OAM slots;

\* reorder sprites;

\* stream objects through different slots;

\* repurpose tile graphics;

\* change palettes;

\* modify OAM every frame.



Persistent identity is a later GTC-HD research problem.



EXP-002 should preserve the strongest native identity available without overstating its meaning.



\## 10. Overlap Is Critical



Multiple OBJ tiles can cover the same screen position.



The native PPU does not simply expose every sprite as an independent final layer.



EXP-002 must investigate how the cycle PPU resolves overlapping OBJ samples.



The experiment should determine whether provenance can identify:



1\. source samples considered at a screen X;

2\. which sample survives native OBJ overlap;

3\. the OAM/tile provenance of the surviving native OBJ candidate.



Capturing only OAM evaluation without following the surviving pixel is insufficient to answer the central EXP-002 question.



\## 11. Preserve Native PPU Behavior



The observer must remain observational.



Do not:



\* change OAM evaluation;

\* change sprite limits;

\* change range/time overflow behavior;

\* bypass native OBJ fetches;

\* add extra OAM reads;

\* add extra VRAM reads;

\* change OAM/CGRAM latches;

\* reorder sprite processing;

\* change overlap rules;

\* change native priority behavior;

\* change native framebuffer generation.



Prefer carrying/copying values that the native pipeline has already computed.



\## 12. Native Side Effects



The architecture audit established that OBJ evaluation and fetch participate in PPU behavior, including OAM latch behavior and sprite overflow/status state.



Therefore the native OBJ implementation must remain authoritative.



The semantic-preservation path must not replace native evaluation/fetch merely because equivalent graphical information appears obtainable elsewhere.



\## 13. Experimental Representation



Prefer a side-channel provenance representation rather than adding provenance fields to native structures unless source inspection shows that doing so is the smallest safe experiment.



If native structures must be experimentally extended, provenance fields must:



\* not affect native comparison/evaluation logic;

\* not participate in rendering decisions;

\* be initialized deterministically;

\* not affect serialized emulator behavior unless explicitly intended and documented.



The experiment should prefer observational ownership wherever practical.



\## 14. Capture Window



Reuse the deterministic callback-window mechanism developed during EXP-001.



The initial runtime validation should observe a small callback window that contains active sprite rendering.



Do not capture an arbitrarily long interval before measuring record volume.



Start with one native callback unless source/runtime evidence demonstrates that more is necessary.



\## 15. Test Content



Super Mario World may continue to serve as initial test content because it exercises ordinary OBJ rendering.



The ROM remains private/local.



Record only reproducibility metadata such as:



\* game identifier;

\* ROM SHA-256;

\* SRAM seed SHA-256;

\* settings SHA-256.



No ROM or SRAM contents should enter the public repository.



A later deterministic gameplay-input experiment should expand coverage beyond the boot/title sequence.



\## 16. Runtime Comparison



Use the same methodology established by EXP-001.



Compare:



A — baseline/harness reference



B — OBJ observer integrated but disabled



C — same executable with OBJ observer enabled for the selected callback window



Require exact equality of native framebuffer callback hashes for the tested sequence.



B and C should use the exact same executable whenever practical.



\## 17. Provenance Validation



For the captured window, validate that provenance is internally plausible.



At minimum examine whether:



\* OAM indices are present for active objects;

\* fetched OBJ tiles retain their originating OAM index;

\* source tile/row information follows the expected fetch;

\* screen coordinates are consistent;

\* transparent samples do not falsely become native OBJ candidates;

\* overlapping sprites resolve to a specific surviving native candidate;

\* final native OBJ candidate provenance can be traced back to an OAM object and fetched tile.



Do not infer persistent game identity from this validation.



\## 18. Buffering / Volume



Measure:



\* evaluation records;

\* fetched-tile records;

\* per-pixel provenance records;

\* bytes per observed callback;

\* dropped records;

\* overflow;

\* approximate observer cost.



Do not optimize prematurely.



If the experimental representation is too verbose, preserve the evidence first and use that result to design a smaller representation later.



\## 19. Success Criteria



EXP-002 supports its hypothesis if:



1\. native OBJ evaluation/fetch remains authoritative;

2\. OAM identity is preserved into fetched OBJ provenance;

3\. the provenance path can identify the source of the surviving native OBJ candidate;

4\. useful source tile/pixel information survives alongside that candidate;

5\. the observer produces records without silent overflow;

6\. observer-disabled native framebuffer output matches baseline;

7\. observer-enabled native framebuffer output matches observer-disabled output for the tested sequence;

8\. no additional stateful PPU operations are performed solely for observation;

9\. limitations and unsupported identity claims are documented.



Passing EXP-002 proves only the tested OBJ provenance slice.



\## 20. Failure Conditions



The hypothesis is unsupported if useful provenance requires:



\* altering native OBJ evaluation;

\* changing sprite ordering;

\* changing native overlap behavior;

\* performing extra stateful PPU reads;

\* replacing execution-visible native operations;

\* causing native framebuffer divergence;

\* relying on later mutable state to reconstruct missing identity.



A failed experiment is valid research evidence.



\## 21. Non-Goals



EXP-002 does NOT:



\* select bsnes as the final GTC-HD emulator;

\* define persistent sprite/game-object identity;

\* implement sprite replacement;

\* implement lighting;

\* classify torches/enemies/characters;

\* design game profiles;

\* implement a GPU renderer;

\* implement depth reconstruction;

\* alter sprite limits;

\* remove native PPU sprite behavior;

\* define the final GTC-HD graphics-state schema.



\## 22. Product / Architecture Question



The durable architectural question is:



> Can GTC-HD preserve sprite semantics while the native PPU still knows them, so that the future enhancement renderer receives source identity rather than only flattened sprite pixels?



If successful, EXP-002 adds another piece to a possible semantic-preservation architecture:



BG provenance



\* OBJ provenance

\* future Mode 7/composition semantics

&#x20; → GTC-HD frame representation

&#x20; → enhancement renderer



\## 23. Status Rules



A successful experiment may support:



\*\*OBJ provenance preservation — experimentally supported\*\*



It must not automatically establish:



\*\*Semantic preservation architecture — ACCEPTED\*\*



or:



\*\*bsnes — ACCEPTED foundation\*\*



Those decisions require broader evidence.



\## 24. Required Results Documentation



Create:



`docs/experiments/EXP-002/RESULTS.md`



The results should emphasize:



1\. what problem was investigated;

2\. what semantic information was successfully preserved;

3\. what information remains unavailable;

4\. whether native output remained unchanged;

5\. how the result advances the future GTC-HD renderer;

6\. limitations;

7\. implications for the emerging graphics-state representation;

8\. recommended next research step.



Raw generated artifacts should remain local by default.



Commit curated evidence and reproducibility metadata only when they materially support the architectural record.



