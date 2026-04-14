"""End-to-end experiment flow orchestrator."""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from lab_harness.config import Settings
from lab_harness.orchestrator.decider import decide_measurement
from lab_harness.orchestrator.folder import open_folder, prepare_data_folder
from lab_harness.orchestrator.session import ExperimentSession

logger = logging.getLogger(__name__)


class ExperimentFlow:
    """Guides a user through a complete experiment from question to data."""

    def __init__(self, settings: Settings, data_root: Path | None = None):
        self.settings = settings
        self.data_root = data_root or Path("./data")
        self.session = ExperimentSession()

    async def run(self, direction: str = "", material: str = "") -> ExperimentSession:
        """Run the full experiment flow. Returns the completed session."""
        print("\n" + "=" * 60)
        print("  LabAgent — Guided Experiment")
        print("=" * 60 + "\n")

        # Step 1: Check API key
        if not (self.settings.model.api_key or self.settings.model.base_url):
            print("⚠  No AI model configured. Run: labharness setup\n")
            print("Continuing with rule-based fallback...\n")

        # Step 2: Gather user input
        self.session.direction = direction or input("Research direction (e.g. 'transport', 'photovoltaics'): ").strip()
        self.session.material = material or input("Sample material (e.g. 'Si wafer', 'Fe/MgO'): ").strip()

        # Step 3: Parallel — literature search + instrument scan
        print("\n[Step 1/6] Searching literature and scanning instruments (parallel)...")
        literature, instruments = await asyncio.gather(
            self._search_literature(),
            self._scan_instruments(),
            return_exceptions=True,
        )
        if isinstance(literature, Exception):
            logger.warning("Literature search failed: %s", literature)
            literature = {}
        if isinstance(instruments, Exception):
            logger.warning("Instrument scan failed: %s", instruments)
            instruments = []
        self.session.literature = literature if isinstance(literature, dict) else {}
        self.session.instruments = instruments if isinstance(instruments, list) else []

        print(f"  ✓ Found {len(self.session.instruments)} instrument(s)")
        if self.session.literature.get("source_papers"):
            print(f"  ✓ Found {len(self.session.literature['source_papers'])} relevant reference(s)")
        else:
            print("  ✓ Literature context ready")

        # Step 4: AI decides measurement type
        print("\n[Step 2/6] AI deciding measurement type...")
        decision = decide_measurement(
            self.session.direction,
            self.session.material,
            self.session.instruments,
            self.session.literature,
        )
        self.session.measurement_type = decision.get("measurement_type", "IV")
        self.session.measurement_reason = decision.get("reasoning", "")
        print(f"  → {self.session.measurement_type}")
        print(f"  Reasoning: {self.session.measurement_reason}")

        # Step 5: Generate plan
        print("\n[Step 3/6] Generating measurement plan...")
        from lab_harness.planning.boundary_checker import check_boundaries
        from lab_harness.planning.plan_builder import build_plan_from_template

        try:
            plan = build_plan_from_template(
                self.session.measurement_type,
                sample_description=self.session.material,
            )
            validation = check_boundaries(plan)
            self.session.plan = plan.model_dump()
            self.session.validation = validation.model_dump()
            print(f"  ✓ {plan.total_points} points, safety: {validation.decision.value.upper()}")
        except FileNotFoundError:
            print(f"  ⚠  No template for {self.session.measurement_type}, falling back to IV")
            self.session.measurement_type = "IV"
            plan = build_plan_from_template("IV", sample_description=self.session.material)
            validation = check_boundaries(plan)
            self.session.plan = plan.model_dump()
            self.session.validation = validation.model_dump()

        # Step 6: Prepare data folder
        folder = prepare_data_folder(self.data_root, self.session.folder_name)
        self.session.data_folder = str(folder)
        print(f"\n[Step 4/6] Data folder: {folder}")

        # Step 7: Wait for user to set up circuit
        print("\n[Step 5/6] Please connect your instruments as follows:")
        for inst in self.session.instruments[:5]:
            print(f"  - {inst.get('vendor', '?')} {inst.get('model', '?')} at {inst.get('resource', '?')}")
        input("\nPress Enter when your circuit is ready... ")

        # Step 8: Launch measurement (simulated for now)
        print("\n[Step 6/6] Running measurement...")
        data_file = await self._run_measurement(plan, folder)
        self.session.data_file = str(data_file)
        self.session.measurement_completed = True
        print(f"  ✓ Saved: {data_file}")

        # Step 9: Analyze with literature context
        print("\n[Analysis] Analyzing results with literature context...")
        await self._analyze(data_file, folder)

        # Step 10: Save summary + offer to open folder
        self.session.save_summary(folder)
        print("\n" + "=" * 60)
        print(f"  Experiment complete! Data in: {folder}")
        print("=" * 60 + "\n")

        if input("Open data folder? [Y/n]: ").strip().lower() != "n":
            open_folder(folder)

        return self.session

    async def _search_literature(self) -> dict:
        from lab_harness.literature.paper_pilot_client import PaperPilotClient

        client = PaperPilotClient()
        # Use direction as measurement hint
        ctx = await client.search_for_protocol(self.session.direction or "IV", self.session.material)
        return ctx.model_dump() if hasattr(ctx, "model_dump") else dict(ctx.__dict__)

    async def _scan_instruments(self) -> list[dict]:
        from lab_harness.discovery.visa_scanner import scan_visa_instruments

        loop = asyncio.get_event_loop()
        instruments = await loop.run_in_executor(None, scan_visa_instruments)
        return [i.model_dump() for i in instruments]

    async def _run_measurement(self, plan, folder: Path) -> Path:
        """Simulated measurement execution. Real execution requires driver integration."""
        import csv
        import random

        data_file = folder / "raw_data.csv"

        # Simulate data based on plan's x_axis
        x_axis = plan.x_axis
        points = []
        for i in range(plan.total_points):
            x = x_axis.start + i * x_axis.step
            # Generic noisy response
            y = 0.001 * x + random.gauss(0, 0.0001)
            points.append({x_axis.label: x, "measurement": y})

        with open(data_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[x_axis.label, "measurement"])
            writer.writeheader()
            writer.writerows(points)

        return data_file

    async def _analyze(self, data_file: Path, folder: Path) -> None:
        """Run analysis with literature-aware interpretation."""
        from lab_harness.analysis.analyzer import Analyzer

        analyzer = Analyzer(output_dir=folder)
        try:
            result = analyzer.analyze(
                data_file,
                self.session.measurement_type,
                use_ai=False,
                interpret=True,
            )
            self.session.analysis_result = result.model_dump()
            self.session.ai_interpretation = result.ai_interpretation
            print(f"  ✓ Analysis script: {Path(result.script_path).name}")
            if result.figures:
                print(f"  ✓ Figures: {len(result.figures)}")
            if result.ai_interpretation:
                print("\n  AI Interpretation:")
                print(f"  {result.ai_interpretation[:300]}...")
        except Exception as e:
            logger.warning("Analysis failed: %s", e)
            print(f"  ⚠  Analysis encountered an issue: {e}")

        # Generate next-step suggestions
        self._suggest_next_steps(folder)

    def _suggest_next_steps(self, folder: Path) -> None:
        """AI-generated suggestions for next experiments."""
        if not (self.settings.model.api_key or self.settings.model.base_url):
            return
        try:
            from lab_harness.llm.router import LLMRouter

            router = LLMRouter(config=self.settings.model)
            prompt = (
                f"Based on this {self.session.measurement_type} measurement on {self.session.material}, "
                f"suggest 3 concrete follow-up experiments. Be brief (under 100 words)."
            )
            resp = router.complete(
                [
                    {"role": "system", "content": "You are a helpful experimental physicist."},
                    {"role": "user", "content": prompt},
                ]
            )
            text = resp["choices"][0]["message"]["content"].strip()
            self.session.next_step_suggestions = text
            (folder / "next_steps.md").write_text(text, encoding="utf-8")
            print("\n  Next step suggestions saved to next_steps.md")
        except Exception:
            pass
