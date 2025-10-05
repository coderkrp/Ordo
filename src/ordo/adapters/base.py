from abc import ABC, abstractmethod
from typing import Any, Dict, List

from ordo.models.api.order import Order, Trade, Position, OrderResponse
from ordo.models.api.user import Profile
from ordo.models.api.portfolio import Holding, Portfolio


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
    async def get_portfolio(self, session_data: Dict[str, Any]) -> Portfolio:
        """
        Retrieves the portfolio from a broker.
        """
        raise NotImplementedError

    @abstractmethod
    async def modify_order(
        self, session_data: Dict[str, Any], order_id: str, **kwargs
    ) -> OrderResponse:
        """
        Modifies an existing order.
        """
        raise NotImplementedError

    @abstractmethod
    async def cancel_order(
        self, session_data: Dict[str, Any], order_id: str
    ) -> OrderResponse:
        """
        Cancels an existing order.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_order_book(self, session_data: Dict[str, Any]) -> List[Order]:
        """
        Retrieves the order book.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_trade_book(self, session_data: Dict[str, Any]) -> List[Trade]:
        """
        Retrieves the trade book.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_profile(self, session_data: Dict[str, Any]) -> Profile:
        """
        Retrieves the user profile.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_holdings(self, session_data: Dict[str, Any]) -> List[Holding]:
        """
        Retrieves the user's holdings.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_positions(self, session_data: Dict[str, Any]) -> List[Position]:
        """
        Retrieves the user's positions.
        """
        raise NotImplementedError
