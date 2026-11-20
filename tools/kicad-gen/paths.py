"""Repo-relative paths so the generators run from any clone."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
KOUT = os.path.join(REPO, "kicad")                  # KiCad projects live here
REDRAW = os.path.join(REPO, "tools", "redraw")      # PDF redraw toolkit (shared geometry)
FR = os.environ.get("FREEROUTING_JAR", os.path.join(REPO, "tools", "freerouting-1.9.0.jar"))
