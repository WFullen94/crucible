# Research Directions

Open research questions that emerged from building crucible. Each one is a potential
workshop paper, arXiv preprint, or full venue submission. Framed as a unified stress-test
of the SkillOpt paradigm (arXiv 2605.23904, May 2026).

**Overarching claim:** SkillOpt works when (a) the validation distribution stays honest,
(b) the task distribution stays stable, and (c) the environment is benign. This project
relaxes each assumption and measures what breaks.

---

## 1. Adversarial Validation Gates

**Hypothesis:** SkillOpt's static held-out validation split becomes an increasingly weak
gate as optimization progresses — the skill learns to perform on the fixed distribution
rather than generalize. Replacing the static split with a red-team LLM that generates
harder test cases as the skill improves produces more stable and generalizable skills.

**Novel claim:** The validation gate in SkillOpt is treated as a fixed object. Nobody has
studied what happens when it adapts. For adversarial domains (security, red-teaming), a
static gate is structurally mismatched to the task — the gate should be as adversarial as
the domain.

**What we need:**
- Phase 2 (base loop) complete
- Phase 3: red-team module that generates injection variants targeting current skill's rules
- Ablation: static gate vs. adversarial gate on same task, same target model
- Metric: final PINT benchmark score, convergence speed, skill document stability

**Potential finding:** Adversarial-gated skills generalize better to held-out attack types
and score higher on PINT than statically-gated skills, with similar or fewer accepted edits
(more selective, not more aggressive).

**Target venue:** NeurIPS 2026 Workshop on Agentic AI, or arXiv preprint
**Status:** Blocked on Phase 2 (base loop)

---

## 2. Skill Forgetting Under Distribution Shift

**Hypothesis:** Skills optimized on one attack distribution degrade measurably when the
attack distribution shifts — analogous to catastrophic forgetting in continual learning.
The slow update layer (protected region) partially mitigates this, but not fully.

**Novel claim:** SkillOpt's forgetting behavior has never been studied. The paper optimizes
on a fixed distribution and evaluates there. The continual learning literature has decades
of forgetting analysis for neural networks; the text-space analog is completely unexplored.
A skill document that performs well on direct injection may actively mislead the agent on
jailbreak-style attacks if its rules are too specific.

**What we need:**
- Phase 2 (base loop) + Phase 4 (forgetting experiment)
- Three-phase experiment: optimize on `direct` → shift to `jailbreak` → shift to `context_manipulation`
- Metrics: accuracy drop per transition, recovery curve after re-optimization, comparison with and without slow update layer
- Control: from-scratch optimization on the shifted distribution as a ceiling

**Potential finding:** Skills optimized on direct injection transfer partially to jailbreak
(shared surface patterns) but degrade sharply on context manipulation (requires different
detection logic). The slow update layer provides ~40-60% retention vs. no protection. This
maps directly to a practitioner recommendation: re-optimize on fresh data periodically; do
not treat learned skills as fixed artifacts.

**Target venue:** ICLR 2027 (agents / continual learning track), or NeurIPS 2026 Workshop
**Status:** Blocked on Phase 2 (base loop)

---

## 3. Adversarial Robustness of Learned Skill Rules

