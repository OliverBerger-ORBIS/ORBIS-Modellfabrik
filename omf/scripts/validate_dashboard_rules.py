#!/usr/bin/env python3
"""
Minimaler Validator für das Streamlit-Dashboard.

Prüft in den Komponenten:
- Keine Client-Erzeugung in Komponenten (OmfMqttClient, mqtt.Client)
- Keine Factory-/Callback-Verdrahtung in Komponenten
- Keine subscribe("#") und keine super-breiten Abos
- Kein st.rerun() in Komponenten
- Optional: render_* muss einen Parameter "client" oder "mqtt_client" haben

Anpassen (falls Pfade anders sind):
  COMPONENTS_DIR, DASHBOARD_ENTRY
"""

from __future__ import annotations

import argparse
import ast
from dataclasses import dataclass
from pathlib import Path

# --- Projektpfade (falls nötig anpassen) ---
COMPONENTS_DIR = Path("omf/dashboard/components")
DASHBOARD_ENTRY = Path("omf/dashboard/omf_dashboard.py")

# --- Feste Namensregeln (keine Config nötig) ---
CLIENT_CLASS_NAME = "OmfMqttClient"
PAHO_CLIENT_FULL = {"mqtt.Client", "paho.mqtt.client.Client"}
FORBIDDEN_TOPICS = {"#"}
BROAD_PATTERNS = ("module/#", "fts/#", "/j1/txt/1/#", "ccu/#")  # sehr grob, reicht i.d.R.
FACTORY_HINTS = ("omf_mqtt_factory", "mqtt_factory", "session_manager", "ensure_dashboard_client", "create_log_buffer")

# UI-Refresh Regeln
ALLOWED_REFRESH_FUNCTIONS = {"request_refresh"}  # Erlaubte Refresh-Funktionen
FORBIDDEN_REFRESH_FUNCTIONS = {"st.rerun"}  # Verbotene Refresh-Funktionen

ALLOWED_RENDER_PARAM_NAMES = {"client", "mqtt_client"}  # erzwingen wir optional


@dataclass
class Violation:
    kind: str  # ERROR | WARN
    code: str  # Regelcode
    file: str
    line: int
    message: str
    line_txt: str | None = None


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _call_qualname(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_call_qualname(node.value)}.{node.attr}"
    return node.__class__.__name__


