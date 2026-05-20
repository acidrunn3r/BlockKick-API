from pydantic import BaseModel, ConfigDict, Field


class TransactionResponse(BaseModel):
    """A single blockchain transaction indexed by the API."""

    tx_id: str = Field(..., description="SHA-256 transaction identifier")
    tx_type: str = Field(
        ..., description="Transfer | CreateProject | FundProject | Coinbase"
    )
    from_address: str | None = Field(None, description="Sender wallet address")
    to_address: str | None = Field(None, description="Recipient wallet address")
    amount: int | None = Field(
        None, description="Coin amount (Transfer/FundProject/Coinbase)"
    )
    project_id: str | None = Field(
        None, description="Project ID (CreateProject/FundProject)"
    )
    block_height: int = Field(..., description="Block containing this transaction")
    timestamp: int = Field(..., description="Unix timestamp of the transaction")

    model_config = ConfigDict(from_attributes=True)
