from abc import ABC, abstractmethod
from typing import Any, Dict


class IBrokerAdapter(ABC):
    """
    Abstract base class for all broker adapters.
    """

    @abstractmethod
    async def initiate_login(self, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiates the login process for a broker.
        """
        raise NotImplementedError

    @abstractmethod
    async def complete_login(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Completes the login process for a broker.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_portfolio(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Retrieves the portfolio from a broker.
        """
        raise NotImplementedError
