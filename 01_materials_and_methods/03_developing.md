## Main Workflow

1. **Gather Information**
2. **Filter** 
3. **Build the codebook**
4. **Do Pilot**, then revise codebook
5. **Reliabilty test** of Krippendorff
   1. You and the 2 coders code the **same subset** of species.
   2. Compute Krippendorff's alpha.
   3. Pass → freeze the codebook.
   4. Fail → fix the rules and retest on **fresh** species.
6. **Code all species** alone
7. 1st Main Course: Making License
   1. Coverage
   2. Base
   3. Variants
8. 2ndary Course: Species exclusivity reclassification

## Filter the Species

Species filter

- **Do:** count how many aspects each species has an extracted passage (anything except "Not mentioned").
- **Out:** species with too few are marked *insufficient* and left out of the counts below. They stay in the table list.
- **State:** the threshold (e.g. at least half of the aspects).

THRESHOLD STATED IN [`variables.toml` as `initial_filter_pct`](variables.toml) 

## Aspect of Codebook

Insert the output of two method before, here

### File Structure

```md
Version number and date

## Definitions

---

Below this are Coder section

## Scope and unit
- Unit: one species × one aspect = one coded cell = one code.
- Not coded: [baseline terms].

## Coder Procedure

## Values

Value definitions and Conditional sub-codes
also includes Ambiguous vs Not mentioned

### General decision rules

## Each aspect

definition of the aspect
keywords for search
type of the aspect
What each value means, per aspect.
Decision rules.
Examples

## Repeat

---

## Changelog

```

## Coding the Value of the Aspect

The data be in excel

Give to each coder this items, as columns: 
- species name, 
- source link
- aspect 
- the relevant quoted passage(s) 
  - already pulled out — not the full page, and not a bare link.
- code (empty blank)
- note

> [!INFO] relevant quoted passage
>
> - A passage is the chunk of text you copy from a species' rules page that talks about one aspect.
> - It's called a passage, not a quote, because sometimes it's more than one sentence, e.g. a rule plus its exception, or a bullet list

⚠️ Don't use live multiplayer for the reliability round. Coders would see each other's answers, which breaks independence. Give each coder their own copy, then merge.

### Why it felt confusing

Rename them to stances so the two layers stay separate:

- **Coding layer:** Allowed / Conditional / Prohibited / Not mentioned / Ambiguous
- **License layer:** Permissions / Condition / Prohibitions

### The rule: code the activity, not the sentence

Each aspect in your codebook is named as an **activity**. The code is the species' stance toward that activity.

**Aspect "NSFW"** → activity: *making NSFW content of a MYO*

| Source text | Code |
|---|---|
| "NSFW is allowed" | Allowed |
| "NSFW is not allowed" / "SFW only" / "keep it clean" | Prohibited |
| "NSFW OK if tagged" / "18+ only" | Allowed with condition |
| "Please be respectful" | Ambiguous |
| (nothing about it) | Not mentioned |

Sentences with "not" stop being confusing, because you're never asking "is this sentence a permission?" You're asking "can I do the activity?"

### ❓ "Conditional with different conditions among species?"

Good catch.

1. Sub-code the condition in the note column (e.g. NSFW: tagging / 18+ / platform-only).
2. Treat each condition type like a ban in Step 3: if one type reaches the threshold, decide per type:
    - Usage-level, low-burden (e.g. tagging) → can go into the base Conditions. State why.
    - Otherwise → it becomes a variant, or is left for creators' additional terms.
3. Your current base already has "tag NSFW content". Justify it this way, or it looks like it breaks Rule B.

## Reliability Test

Use Krippendorff's alpha 

Use *different* species for the reliability test so coders aren't seeing pilot cells.

The amount of species be made for reliability test per round IS STATED in [`variables.toml` as `pilot_species`](variables.toml)

**Pre-arrange the excerpts** that said in the previous section of this document.

> [!TIP] Why?
> 
> 1. **It isolates what you're actually testing.** Kappa/alpha measures agreement in *interpretation*, not agreement in *research effort*. If coders search independently, disagreements get muddied — you can't tell if it's "we read the same text differently" or "we found different text."
> 2. **Faster for volunteers**, which matters since they're unpaid.
> 3. **More reproducible.** Anyone auditing your data later sees exactly what the coder saw.

### No reliability test needed for

