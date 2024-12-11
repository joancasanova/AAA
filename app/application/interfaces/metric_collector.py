# application/interfaces/metric_collector.py
from typing import Dict, Any, List, Optional, Protocol
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum

class MetricType(Enum):
    COUNTER = "counter"
    GAUGE = "gauge"
    HISTOGRAM = "histogram"
    SUMMARY = "summary"

class MetricValue(Protocol):
    def get_value(self) -> float:
        """Get the current value of the metric."""
        pass

    def update(self, value: float) -> None:
        """Update the metric value."""
        pass

class MetricCollector(ABC):
    @abstractmethod
    def record(
        self,
        name: str,
        value: float,
        metric_type: MetricType,
        labels: Optional[Dict[str, str]] = None,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Record a metric value.
        
        Args:
            name: Metric name
            value: Metric value
            metric_type: Type of metric
            labels: Optional key-value pairs for metric labeling
            timestamp: Optional timestamp for the metric
        """
        pass

    @abstractmethod
    def get_metrics(
        self,
        name: Optional[str] = None,
        metric_type: Optional[MetricType] = None,
        labels: Optional[Dict[str, str]] = None
    ) -> Dict[str, MetricValue]:
        """
        Get current metric values.
        
        Args:
            name: Optional metric name filter
            metric_type: Optional metric type filter
            labels: Optional labels filter
            
        Returns:
            Dictionary of metric names to their current values
        """
        pass