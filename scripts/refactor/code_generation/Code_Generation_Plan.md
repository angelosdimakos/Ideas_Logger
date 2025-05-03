RefactorGuard-Powered Code-Generation

Full implementation roadmap (8 weeks, 6 engineers‐days per week)

    Goal: turn Refactor Guard from a post-hoc auditor into a closed-loop, knowledge-graph-guided, LLM refactor engine that you can invoke from the new zephyrus generate and pipe commands.

Phase 0 Project scaffolding (½ week)
Task	Details
A. Repo re-org	scripts/llm/ (agents + prompts), scripts/sandbox/ (exec isolation), scripts/kg/ (graph OPS)
B. Baseline CI	Flake + Ruff + Black, test matrix: Linux + Mac; add pytest -q tests/guard_loop
C. Feature flags	AppConfig.refactor_guard.enabled, max_retry, complexity_budget, etc.
Phase 1 Δ-sandbox runner (1 week)
Deliverable	Steps
1. SandboxRunner class	• Creates tmpdir/<uuid> • symlinks original package • writes generated code under same module path • manages venv (or pex / pipx run)
2. Test harness	API: SandboxRunner.run_pytest(paths, timeout) → (passed: bool, coverage_json)
3. Security	• Nasty-import blocklist (os, subprocess, socket, etc.) via PYTHONSAFEPATH & AST transform • resource limits with resource.setrlimit
Phase 2 LLM generation agent (1 week)
Deliverable	Steps
1. Prompt templates	templates/refactor.jinja: receives signature, KG snippet, coding-style rules, complexity budget
2. RefactorAgent class	Wrapper around OpenAI/Anthropic/Ollama; returns str code block & model metadata; generate_function(signature, kg_ctx)
3. Retry policy	Exponential back-off, up to N=3; inject Guard feedback (e.g., “Complexity 11—reduce to ≤8”).
4. Unit tests	Mock LLM; assert prompt composition & basic parsing.
Phase 3 Guard loop orchestrator (1 week)

def guarded_generate(signature, kg_ctx, tests):
    for attempt in 0..max_retry:
        code = agent.generate_function(...)
        runner.write(code)
        tests_ok, coverage = runner.run_pytest(tests)
        report = guard.analyze_module(original, generated, coverage)
        if tests_ok and report.pass_all():
            return code, report
        agent.feedback(report)  # prompt injection
    raise GuardFail(report)

Integrates:

    RefactorGuard.analyze_module (API diff + complexity + missing tests)

    attach_coverage_hits feed coverage JSON

    Decision: pass/fail thresholds configurable in AppConfig.refactor_guard.

Phase 4 Knowledge-graph hooks (1 week)
Task	Details
A. KG schema extension	Node types: Function, Concept, File – edges: USES, IMPROVES, REFERS_TO.
B. kg.extract_context(signature)	Returns list of triples & natural-language bullet summary for prompt.
C. Automatic KG update after successful refactor	Add new Function node + IMPROVES link to original.
Phase 5 CLI & GUI integration (½ week)
Command	Behaviour
zephyrus generate	calls guarded_generate; prints code & minimal report JSON.
zephyrus pipe --refactor …	runs full loop; on success appends summary of guard metrics.
GUI “Generate code” panel* (optional)*	Input signature + dropdown for KG entity; progress bar; shows pass/fail badges.
Phase 6 Observability & docs (½ week)

    Logs: structured JSON lines in .zephyrus/logs/refactor_guard.log

    Grafana/Prom metrics: attempts, avg complexity reduction, guard-pass rate

    Docs: tutorial “Write a spec → auto-implementation under guardrails”.

Phase 7 Hardening & beta (1 week)

    Large-file diff: fall back to directory-wide analysis (analyze_directory_recursive).

    Timeout / OOM failsafe in SandboxRunner.

    Parallel builds with xdist when running many tests.

    User study: internal devs try real refactors; collect guard pain-points.

Stretch goals (post-MVP)

    Dynamic tracing - integrate pytest-cov branch coverage + pytest-profiling for perf regression thresholds.

    Mutation testing (e.g., Cosmic-Ray) as an extra guard step.

    Graph-search planner – use KG to select which functions to refactor next (auto-prioritise complexity hotspots).

Resource summary
Role	Est. effort
Lead engineer / architect	8 weeks
Support dev (tests, GUI)	4 weeks
Dev-ops (CI, observability)	1 week
Prompt / ML engineer	1 week