**Hypothesis:** Skill optimization produces specific, auditable rules ("flag inputs
containing 'ignore previous instructions'"). These rules are exploitable: an attacker who
reads the deployed skill — or infers its rules from black-box probing — can craft inputs
that satisfy the skill's benign criteria while still executing an injection.

**Novel claim:** Prompt injection literature studies evasion of classifiers, not of learned
skill documents. SkillOpt literature doesn't study post-deployment adversarial exposure at
all. The transparency that makes skill documents auditable also makes them attackable.
This is the first study of the security/transparency tradeoff in skill-based agents.

**What we need:**
- Phase 2 (base loop) + Phase 5 (robustness probe)
- Parse `edit_apply_report.json` to extract the learned rules explicitly
- For each rule, generate adversarial inputs that bypass it: semantic paraphrases, encoding tricks, indirect instruction patterns
- Metrics: per-rule bypass rate, overall post-optimization detection rate under adversarial probing vs. naive inputs

**Potential finding:** Rules that are specific and brittle (exact phrase matching) are
highly exploitable; rules that are abstract and structural are more robust but harder to
learn. The optimizer converges toward specific rules because they produce clean training
signal — creating a systematic exploitability bias in skill optimization.

**Target venue:** IEEE S&P or USENIX Security (security + ML track), or arXiv
**Status:** Blocked on Phase 2 + 5

---

## 4. Preference-Based Validation for Hard-to-Score Tasks

**Hypothesis:** Replacing the scalar scorer in SkillOpt's validation gate with a pairwise
LLM judge (given two skills, which produces better outputs?) extends skill optimization to
tasks where correctness is subjective or multi-dimensional — and converges to similar skills
as scorer-gated optimization when both are available.

**Novel claim:** SkillOpt's own future work section flags this gap: "extending to
preference-based feedback or reward-free validation." This is the direct implementation
and empirical test of that direction. If preference gating converges comparably to scorer
gating, it unlocks skill optimization for domains where human labels are the only signal —
including the original SOC investigation use case that motivated this project.

**What we need:**
- Phase 2 + Phase 7 (preference-based validation)
- Pairwise judge: Claude evaluates which of two skill documents produces better classified outputs on five examples
- Run on same prompt injection task where scalar scorer is available (ground truth comparison)
- Metrics: convergence rate, final accuracy, skill document similarity between gating modes

**Potential finding:** Preference gating converges to comparable final accuracy but takes
~1.5–2x as many epochs (noisier gate). On tasks where the scorer is available, the
preference-gated skill is slightly shorter and more general — the judge penalizes
over-specific rules that the binary scorer rewards. On hard tasks without a scorer,
preference gating is the only viable path.

**Target venue:** EMNLP 2026 (industry track or findings), or arXiv preprint
**Status:** Blocked on Phase 2 + 7

---

## 5. Pareto Efficiency of Skill Documents

**Hypothesis:** Adding a length penalty to SkillOpt's edit-ranking step reveals a Pareto
frontier between classification accuracy and skill document size. Shorter skills generalize
better on held-out distributions and are less exploitable, at a measurable accuracy cost.
The linguistic style of accepted edits correlates with where a skill lands on this frontier.

**Novel claim:** SkillOpt reports final skill sizes (300–2000 tokens) but never optimizes
for compactness or studies length as a variable. No paper has plotted the accuracy/size
tradeoff for learned skill documents. The practical implication is significant: a
practitioner can choose where to sit on the frontier based on their generalization vs.
accuracy requirements.

**What we need:**
- Phase 2 + Phase 8 (Pareto + style analysis)
- Sweep: run optimization with length penalty weights [0, 0.1, 0.3, 0.5, 1.0]; record final accuracy and skill token count per setting
- Style analysis: categorize edits in accepted skills (imperative, declarative, specific, abstract); measure correlation with accuracy and size
- Metric: Pareto frontier plot, style composition per Pareto point

**Potential finding:** The Pareto frontier has a sharp knee — small penalty weight reduces
skill size by 30-40% with <5% accuracy loss. Beyond the knee, accuracy drops sharply.
Compact, general skills use abstract structural rules; large, accurate skills accumulate
specific pattern-matching rules. The style analysis reveals that the optimizer naturally
prefers specificity — the length penalty is the only mechanism that pushes toward
generalization.

**Target venue:** arXiv preprint, or EMNLP Findings
**Status:** Blocked on Phase 2 + 8

---

## Dependency map

```
Phase 2 (base loop)  ──► Ideas 1, 2, 3, 4, 5 (all blocked here)
Phase 3 (adversarial validation)  ──► Idea 1
Phase 4 (forgetting)              ──► Idea 2
Phase 5 (robustness probe)        ──► Idea 3
Phase 7 (preference validation)   ──► Idea 4
Phase 8 (Pareto + style)          ──► Idea 5
```

**Natural first paper: Ideas 1 + 2 + 3** — the three-assumption stress-test framed as a
single contribution: *"Robust Self-Evolving Agent Skills: What Happens When SkillOpt's
Assumptions Break?"* Ideas 4 and 5 are the follow-on or expanded version.

**Blog series:**
- Post 1 (after Phase 2): mechanism explainer — how the base loop works, what the skill document looks like before and after
- Post 2 (after Phase 5): the three broken assumptions — adversarial validation, forgetting, robustness
- Post 3 (after Phase 8): what makes a skill document efficient — Pareto frontier + style analysis
