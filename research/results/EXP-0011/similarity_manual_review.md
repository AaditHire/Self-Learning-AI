# Phase 1T pre-inference similarity review

Threshold: identifier/literal-normalized reference sequence similarity >= 0.90.
Prompt-token Jaccard produced no flags at the same threshold (maximum 0.65).

The validator flagged 23 code pairs. Each was manually reviewed before model
inference against prompt semantics, algorithmic structure, control-flow label,
structural signature, hidden inputs, and expected outputs.

| Pair | Similarity | Disposition |
|---|---:|---|
| CD01 / CD07 | 0.976 | Retain: sign classification versus bounded temperature bands; shared three-way branch skeleton disclosed. |
| EV01 / EV02 | 0.964 | Retain: affine combination versus two-stage discount; shared split/convert boilerplate. |
| IO02 / IO08 | 0.953 | Retain: one-line angle/parenthesis format versus two-line status/title format. |
| IO01 / IO08 | 0.948 | Retain: reordered city/country single line versus bracketed status plus second line. |
| AR03 / AR04 | 0.947 | Retain: positive predicate count versus target-frequency count; shared array scan skeleton. |
| EV01 / EV03 | 0.946 | Retain: affine expression versus unit conversion with compound assignment. |
| IO03 / IO08 | 0.927 | Retain: three-field reordered single line versus two-field two-line output. |
| EV02 / EV03 | 0.924 | Retain: multiplicative discount pipeline versus hours/minutes accumulation. |
| ST05 / IO08 | 0.923 | Retain: string repetition with numeric conversion versus two-line field formatting. |
| IO03 / IO06 | 0.922 | Retain: semantic name/id ordering versus three independent bracketed fields. |
| CD01 / CD06 | 0.921 | Retain: flat three-way sign branch versus nested positivity/parity decision. |
| LP05 / CP02 | 0.921 | Retain: digit count versus digit sum; deliberately related input representation but different accumulator semantics. |
| LP03 / CP07 | 0.921 | Retain: divisibility counter versus repeated power followed by parity classification. |
| LP04 / LP06 | 0.918 | Retain: fixed five multiples versus variable-bound even sequence; both are direct-output loops. |
| AR01 / AR03 | 0.916 | Retain: product reduction versus conditional positive count. |
| EV06 / ST01 | 0.915 | Retain: numeric absolute distance versus reverse-and-uppercase text pipeline. |
| EV03 / EV05 | 0.915 | Retain: unit accumulation versus PI-based geometric product. |
| LP01 / LP02 | 0.911 | Retain: factorial product versus odd-square sum with step two. |
| EV01 / EV05 | 0.910 | Retain: two-value affine expression versus cylinder volume with two imports and PI. |
| ST05 / IO01 | 0.909 | Retain: repeat operation versus field reordering and literal separator. |
| AR01 / AR04 | 0.904 | Retain: numeric product reduction versus equality-frequency scan. |
| IO01 / IO02 | 0.902 | Retain: field reordering with colon versus angle/parenthesis enclosure. |
| FN04 / FN08 | 0.901 | Retain: branching absolute difference versus percentage adjustment with local arithmetic. |

The flags are dominated by mandatory GOCO input/split/display boilerplate and
the intentionally coarse normalization that replaces every identifier and
library name with `ID`. No pair shares the same semantic target, algorithmic
label, control-flow label, structural signature, or hidden-test mapping. The
pairs remain disclosed as correlated structures; the 64 tasks are not claimed
to be statistically independent.
