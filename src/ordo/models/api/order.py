from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class ExchangeType(str, Enum):
    NSE = "NSE"
    BSE = "BSE"


class InstrumentSegmentType(str, Enum):
    EQUITY = "EQUITY"
    OPTIDX = "OPTIDX"
    OPTSTK = "OPTSTK"
    FUTIDX = "FUTIDX"
    FUTSTK = "FUTSTK"
    OPTCUR = "OPTCUR"
    FUTCUR = "FUTCUR"


class TransactionType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    SL = "SL"
    SL_M = "SL-M"


class ProductType(str, Enum):
    DELIVERY = "DELIVERY"
    INTRADAY = "INTRADAY"
    MARGIN = "MARGIN"
    OVERNIGHT = "OVERNIGHT"
    MTF = "MTF"
    COLL_SELL = "COLL-SELL"
    ENCASH = "ENCASH"


class ValidityType(str, Enum):
    DAY = "DAY"
    IOC = "IOC"
    GTD = "GTD"


class OptionType(str, Enum):
    CALL = "CE"
    PUT = "PE"


class OrderStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    OPEN = "open"


class Order(BaseModel):
    order_id: str = Field(..., description="Unique order identifier")
    symbol: str = Field(..., description="Instrument symbol")
    status: OrderStatus = Field(..., description="Current status of the order")
    transaction_type: TransactionType = Field(
        ..., description="Type of transaction (BUY/SELL)"
    )
    order_type: OrderType = Field(
        ..., description="Type of order (MARKET, LIMIT, etc.)"
    )
    product_type: ProductType = Field(
        ..., description="Product type (CNC, INTRADAY, etc.)"
    )
    quantity: int = Field(..., description="Quantity of the instrument")
    price: float = Field(
        ..., description="Price at which the order was placed or executed"
    )
    timestamp: datetime = Field(
        ..., description="Timestamp of the order in ISO 8601 format"
    )


class Trade(BaseModel):
    trade_id: str = Field(..., description="Unique trade identifier from HDFC API.")
    order_id: str = Field(..., description="Related order identifier from HDFC API.")
    exchange: str = Field(..., description="Exchange where the trade occurred.")
    product: ProductType = Field(
        ..., description="Product type of the trade (e.g., CNC, INTRADAY)."
    )
    average_price: float = Field(..., description="Average price of the trade.")
    filled_quantity: int = Field(
        ..., description="Quantity of the instrument filled in the trade."
    )
    exchange_order_id: str = Field(..., description="Order ID from the exchange.")
    transaction_type: TransactionType = Field(
        ..., description="Type of transaction (BUY/SELL)."
    )
    fill_timestamp: datetime = Field(
        ..., description="Timestamp when the trade was filled in ISO 8601 format."
    )
    security_id: str = Field(..., description="Security identifier.")
    company_name: str = Field(..., description="Name of the company/instrument.")


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
