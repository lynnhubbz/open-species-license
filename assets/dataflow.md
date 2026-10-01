Finishing the comparison of your graph against the 01–04 notes. I've built a strict dataflow version, and I'm attaching it now.No, it isn't equivalent yet, and it also isn't a dataflow diagram yet. I compared it against `01`–`04` and `variables.toml`, then rebuilt it as `dataflow_strict.dot` (above).

## Why it isn't a dataflow yet

A dataflow alternates **item → activity → item**. Your graph has several item → item arrows with no activity between them:
1. The five `defs` → New Definitions
2. New Definitions and Final Aspect → Codebook
3. Species List → Coded Table
4. Coded Table → License

`Developing` is also a red node with no edges at all.

## Where it differs from your notes

**In your notes, missing from the graph**
1. **Passages sheet**, the extracted raw data that coding depends on.
2. **Species filter**, with Included and Insufficient species (`03` step 2).
3. **`variables.toml`**, which feeds the filter, reliability test, and license steps.
4. **Pilot**, and the **frozen codebook** plus reliability report (`03` steps 4-5).
5. **Code all species** as its own activity (step 6).
6. **Classify species** (the "2ndary Course").
7. **Reporting** (`04`).
8. Parts of `01`'s outputs: Closed and Semi definitions, creation vs usage, baseline, and scope exclusions.

**In the graph, not in your notes**
1. Open Source, Open Access, and Misc defs. These exist only in the manuscript and your older diagram.
2. **Final Aspect.**
3. **Developing** as a node. It's the whole `03` stage, not one step.

**Wrong connections**
1. **Species List** comes from Gather Information (`03` step 1), not from Listing Aspect.
2. **Merge rules** goes nowhere, but `02` says all its outputs go into the codebook.
3. **Reliability Test → Coded Table:** the test produces the reliability report and the frozen codebook. *Code all species* produces the coded table.

## What the new file does

1. **Strict dataflow.** I checked it with a script: no edge joins two items or two activities, and every activity has an input and an output.
2. **Clusters are labelled with your doc numbers** (01, 02, 03, 04), so you can map each box to a file.
3. **Dashed nodes mean "not in `01`–`04` yet"** (Open Source, Access, and Misc defs, Redefining, Finalizing aspects, Final Aspect). Either document them or delete them.
4. **The dashed "fail" arrow** loops from the reliability report back to Pilot.

## For you to decide

1. Are the Source, Access, and Misc "Open" definitions part of the method? If yes, add them to `01`'s outputs. If not, delete them.
2. Is "Final Aspect" a real step? If yes, write it into `02` or `03`.
3. Should Reporting also take the Species List and Included species?

The graph is wide, so use `scope: "parent"` for the figure. Or shrink it by merging Pilot with Reliability Test and dropping the `variables.toml` arrows.