from pydantic import BaseModel
from enum import Enum


class TransactionType(str, Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"
    STOP = "stop"
    STOP_LIMIT = "stop_limit"


class ProductType(str, Enum):
    CNC = "cnc"
    INTRADAY = "intraday"
    MARGIN = "margin"
    DELIVERY = "delivery"


class Order(BaseModel):
    order_id: str
    symbol: str
    status: str
    transaction_type: TransactionType
    order_type: OrderType
    product_type: ProductType
    quantity: int
    price: float
    timestamp: str


class Trade(BaseModel):
    trade_id: str
    order_id: str
    symbol: str
    transaction_type: TransactionType
    quantity: int
    price: float
    timestamp: str


class Position(BaseModel):
    symbol: str
    quantity: int
    product_type: ProductType
    exchange: str
    instrument_type: str
    realised_pnl: float


class OrderResponse(BaseModel):
    order_id: str
    status: str
