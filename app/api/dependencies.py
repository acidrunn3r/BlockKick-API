from app.core.client import BlockchainClient, client


async def get_blockchain_client() -> BlockchainClient:
    """Provide the singleton blockchain client to endpoint handlers."""
    return client