1. **Steps 1, 2 and 4:** these are counts and thresholds, so anyone gets the same numbers.
2. **Step 3:** a rule you chose, justified by your definition.
3. **Tagging each aspect as creation or usage:** your analytical decision, justified by the definition. It's only ~10 items, too few to test.

### Performing the calculation and serving it

**Calculation**

1. **Merge** the coders' copies into one sheet: one row per species × aspect that has a passage, and one column per coder.
2. **Convert codes to numbers:** Allowed=1, Conditional=2, Prohibited=3, Ambiguous=4.
3. **Compute:**

```python
import krippendorff, pandas as pd
df = pd.read_excel("round1.xlsx")          # columns: coder_a, coder_b, coder_c
data = df[["coder_a", "coder_b", "coder_c"]].T.to_numpy(dtype=float)
alpha = krippendorff.alpha(reliability_data=data, level_of_measurement="nominal")
agree = (df.nunique(axis=1, subset=None) if False else
         (df["coder_a"] == df["coder_b"]) & (df["coder_b"] == df["coder_c"])).mean()
print(alpha, agree)
```

4. Also compute a **confidence interval** (bootstrap) and alpha **per aspect** when an aspect has enough cells.

**Serving (reporting)**

| round | codebook | species | cells | coders | α (95% CI) | % agreement | result |
|---|---|---|---|---|---|---|---|
| 1 | v1.0 | 5 | 40 | 3 | 0.61 (0.45–0.74) | 70% | fail |
| 2 | v1.1 | 5 | 38 | 3 | 0.82 (0.71–0.90) | 87% | pass |

Add a short list of the main disagreement causes and what you changed.

### Retest

**When:** alpha is below `alpha_min`.

1. **List every disagreeing cell** and label the cause: vague rule / unclear source / coder mistake.
2. **Fix the codebook** for the vague-rule cases (new rule + example) and bump the version (v1.0 → v1.1).
3. **Pick fresh species.** Don't reuse pilot or earlier-round species, because coders remember them.
4. **Coders code blind again**, each with their own copy.
5. **Compute alpha again** and report both rounds, including the failed one.
6. **Stop rule:** after `max_rounds` fails, drop or merge the problem aspect, or report it as a limitation.
7. **After passing:** re-code the earlier rounds' species with the final codebook, then include them in the dataset.

## After all species are coded

After the species have been recoded

You now have one big table: **species (row) × aspects (col)**, with each cell holding one code (Allowed / Conditional / Prohibited / Ambiguous / Not mentioned).

The table is read in two directions:
- **Columns (per aspect)** → build the license
- **Rows (per species)** → classify each species


## 1st Main Course: Per aspect (builds the license)

In short, the base says "yes", and the variant says "no". The data only decides which topics get a line, and which "no" variants are worth offering.

### Step 1:  Coverage (does the aspect get a clause?)

- **Do:** for each aspect, count how many included species mention it.
- **Output:** 
  - IF above the threshold → THEN the aspect gets a clause. 
  - IF Below → THEN it's left out of the license.
- **State:** the coverage threshold (e.g. 50%).

### Step 2: Base license (what the clause says)

- **Do:** The stance is not determined by counts; it follows from the Open definition. write the most permissive stance possible", which is always "You MAY".
- **Output:** the base Open Species License.
- **State:** *why*. Your definition of Open means as few restrictions as possible, so bans are optional extras, not the default.

### Step 3: Variants (which bans are offered)

Not a count of clauses. If enough species use it (pick a threshold, e.g. ≥ 25% of those mentioning it), it becomes a variant.

- **Do:** for each aspect with a clause, count how many of the species mentioning it coded it **Prohibited**.
- **Output:** IF above the threshold →  THEN a variant that bans it (e.g. SFW-only, no-hybrid).
- **State:** the variant threshold (e.g. 25%), and that Conditional doesn't count as a ban.

## 2ndary Course: Per species (classifies the species)

- **Do:** for each included species, check whether it prohibits (or puts conditions on) any **creation** aspect (e.g. hybrid, traits, approval).
- **Output:** 
  - IF prohibiting is yes  → THEN Semi-Open. 
  - IF Not → THEN Open. IF Usage-only bans (NSFW, selling) → THEN still Open.
- **State:** which aspects you tagged as creation vs usage, and that this follows your definition of restricting.