class Checker(ast.NodeVisitor):
    def __init__(self, filename: Path, source: str, enforce_render_param: bool):
        self.filename = filename
        self.source = source
        self.lines = source.splitlines()
        self.violations: list[Violation] = []
        self.enforce_render_param = enforce_render_param
        self.func_defs: list[ast.FunctionDef] = []
        self.import_map: dict[str, str] = {}

    def add(self, kind: str, code: str, node: ast.AST, msg: str):
        ln = getattr(node, "lineno", 1)
        txt = self.lines[ln - 1].strip() if 1 <= ln <= len(self.lines) else None
        self.violations.append(Violation(kind, code, str(self.filename), ln, msg, txt))

    # --- Imports (nur für simple Alias-Auflösung) ---
    def visit_Import(self, node: ast.Import):
        for a in node.names:
            self.import_map[a.asname or a.name] = a.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        # R014: Relative Imports (generell)
        if node.level > 0:
            self.add(
                "WARN",
                "R014",
                node,
                "Relativer Import erkannt - verwende absolute Imports für externe Module: from omf.dashboard.tools.logging_config import get_logger",
            )

        mod = node.module or ""
        for a in node.names:
            name = a.asname or a.name
            full = f"{mod}.{a.name}" if mod else a.name
            self.import_map[name] = full
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self.func_defs.append(node)
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call):
        callee = _call_qualname(node.func)
        # Alias-Auflösung (nur eine Ebene)
        callee_root = callee.split(".")[0]
        callee = self.import_map.get(callee_root, callee_root) + (
            "" if "." not in callee else callee[callee.find(".") :]
        )

        # R001: Client-Erzeugung in Komponenten (OmfMqttClient)
        if callee.split(".")[-1] == CLIENT_CLASS_NAME:
            self.add("ERROR", "R001", node, f"{CLIENT_CLASS_NAME} darf in Komponenten nicht instanziiert werden.")

        # R002: paho.mqtt.client.Client in Komponenten
        if callee in PAHO_CLIENT_FULL:
            self.add("ERROR", "R002", node, "paho.mqtt.client.Client darf in Komponenten nicht instanziiert werden.")

        # R003: Factory-/Session-Manager-Hinweise (heuristisch, einfach)
        if any(h in callee for h in FACTORY_HINTS):
            self.add("ERROR", "R003", node, f"Factory/Session-Manager-Aufruf in Komponente erkannt: {callee}")

        # R005: Direkte connect/reconnect-Aufrufe
        if callee.endswith(".connect") or callee.endswith(".reconnect"):
            self.add("WARN", "R005", node, f"Direkter Aufruf {callee} in Komponente vermeiden.")

        # R006/R012/R009: subscribe / subscribe_many
        short = callee.split(".")[-1]
        if short in {"subscribe", "subscribe_many"}:
            # Erlaubnis für Message Center: subscribe("#") ist OK
            is_message_center = "message_center.py" in str(self.filename)

            # erster Parameter als String?
            if node.args:
                a0 = node.args[0]
                # subscribe("topic")
                if isinstance(a0, ast.Constant) and isinstance(a0.value, str):
                    topic = a0.value.strip()
                    if topic in FORBIDDEN_TOPICS:
                        if is_message_center:
                            self.add(
                                "WARN",
                                "R006",
                                node,
                                "subscribe('#') im Message Center (erlaubt, aber prüfen ob nötig).",
                            )
                        else:
                            self.add("ERROR", "R006", node, "subscribe('#') ist verboten (außer im Message Center).")
                    elif topic.endswith("/#") or any(bp in topic for bp in BROAD_PATTERNS):
                        self.add("WARN", "R012", node, f"Sehr breiter Subscribe erkannt: '{topic}'")
                # subscribe_many([...])
                if isinstance(a0, (ast.List, ast.Tuple)):
                    for el in a0.elts:
                        if isinstance(el, ast.Constant) and isinstance(el.value, str):
                            t = el.value.strip()
                            if t in FORBIDDEN_TOPICS:
                                if is_message_center:
                                    self.add(
                                        "WARN",
                                        "R006",
                                        node,
                                        "subscribe_many mit '#' im Message Center (erlaubt, aber prüfen ob nötig).",
                                    )
                                else:
                                    self.add(
                                        "ERROR",
                                        "R006",
                                        node,
                                        "subscribe_many mit '#' ist verboten (außer im Message Center).",
                                    )
                            elif t.endswith("/#") or any(bp in t for bp in BROAD_PATTERNS):
                                self.add("WARN", "R012", node, f"Sehr breiter Subscribe erkannt: '{t}'")
            # generelle Warnung (nicht für Message Center)
            if not is_message_center:
                self.add(
                    "WARN", "R009", node, "subscribe in Komponenten gefunden (besser: Interesse/Buffer deklarieren)."
                )

        # R008: Callback-Wiring in Komponenten
        if callee.endswith(".message_callback_add") or callee.endswith(".message_callback_remove"):
            self.add("ERROR", "R008", node, f"{callee} darf in Komponenten nicht verwendet werden.")

        # R015: UI-Refresh Regeln
        if callee in FORBIDDEN_REFRESH_FUNCTIONS:
            self.add("ERROR", "R015", node, f"{callee} ist verboten - verwende request_refresh() statt st.rerun()")
        elif callee in ALLOWED_REFRESH_FUNCTIONS:
            # request_refresh() ist erlaubt - keine Meldung
            pass

        # R016: Logging-System Regeln
        if callee == "configure_logging" and not self._is_in_init_function():
            self.add("ERROR", "R016", node, "configure_logging() nur in _init_logging_once() verwenden")

        self.generic_visit(node)

    def visit_Attribute(self, node: ast.Attribute):
        # R007: st.rerun()
        if isinstance(node.value, ast.Name) and node.value.id == "st" and node.attr == "rerun":
            self.add("ERROR", "R007", node, "st.rerun() darf in Komponenten nicht verwendet werden.")
        self.generic_visit(node)

    def _is_in_init_function(self) -> bool:
        """Prüft ob wir in einer _init_logging_once Funktion sind"""
        for fn in self.func_defs:
            if fn.name == "_init_logging_once":
                return True
        return False

    def post_check_renderer_params(self):
        if not self.enforce_render_param:
            return
        for fn in self.func_defs:
            if fn.name.startswith("render_"):
                names = [a.arg for a in fn.args.args]
                if not any(n in ALLOWED_RENDER_PARAM_NAMES for n in names):
                    self.add(
                        "ERROR", "R013", fn, f"'{fn.name}' sollte einen Parameter 'client' oder 'mqtt_client' besitzen."
                    )


