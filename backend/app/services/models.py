"""Interfaces that allow future validated models to replace rule-based engines."""
from abc import ABC, abstractmethod
from typing import Any, Dict, List
from .performance_engine import calculate_performance
from .injury_engine import calculate_injury_risk


class PerformancePredictionModel(ABC):
    @abstractmethod
    def predict(self, frames: List[Dict[str, Any]]) -> Dict[str, Any]: ...


class RiskPredictionModel(ABC):
    @abstractmethod
    def predict(self, frames: List[Dict[str, Any]]) -> Dict[str, Any]: ...


class RuleBasedPerformanceModel(PerformancePredictionModel):
    def predict(self, frames):
        return calculate_performance(frames)


class RuleBasedRiskModel(RiskPredictionModel):
    def predict(self, frames):
        return calculate_injury_risk(frames)
