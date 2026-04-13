"""Data analysis orchestrator.

Generates and optionally runs analysis scripts from measurement data.
Two-tier approach: template-based for known types, LLM for custom.
"""
from __future__ import annotations
import logging
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent / "templates"

class AnalysisResult(BaseModel):
    measurement_type: str
    script_path: str
    script_source: str
    figures: list[str] = []
    extracted_values: dict[str, Any] = {}

@dataclass
class Analyzer:
    output_dir: Path = Path("./data/analysis")

    def generate_script(
        self,
        data_path: Path,
        measurement_type: str,
    ) -> str:
        """Generate analysis script from built-in template."""
        template_path = TEMPLATES_DIR / f"{measurement_type.lower()}.py"
        if not template_path.exists():
            raise FileNotFoundError(
                f"No analysis template for '{measurement_type}'. "
                f"Available: {[p.stem for p in TEMPLATES_DIR.glob('*.py')]}"
            )

        template = template_path.read_text()
        # Replace placeholder with actual data path
        script = template.replace("{{DATA_PATH}}", str(data_path))
        script = script.replace("{{OUTPUT_DIR}}", str(self.output_dir))

        return script

    def save_script(self, script: str, name: str) -> Path:
        """Save generated script to output directory."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        script_path = self.output_dir / f"{name}_analysis.py"
        script_path.write_text(script)
        logger.info("Saved analysis script to %s", script_path)
        return script_path

    def run_script(self, script_path: Path, timeout: int = 120) -> AnalysisResult:
        """Execute analysis script in subprocess with timeout."""
        result = subprocess.run(
            ["python", str(script_path)],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(script_path.parent),
        )

        if result.returncode != 0:
            logger.error("Analysis script failed:\n%s", result.stderr)
            raise RuntimeError(f"Analysis failed: {result.stderr[:500]}")

        # Find generated figures
        figures = list(self.output_dir.glob("*.png")) + list(self.output_dir.glob("*.pdf"))

        return AnalysisResult(
            measurement_type=script_path.stem.replace("_analysis", ""),
            script_path=str(script_path),
            script_source=script_path.read_text(),
            figures=[str(f) for f in figures],
        )
