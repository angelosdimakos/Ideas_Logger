"""Zephyrus unified CLI (v2)
==========================
A single command‑line entry point that surfaces **all existing back‑end
capabilities discovered in the parsed *docstring_summary.json*.  The CLI now
covers four pillars:

1.  **Idea Logger**       – capture & retrieve raw notes
2.  **Summariser**        – AI docstring‑style summaries
3.  **Knowledge‑Graph**   – build / query graph (stub until impl.)
4.  **RefactorGuard**     – guarded code generation / refactoring
5.  **CI Analytics**      – code‑quality reports + metric trends
6.  **Developer helpers** – Git branch suggester

It is built with **Typer** and keeps zero logic inside: every verb delegates to
functions/classes already present in the codebase, or – where a module is still
future work – a soft stub prints a helpful TODO but does not break the flow.

Install & run:
--------------
$ poetry install  # or pip install -e .[cli]
$ zephyrus --help

Examples:
---------
• Log + summarise + KG update + guarded implementation + CI report one‑liner:

    zephyrus pipe \
        --note "Graph prompts reduce hallucinations" \
        --main Research --sub LLMs \
        --refactor "def add(a: int, b: int) -> int" \
        --ci-report

• Stand‑alone guarded function generation:

    zephyrus generate "def slugify(text: str) -> str"

pyproject entry‑point:
----------------------
[tool.poetry.scripts]
zephyrus = "scripts.cli.cli:app"
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer

################################################################################
#  Dynamic imports (real modules or graceful stubs)                             #
################################################################################


def _safe_import(path: str, stub_attrs: Optional[dict] = None):
    try:
        module = __import__(path, fromlist=["*"])
    except ModuleNotFoundError:  # provide minimal stub
        module = type(path, (), stub_attrs or {})()  # type: ignore[arg-type]
    return module


# Core logging & summarisation
core_mod = _safe_import("scripts.core.core")
ctrl_mod = _safe_import("scripts.gui.gui_controller")

# CI analytics
orchestrator = _safe_import("scripts.ci_analyzer.orchestrator")
ci_trends_mod = _safe_import("scripts.ci_analyzer.ci_trends")

# Dev helper
dev_commit_mod = _safe_import(
    "scripts.dev_commit", {"switch_to_new_branch": lambda: print("TODO: Git helper not available")}
)

# RefactorGuard (future module)
refactor_mod = _safe_import(
    "scripts.refactor.refactor_guard",
    {
        "RefactorGuard": type(
            "RefactorGuard",
            (),
            {
                "__init__": lambda self, *a, **k: None,
                "generate_function": lambda self, signature, graph_context=None, tests_path=None, max_tokens=256: (
                    f"# TODO RefactorGuard stub for {signature}\n"
                    f"def {signature.split('(')[0]}(*args, **kwargs):\n    pass\n"
                ),
            },
        ),
    },
)

# Knowledge‑graph builder (future)
kg_mod = _safe_import(
    "scripts.kg.kg_builder",
    {
        "build_graph": lambda since=None: print("TODO: build KG (stub)"),
        "query_graph": lambda entity: [],
    },
)

################################################################################
#  CLI setup                                                                    #
################################################################################
app = typer.Typer(add_completion=False, help="Zephyrus Logger CLI v2 🪐")

################################################################################
#  Helpers                                                                      #
################################################################################


def _core() -> "core_mod.ZephyrusLoggerCore":  # type: ignore[name-defined]
    return core_mod.ZephyrusLoggerCore(script_dir=Path.cwd())


def _ctrl() -> "ctrl_mod.GUIController":  # type: ignore[name-defined]
    return ctrl_mod.GUIController(logger_core=None, script_dir=str(Path.cwd()))


################################################################################
#  Idea logging & summarisation                                                 #
################################################################################


@app.command()
def log(
    note: str = typer.Argument(..., help="Raw idea text"),
    main: str = typer.Option("General", help="Main category"),
    sub: str = typer.Option("General", help="Sub‑category"),
    summarize_immediately: bool = typer.Option(False, "--summarize/--no-summarize"),
) -> None:
    """Write a raw idea; (optionally) summarise immediately."""
    ok = _ctrl().log_entry(main, sub, note)
    if not ok:
        typer.echo("❌ Failed to log idea", err=True)
        raise typer.Exit(1)
    typer.echo("✅ Idea logged")
    if summarize_immediately:
        _core().force_summary_all()
        typer.echo("📝 Summary generated")


@app.command()
def summarize() -> None:
    """Summarise *all* unsummarised entries."""
    _core().force_summary_all()
    typer.echo("📝 All pending summaries created")


################################################################################
#  Knowledge graph operations                                                   #
################################################################################

kg_app = typer.Typer(help="Knowledge‑graph operations (stub)")
app.add_typer(kg_app, name="kg")


@kg_app.command("build")
def kg_build(
    since: Optional[str] = typer.Option(None, help="Only build from notes after YYYY‑MM‑DD")
) -> None:
    kg_mod.build_graph(since=since)


@kg_app.command("query")
def kg_query(entity: str = typer.Argument(..., help="Entity or node label")) -> None:
    res = kg_mod.query_graph(entity)
    typer.echo(json.dumps(res, indent=2, ensure_ascii=False))


################################################################################
#  RefactorGuard – guarded code generation                                      #
################################################################################


@app.command("generate")
def generate_function(
    signature: str = typer.Argument(..., help="Python signature e.g. 'add(a: int, b: int) -> int'"),
    context_entity: Optional[str] = typer.Option(None, help="KG entity to give as context"),
    tests: Optional[Path] = typer.Option(
        None, help="Optional pytest file used as acceptance guard"
    ),
    max_tokens: int = typer.Option(256, help="Token limit for LLM"),
) -> None:
    guard = refactor_mod.RefactorGuard()
    graph_ctx = {"entity": context_entity} if context_entity else None
    code = guard.generate_function(signature, graph_ctx, tests_path=tests, max_tokens=max_tokens)
    typer.echo(code)


################################################################################
#  Search & coverage                                                            #
################################################################################


@app.command()
def search(
    query: str = typer.Argument(...),
    mode: str = typer.Option("summary", help="summary | raw"),
    k: int = 5,
) -> None:
    core = _core()
    hits = (
        core.search_summaries(query, k)
        if mode.startswith("summary")
        else core.search_raw_logs(query, k)
    )
    typer.echo(json.dumps(hits, indent=2, ensure_ascii=False))


@app.command()
def coverage() -> None:
    typer.echo(json.dumps(_ctrl().get_coverage_data(), indent=2))


################################################################################
#  Index maintenance                                                            #
################################################################################


@app.command("rebuild-index")
def rebuild_index(index: str = typer.Option("all", help="summary | raw | all")) -> None:
    tracker = _core().summary_tracker
    if index in ("summary", "all") and getattr(tracker, "summary_indexer", None):
        tracker.summary_indexer.rebuild()
        typer.echo("🔄 Summary index rebuilt")
    if index in ("raw", "all") and getattr(tracker, "raw_indexer", None):
        tracker.raw_indexer.rebuild()
        typer.echo("🔄 Raw index rebuilt")


################################################################################
#  CI analytics                                                                 #
################################################################################

ci_app = typer.Typer(help="CI code‑quality commands")
app.add_typer(ci_app, name="ci")


@ci_app.command("report")
def ci_report(
    audit: Path = typer.Option(Path("refactor_audit.json")),
    out: Path = typer.Option(Path("ci_summary.md")),
) -> None:
    data = orchestrator.load_audit(str(audit))
    md = orchestrator.generate_ci_summary(data)
    orchestrator.save_summary(md, str(out))
    typer.echo(f"📄 CI report saved → {out}")


@ci_app.command("trends")
def ci_trends(
    audit: Path = typer.Option(Path("refactor_audit.json")),
    history: Path = typer.Option(Path(".ci-history/last_metrics.json")),
) -> None:
    curr = ci_trends_mod.extract_metrics(ci_trends_mod.load_audit(str(audit)))
    prev = ci_trends_mod.load_previous_metrics(str(history))
    delta = ci_trends_mod.compare_metrics(curr, prev)
    ci_trends_mod.print_comparison(curr, delta)
    ci_trends_mod.save_metrics(curr, str(history))


################################################################################
#  Dev helper                                                                   #
################################################################################


@app.command("git-new-branch")
def git_new_branch() -> None:  # pragma: no cover
    dev_commit_mod.switch_to_new_branch()


################################################################################
#  One‑shot pipeline                                                            #
################################################################################


@app.command()
def pipe(
    note: str = typer.Argument(..., help="Idea text"),
    main: str = "General",
    sub: str = "General",
    refactor: Optional[str] = typer.Option(None, help="Signature for guarded generation"),
    ci_report: bool = typer.Option(False, help="Run ci report at the end"),
) -> None:
    """Complete flow: log → summarise → KG build → optional guarded generation → optional CI report."""
    # 1) Log idea
    if not _ctrl().log_entry(main, sub, note):
        typer.echo("❌ Couldn’t log idea", err=True)
        raise typer.Exit(1)

    # 2) Summaries
    _core().force_summary_all()

    # 3) KG build (stub ok)
    kg_mod.build_graph()

    # 4) Optional guarded generation
    if refactor:
        code = refactor_mod.RefactorGuard().generate_function(refactor)
        typer.echo("\n# ── RefactorGuard output ──\n" + code)

    # 5) Optional CI report
    if ci_report:
        ci_report()  # reuse Typer callback – called with defaults

    typer.echo("✅ Pipeline finished")


################################################################################

if __name__ == "__main__":  # pragma: no cover
    app()
