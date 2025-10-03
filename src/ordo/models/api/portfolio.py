from pydantic import BaseModel, Field
from typing import List


class Holding(BaseModel):
    symbol: str = Field(..., description="Trading symbol of the instrument.")
    quantity: int = Field(..., description="The quantity of the instrument held.")
    ltp: float = Field(..., description="Last Traded Price of the instrument.")
    avg_price: float = Field(
        ..., description="Average acquisition price of the instrument."
    )
    pnl: float = Field(..., description="Profit and Loss for the holding.")
    day_pnl: float = Field(..., description="Profit and Loss for the current day.")
    value: float = Field(
        ..., description="Current market value of the holding (quantity * ltp)."
    )


class Funds(BaseModel):
    available_balance: float = Field(
        ..., description="The total available balance in the account."
    )
    margin_used: float = Field(..., description="The total margin utilized for trades.")
    total_balance: float = Field(
        ..., description="The total balance in the account (available + margin)."
    )


class Portfolio(BaseModel):
    holdings: List[Holding] = Field(
        ..., description="List of all holdings in the portfolio."
    )
    funds: Funds = Field(..., description="Details of the funds in the account.")
    total_pnl: float = Field(
        ..., description="Total Profit and Loss for the portfolio."
    )
    total_day_pnl: float = Field(
        ..., description="Total Profit and Loss for the current day for the portfolio."
    )
    total_value: float = Field(
        ..., description="Total current market value of the portfolio."
    )
