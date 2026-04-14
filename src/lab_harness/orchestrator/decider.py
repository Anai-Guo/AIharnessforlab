"""AI decides measurement type from direction + material + instruments + literature."""

from __future__ import annotations

import json
import logging

logger = logging.getLogger(__name__)

SYSTEM_DECIDE = """\
You are an expert experimental physicist. Given a research direction,
a material sample, available instruments, and literature context,
decide the most appropriate measurement type.

Available measurement types and when to use them:
- IV: Basic current-voltage characterization (any conductor/semiconductor)
- RT: Resistance vs temperature (needs temp controller; for phase transitions)
- HALL: Hall effect (needs gaussmeter; for carrier density/mobility)
- MR: Magnetoresistance (needs gaussmeter; for magnetic samples)
- AHE: Anomalous Hall effect (needs gaussmeter; for magnetic thin films)
- SOT: Spin-orbit torque (needs pulse source + gaussmeter; for spintronics)
- CV: Capacitance-voltage (needs LCR meter; for semiconductors/dielectrics)
- DELTA: Ultra-low resistance delta mode (needs K6221 + K2182A)
- HIGH_R: High resistance (needs electrometer; for insulators)
- CYCLIC_VOLTAMMETRY: CV scan (needs potentiostat; for electrochemistry)
- EIS: Impedance spectroscopy (needs LCR/impedance analyzer)
- PHOTO_IV: Solar cell IV under illumination
- SEEBECK: Seebeck coefficient (needs temperature gradient)
- TC: Superconducting transition (needs cryostat + temp controller)

Respond with valid JSON only:
{
  "measurement_type": "<TYPE>",
  "reasoning": "<why this measurement fits the direction, material, and available instruments>",
  "confidence": <float 0-1>
}
"""


def decide_measurement(
    direction: str,
    material: str,
    instruments: list[dict],
    literature: dict | None = None,
) -> dict:
    """Use AI to decide the best measurement type. Returns {type, reasoning, confidence}."""
    from lab_harness.config import Settings
    from lab_harness.llm.router import LLMRouter

    settings = Settings.load()
    if not (settings.model.api_key or settings.model.base_url):
        # Fallback: rule-based decision
        return _rule_based_decision(direction, material, instruments)

    router = LLMRouter(config=settings.model)

    user_msg = f"Direction: {direction}\nMaterial: {material}\n\n"
    user_msg += "Available instruments:\n"
    for inst in instruments:
        user_msg += f"- {inst.get('vendor', '?')} {inst.get('model', '?')}\n"

    if literature and literature.get("suggested_parameters"):
        user_msg += f"\nLiterature suggests: {json.dumps(literature.get('suggested_parameters', {}))}\n"

    response = router.complete(
        [
            {"role": "system", "content": SYSTEM_DECIDE},
            {"role": "user", "content": user_msg},
        ]
    )
    text = response["choices"][0]["message"]["content"].strip()

    # Strip markdown fences if present
    if text.startswith("```"):
        text = text[text.index("\n") + 1 :]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        logger.warning("Could not parse decision response; using fallback")
        return _rule_based_decision(direction, material, instruments)


def _rule_based_decision(
    direction: str,
    material: str,
    instruments: list[dict],
) -> dict:
    """Rule-based fallback when AI not available."""
    direction_lower = direction.lower()
    material_lower = material.lower()

    models = " ".join(inst.get("model", "").lower() for inst in instruments)
    has_gauss = "425" in models or "455" in models
    has_temp = "335" in models or "340" in models or "350" in models
    has_lcr = "e4980" in models
    has_pulse = "6221" in models

    if has_pulse and has_gauss and "spin" in direction_lower:
        return {
            "measurement_type": "SOT",
            "reasoning": "Pulse source + gaussmeter + spin direction → SOT",
            "confidence": 0.7,
        }
    if has_gauss and ("magnetic" in material_lower or "ferro" in material_lower or "magnetic" in direction_lower):
        return {"measurement_type": "AHE", "reasoning": "Gaussmeter + magnetic material → AHE", "confidence": 0.7}
    if has_gauss:
        return {"measurement_type": "HALL", "reasoning": "Gaussmeter available → Hall effect", "confidence": 0.6}
    if has_temp:
        return {"measurement_type": "RT", "reasoning": "Temperature controller → R-T", "confidence": 0.6}
    if has_lcr:
        return {"measurement_type": "CV", "reasoning": "LCR meter → C-V", "confidence": 0.6}
    return {"measurement_type": "IV", "reasoning": "Default: basic IV characterization", "confidence": 0.5}
