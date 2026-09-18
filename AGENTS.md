\# GTC-HD Research Workspace



\## Purpose



This workspace supports architecture and source-code research for GTC-HD.



GTC-HD is an experimental modern enhancement rendering system for SNES games.



Guiding principle:



> \*\*Enhance the pixel art. Never erase the pixel art.\*\*



The project is currently in:



\*\*Phase 0 — Discovery / Research / Architecture\*\*



Read `project/GTC-HD\_PROJECT\_STATE.md` before performing substantive GTC-HD research.



\## Authority Model



Do not confuse upstream emulator repositories with GTC-HD project authority.



\### GTC-HD project authority



Files under `project/` describe GTC-HD project state, research findings, and architectural decisions.



Do not infer an accepted GTC-HD decision unless it is explicitly documented as accepted.



\### Upstream source authority



Repositories under `upstream/` are external projects being investigated.



Their checked-out source code is authoritative only for claims about that specific upstream implementation and revision.



For example:



`upstream/bsnes/` may be used to determine how the checked-out version of bsnes works.



It is NOT the GTC-HD codebase.



It is NOT evidence that GTC-HD has selected bsnes.



It is NOT authoritative for GTC-HD architectural decisions.



\## Current Research Status



The SNES emulator/core foundation and PPU interception boundary are:



\*\*INVESTIGATING\*\*



No emulator/core has been selected.



\## Working Rules



Unless a task explicitly says otherwise:



\* Treat repositories under `upstream/` as read-only research targets.

\* Do not modify upstream source code.

\* Do not commit changes inside upstream repositories.

\* Do not implement GTC-HD inside an upstream repository.

\* Record the exact Git branch and commit SHA used for substantive research.

\* Ground source-code findings in actual repository paths, classes, functions, methods, and data structures.

\* Clearly distinguish:



&#x20; \* source-code observation;

&#x20; \* inference;

&#x20; \* hypothesis;

&#x20; \* uncertainty.

\* Never convert brainstorming or upstream implementation choices into accepted GTC-HD architecture.



\## Research Outputs



Write GTC-HD research findings outside upstream repositories.



Preferred location:



`project/research/`



Research reports should normally include:



\* repository identity;

\* branch and commit SHA;

\* research question;

\* source-code evidence;

\* findings;

\* uncertainties;

\* implications for GTC-HD;

\* experiments still required;

\* recommended next research step.



\## Accuracy Priority



GTC-HD prioritizes:



1\. Correct game behavior.

2\. Accurate SNES execution.

3\. Faithful original rendering semantics.

4\. Universal enhancement.

5\. Optional game-specific enhancement.

6\. Experimental visual effects.



Do not recommend compromising SNES execution merely to simplify enhanced rendering.



\## Current Primary Research Question



Determine which SNES emulation architecture provides the strongest foundation for GTC-HD and where sufficiently rich PPU state can be intercepted to support a modern enhancement renderer without compromising accurate SNES execution.



