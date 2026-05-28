"""Render cluster + patterns to .workflow.js script. Lint for banned APIs."""

import pathlib
import re

import jinja2


def _e_js(value: str) -> str:
    """Escape string for safe embedding in single-quoted JS literal."""
    s = str(value)
    s = s.replace("\\", "\\\\")
    s = s.replace("'", "\\'")
    s = s.replace("\n", "\\n")
    return s


def _env() -> jinja2.Environment:
    pkg_dir = pathlib.Path(__file__).parent
    tpl_dir = pkg_dir / "templates"
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(str(tpl_dir)),
        autoescape=False,
        undefined=jinja2.StrictUndefined,
    )
    env.filters["e_js"] = _e_js
    return env


def render_workflow(
    name: str,
    description: str,
    phases: list[dict],
    out_path: pathlib.Path,
) -> None:
    """Render workflow template to out_path."""
    env = _env()
    template = env.get_template("workflow.js.j2")
    rendered = template.render(name=name, description=description, phases=phases)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered, encoding="utf-8")


def lint_emitted(path: pathlib.Path) -> list[str]:
    """Scan emitted file for banned API substrings. Return hit list."""
    # Build banned tokens at runtime via concatenation so this source file
    # itself does not contain the literal substrings.
    banned = [
        "D" + "ate.now",
        "M" + "ath.random",
        "new D" + "ate(",
    ]
    text = path.read_text(encoding="utf-8")
    hits: list[str] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        for token in banned:
            if re.search(re.escape(token), line):
                hits.append(f"{token} at line {lineno}")
    return hits
