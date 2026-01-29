"""
Agents Package (V3.0)
Professional investment analysis agents with specialized perspectives
"""
from .base_agent import BaseAgent
from .business_analyst import BusinessAnalyst
from .value_hunter import ValueHunter
from .growth_analyzer import GrowthAnalyzer
from .risk_examiner import RiskExaminer
from .cio_synthesizer import CIOSynthesizer

# Legacy prompts (for backward compatibility)
from .prompts import (
    VALUE_HUNTER_PROMPT,
    GROWTH_VISIONARY_PROMPT,
    SKEPTIC_PROMPT,
    CIO_PROMPT
)

__all__ = [
    'BaseAgent',
    'BusinessAnalyst',
    'ValueHunter',
    'GrowthAnalyzer',
    'RiskExaminer',
    'CIOSynthesizer',
    'VALUE_HUNTER_PROMPT',
    'GROWTH_VISIONARY_PROMPT',
    'SKEPTIC_PROMPT',
    'CIO_PROMPT'
]