def scan(path: Path, include_dashboard: bool, enforce_render_param: bool) -> list[Violation]:
    py_files = list(path.rglob("*.py"))
    if include_dashboard and DASHBOARD_ENTRY.exists():
        py_files.append(DASHBOARD_ENTRY)

    all_v: list[Violation] = []
    for f in sorted(py_files):
        if "__pycache__" in str(f):
            continue
        try:
            src = _read(f)
            tree = ast.parse(src, filename=str(f))
        except Exception as e:
            all_v.append(Violation("ERROR", "PARSE", str(f), 1, f"Syntax/Read-Fehler: {e}"))
            continue
        chk = Checker(f, src, enforce_render_param)
        chk.visit(tree)
        # Fallback-Stringcheck für st.rerun(
        for i, line in enumerate(src.splitlines(), start=1):
            if "st.rerun(" in line.replace(" ", ""):
                chk.violations.append(Violation("ERROR", "R007", str(f), i, "st.rerun() gefunden.", line.strip()))
        chk.post_check_renderer_params()
        all_v.extend(chk.violations)
    return all_v


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--path", default=str(COMPONENTS_DIR), help="Komponenten-Basisordner")
    ap.add_argument("--include-dashboard", action="store_true", help=f"Auch {DASHBOARD_ENTRY} prüfen")
    ap.add_argument("--strict", action="store_true", help="WARN als Fehler werten (Exit 1)")
    ap.add_argument("--loose", action="store_true", help="ERROR als WARN werten (nur WARN blockiert)")
    ap.add_argument("--no-render-param-check", action="store_true", help="render_* Param-Pflicht abschalten")
    args = ap.parse_args()

    comp_dir = Path(args.path)
    if not comp_dir.exists():
        print(f"[validate] Pfad nicht gefunden: {comp_dir}")
        raise SystemExit(2)

    violations = scan(
        comp_dir, include_dashboard=args.include_dashboard, enforce_render_param=not args.no_render_param_check
    )

    # --loose: ERROR als WARN behandeln
    if args.loose:
        for v in violations:
            if v.kind == "ERROR":
                v.kind = "WARN"

    errors = [v for v in violations if v.kind == "ERROR"]
    warns = [v for v in violations if v.kind == "WARN"]

    if not violations:
        print("✔ Keine Verstöße gefunden.")
    else:
        print("=== Dashboard Rules Report ===")
        for v in violations:
            print(f"[{v.kind}] {v.code} {v.file}:{v.line} :: {v.message}")
            if v.line_txt:
                print(f"   {v.line_txt}")
        print(f"\nSummary: {len(errors)} Fehler, {len(warns)} Warnungen")

    exit_nonzero = bool(errors or (args.strict and warns))
    raise SystemExit(1 if exit_nonzero else 0)


if __name__ == "__main__":
    main()
