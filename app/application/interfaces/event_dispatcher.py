# application/interfaces/event_dispatcher.py
from typing import Any, Dict, Optional, Protocol
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum

class EventPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"

class Event(Protocol):
    @property
    def name(self) -> str:
        """Get the event name."""
        pass

    @property
    def data(self) -> Dict[str, Any]:
        """Get the event data."""
        pass

    @property
    def timestamp(self) -> datetime:
        """Get the event timestamp."""
        pass

class EventHandler(Protocol):
    def handle(self, event: Event) -> None:
        """Handle an event."""
        pass

class EventDispatcher(ABC):
    @abstractmethod
    def dispatch(
        self,
        event: Event,
        priority: EventPriority = EventPriority.NORMAL,
        async_dispatch: bool = False
    ) -> None:
        """
        Dispatch an event to registered handlers.
        
        Args:
            event: Event to dispatch
            priority: Event priority
            async_dispatch: Whether to dispatch asynchronously
        """
        pass

    @abstractmethod
    def register(
        self,
        event_name: str,
        handler: EventHandler,
        priority: EventPriority = EventPriority.NORMAL
    ) -> None:
        """
        Register an event handler.
        
        Args:
            event_name: Name of event to handle
            handler: Event handler
            priority: Handler priority
        """
        pass

    @abstractmethod
    def unregister(
        self,
        event_name: str,
        handler: EventHandler
    ) -> bool:
        """
        Unregister an event handler.
        
        Args:
            event_name: Name of event
            handler: Handler to unregister
            
        Returns:
            True if handler was unregistered
        """
        pass