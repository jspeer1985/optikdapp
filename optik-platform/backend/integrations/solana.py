import os
import logging
from typing import Dict, Any, Optional
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair
import json

logger = logging.getLogger(__name__)

class SolanaIntegration:
    """
    Handles interactions with the Solana blockchain.
    """
    
    def __init__(self, rpc_url: Optional[str] = None):
        self.rpc_url = rpc_url or os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")
        self.client = AsyncClient(self.rpc_url)
        
        # Load platform keypair if available
        self.keypair = None
        pk_str = os.getenv("SOLANA_WALLET_PRIVATE_KEY")
        if pk_str:
            try:
                # Handle JSON array format [1,2,3...]
                if pk_str.startswith("["):
                    self.keypair = Keypair.from_bytes(bytes(json.loads(pk_str)))
                else:
                    # Handle Base58 string format (Phantom)
                    try:
                        import base58
                        self.keypair = Keypair.from_base58_string(pk_str)
                    except ImportError:
                        logger.warning("base58 package not found. Falling back to solders only.")
                        self.keypair = Keypair.from_bytes(bytes.fromhex(pk_str) if len(pk_str) == 128 else None)
            except Exception as e:
                logger.error(f"Failed to load Solana keypair: {e}")

    async def get_balance(self, address: str) -> float:
        """Fetch SOL balance for an address."""
        try:
            pubkey = Pubkey.from_string(address)
            response = await self.client.get_balance(pubkey)
            return response.value / 10**9
        except Exception as e:
            logger.error(f"Error fetching balance for {address}: {e}")
            return 0.0

    async def transfer_sol(self, to_address: str, amount_sol: float) -> str:
        """Perform a real SOL transfer on-chain."""
        if not self.keypair:
            raise Exception("No keypair loaded. Check SOLANA_WALLET_PRIVATE_KEY.")

        try:
            from solana.rpc.types import TxOpts
            from solana.transaction import Transaction
            from solders.system_program import TransferParams, transfer
            
            to_pubkey = Pubkey.from_string(to_address)
            lamports = int(amount_sol * 10**9)
            
            # Create transfer instruction
            instruction = transfer(
                TransferParams(
                    from_pubkey=self.keypair.pubkey(),
                    to_pubkey=to_pubkey,
                    lamports=lamports
                )
            )
            
            # Get latest blockhash
            recent_blockhash = await self.client.get_latest_blockhash()
            
            # Build transaction
            txn = Transaction()
            txn.add(instruction)
            txn.recent_blockhash = recent_blockhash.value.blockhash
            
            # Send and confirm
            response = await self.client.send_transaction(
                txn, 
                self.keypair,
                opts=TxOpts(skip_preflight=True)
            )
            return str(response.value)
        except Exception as e:
            logger.error(f"SOL Transfer failed: {e}")
            raise e

    async def require_min_balance(self, min_sol: float) -> float:
        if not self.keypair:
            raise RuntimeError("No keypair loaded. Check SOLANA_WALLET_PRIVATE_KEY.")

        balance = await self.get_balance(str(self.keypair.pubkey()))
        if balance < min_sol:
            raise RuntimeError(f"Insufficient platform funds. Balance {balance} SOL < {min_sol} SOL")
        return balance

    async def deploy_store_account(self, merchant_pubkey: str) -> Dict[str, Any]:
        """
        Deprecated: use SmartContractDeployer.initialize_store with OPTIK_PROGRAM_ID + IDL.
        """
        raise RuntimeError("Use SmartContractDeployer.initialize_store for on-chain merchant setup.")
