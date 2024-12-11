# application/interfaces/results_aggregator.py
from typing import List, Dict, Any, Protocol, Optional
from abc import ABC, abstractmethod
from datetime import datetime, timedelta

class AggregationPeriod(Enum):
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"

class AggregationFunction(Protocol):
    def aggregate(self, values: List[Any]) -> Any:
        """Aggregate a list of values."""
        pass

class ResultsAggregator(ABC):
    @abstractmethod
    def aggregate(
        self,
        results: List[Any],
        group_by: List[str],
        metrics: List[str],
        period: Optional[AggregationPeriod] = None,
        custom_aggregations: Optional[Dict[str, AggregationFunction]] = None
    ) -> Dict[str, Any]:
        """
        Aggregate results by specified dimensions.
        
        Args:
            results: List of results to aggregate
            group_by: Fields to group by
            metrics: Metrics to calculate
            period: Optional time period for temporal aggregation
            custom_aggregations: Optional custom aggregation functions
            
        Returns:
            Aggregated results
        """
        pass

    @abstractmethod
    def get_time_series(
        self,
        results: List[Any],
        metric: str,
        start_time: datetime,
        end_time: datetime,
        interval: timedelta,
        group_by: Optional[List[str]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get time series data for a metric.
        
        Args:
            results: Results to analyze
            metric: Metric to track
            start_time: Start of time range
            end_time: End of time range
            interval: Time interval for data points
            group_by: Optional grouping dimensions
            
        Returns:
            Time series data points
        """
        pass