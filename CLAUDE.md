# crucible

Self-evolving agent skill optimizer — learns compact, auditable skill documents through adversarial feedback, bounded edits, and a strict validation gate. Stress-tests the core assumptions of the SkillOpt paradigm.

**GitHub:** `github.com/wfullen/crucible`
**Thesis:** Agent skills encoded as text can be optimized without touching model weights. But the optimization loop makes three implicit assumptions nobody has tested: that the validation distribution stays honest, that the task distribution stays stable, and that the learned rules aren't exploitable. crucible builds the loop, then breaks each assumption deliberately.

**Deliverables:** Research blog series (3 posts) + arXiv preprint targeting NeurIPS/ICLR agents track.

---

## What this project does

Given a task with an automatic scorer, an initial skill document, and a frozen target model, crucible runs an optimization loop that:
1. Samples trajectory batches with the current skill
2. Reflects on failures and successes to propose structured add/delete/replace edits
3. Ranks and clips edits to a bounded budget (textual learning rate)
4. Accepts edits only when they strictly improve a held-out validation score
5. Stores rejected edits as negative evidence to prevent repeated mistakes
6. Protects a slow-update region for durable, epoch-level lessons

Primary task: **prompt injection detection** — binary classification with automatic scoring, natural distribution shift axes (attack style), and an inherently adversarial domain that makes the red-team module trivial to motivate. Extensible to any security task with a labeled dataset.

Novel contributions layered on top of the base loop:
- **Adversarial validation gate**: red-team LLM generates harder test cases as the skill improves, preventing the gate from going stale
- **Skill forgetting study**: measures what happens when task distribution shifts mid-optimization
- **Adversarial robustness probe**: exploits learned skill rules using the same attack patterns the skill was trained to detect
- **Comparison point**: runs adversarial validation on DSPy to check whether the finding is framework-specific

---

## Phased Roadmap

### Phase 1 — Foundation
- [ ] Project scaffold: `pyproject.toml`, directory structure, `__init__.py` stubs
- [ ] `adapters/base.py`: `TaskAdapter` ABC, `Task` and `Trajectory` dataclasses
- [ ] `data/loaders.py`: load `deepset/prompt-injections` from HuggingFace; load PINT benchmark for final test set
- [ ] `adapters/security/prompt_injection.py`: `PromptInjectionAdapter` with `train_tasks()`, `selection_tasks()`, `test_tasks()`, `shifted_tasks(attack_type)` — splits by attack type metadata

### Phase 2 — Core optimizer
- [ ] `core/skill.py`: `SkillDocument` — immutable, `apply_edits()` returns new instance, slow region fenced by `SLOW_UPDATE_START/END` markers
- [ ] `core/editor.py`: `EditProposer.propose()` from failure/success trajectories + rejected buffer; `rank_and_clip()` to budget
- [ ] `core/validator.py`: `ValidationGate.score()` + strict `accept()` — ties rejected, no drift on noise
- [ ] `core/optimizer.py`: main loop — epochs, minibatches, gate, rejected-edit buffer, epoch-boundary slow update
- [ ] `experiments/run_base.py`: end-to-end run; logs skill snapshots + `edit_apply_report.json` per step
- [ ] Confirm baseline result: skill improves over no-skill on prompt injection detection

### Phase 3 — Adversarial validation (Gap 1)
- [ ] `adversarial/redteam.py`: red-team LLM generates new injection variants targeting current skill's known rules
- [ ] `experiments/configs/adversarial_validation.yaml`: fully specified experiment config
- [ ] `experiments/run_adversarial.py`: same loop with adversarial gate replacing static selection split
- [ ] Ablation: static gate vs. adversarial gate — convergence curve comparison
- [ ] Result: does adversarial gate prevent overfitting to validation distribution?

### Phase 4 — Skill forgetting under distribution shift (Gap 2)
- [ ] `experiments/configs/forgetting.yaml`
- [ ] `experiments/run_forgetting.py`: train on `direct` injection → shift to `jailbreak` → shift to `context_manipulation`
- [ ] Metrics: accuracy per phase, accuracy drop at each transition, recovery curve if re-optimized
- [ ] Ablation: with vs. without slow update layer — does the protected region help retention?

### Phase 5 — Adversarial robustness probe (Gap 10)
- [ ] `adversarial/robustness.py`: parse `edit_apply_report.json` to extract learned rules; generate adversarial inputs that exploit each rule
- [ ] `experiments/configs/robustness.yaml`
- [ ] `experiments/run_robustness.py`: probe trained skill with crafted inputs; report per-rule exploit rate
- [ ] Result: which learned rules are exploitable, and what structural feature makes them so?

### Phase 6 — Framework comparison
- [ ] `comparison/dspy_run.py`: same prompt injection task + scorer through DSPy optimizer
- [ ] Run adversarial validation experiment against DSPy baseline
- [ ] Result: is the adversarial validation finding framework-specific or general?

### Phase 7 — Preference-based validation
- [ ] `experiments/configs/preference.yaml`
- [ ] Swap `ValidationGate` scorer for pairwise LLM judge: given two skill documents, which produces better outputs?
- [ ] `experiments/run_preference.py`: compare convergence vs. scorer-gated loop on same task
- [ ] Result: does preference gating converge to the same skill? When does it diverge?

### Phase 8 — Pareto frontier + style analysis
- [ ] `analysis/pareto.py`: add length penalty term to `rank_and_clip()`; trace accuracy vs. skill size across penalty weights
- [ ] `analysis/style.py`: extract linguistic features of accepted vs. rejected edits — imperative vs. declarative, specificity, rule length
- [ ] `experiments/run_pareto.py`
- [ ] Result: Pareto frontier plot + characterization of what makes a skill document efficient

### Phase 9 — Visualization + reporting
- [ ] Convergence curve: score across epochs, no-skill baseline as flat line
- [ ] Skill evolution timeline: annotated `best_skill.md` at each accepted edit
- [ ] Edit provenance: full `edit_apply_report.json` readable per-run
- [ ] Pareto plot: accuracy vs. skill token count across penalty settings

---

## Conventions

- Conventional commits: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`
- Tag each phase: `v0.1.0`, `v0.2.0`, etc.
- `SkillDocument` is immutable — `apply_edits()` always returns a new instance
- All experiments fully specified by a yaml in `experiments/configs/` — reproducible with one command
- `logs/` captures a skill snapshot + `edit_apply_report.json` per run
- Model-agnostic adapter interface: `TaskAdapter` is the only thing that changes per task
- Target model: Claude (any tier); optimizer model: Claude Sonnet or above
- Test set is PINT benchmark only — never used for training or gate calibration

## Related work in this repo

- `~/llm-security/` — 17 notebooks covering prompt injection, jailbreaking, tool abuse, red teaming. Foundation for the task domain and adversarial modules.
- `~/agentic-ai/` — 12 notebooks on agent fundamentals, memory, multi-agent patterns, evaluation. Foundation for the agent loop design.
- `~/ml-security/` — 20 notebooks on adversarial examples, backdoor attacks, data poisoning. Informs the robustness probe design.
- `~/llm-reliability/` — calibration and drift detection toolkit. Drift detection methodology carries over to the forgetting study.

## Current Status

Phase 1 — not started. Start here.
