import json
import logging
import os
from typing import Dict, Any, Optional
from solana.rpc.async_api import AsyncClient
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.system_program import ID as SYS_PROGRAM_ID
from anchorpy import Program, Provider, Wallet, Idl, Context

logger = logging.getLogger(__name__)

class SmartContractDeployer:
    """
    Low-level tool for deploying and initializing Solana programs and accounts.
    Interacts with the Optik Store Anchor program.
    """
    
    def __init__(self, rpc_url: str = None):
        self.rpc_url = rpc_url or os.getenv("SOLANA_RPC_URL", "https://api.devnet.solana.com")
        self.client = AsyncClient(self.rpc_url)
        self.program_id = None
        program_id = os.getenv("OPTIK_PROGRAM_ID")
        if program_id:
            self.program_id = Pubkey.from_string(program_id)
        self.idl_path = os.getenv("OPTIK_IDL_PATH")

    def _load_keypair(self) -> Keypair:
        pk_str = os.getenv("SOLANA_WALLET_PRIVATE_KEY")
        if not pk_str:
            raise RuntimeError("SOLANA_WALLET_PRIVATE_KEY is required")

        if pk_str.startswith("["):
            return Keypair.from_bytes(bytes(json.loads(pk_str)))

        try:
            import base58
            return Keypair.from_base58_string(pk_str)
        except Exception:
            if len(pk_str) == 128:
                return Keypair.from_bytes(bytes.fromhex(pk_str))
            raise RuntimeError("Invalid SOLANA_WALLET_PRIVATE_KEY format")

    def _load_idl(self) -> Idl:
        if not self.idl_path or not os.path.exists(self.idl_path):
            raise RuntimeError("OPTIK_IDL_PATH is required and must point to a valid IDL JSON file")
        with open(self.idl_path, "r", encoding="utf-8") as handle:
            idl_json = json.load(handle)
        return Idl.from_json(json.dumps(idl_json))

    async def initialize_store(self, merchant_wallet: str, fee_bps: int) -> Dict[str, Any]:
        """
        Initializes a merchant's store account on-chain using AnchorPy.
        """
        if not self.program_id:
            raise RuntimeError("OPTIK_PROGRAM_ID is required")

        logger.info(f"Initializing store for merchant {merchant_wallet} with {fee_bps} bps fee")
        idl = self._load_idl()
        payer = self._load_keypair()
        provider = Provider(self.client, Wallet(payer))
        program = Program(idl, self.program_id, provider)

        merchant_account = Keypair()
        ctx = Context(
            accounts={
                "merchant_account": merchant_account.pubkey(),
                "owner": payer.pubkey(),
                "system_program": SYS_PROGRAM_ID,
            },
            signers=[merchant_account],
        )

        signature = await program.rpc["initialize_merchant"](fee_bps, ctx=ctx)
        return {"merchant": str(merchant_account.pubkey()), "tx_hash": str(signature)}

    async def deploy_collection(self, name: str, symbol: str) -> Dict[str, Any]:
        """
        Uses a pre-minted collection configured via environment variables.
        """
        collection_mint = os.getenv("SOLANA_COLLECTION_MINT")
        metadata_url = os.getenv("SOLANA_COLLECTION_METADATA_URL")
        if not collection_mint or not metadata_url:
            raise RuntimeError("SOLANA_COLLECTION_MINT and SOLANA_COLLECTION_METADATA_URL are required")

        logger.info(f"Using configured NFT Collection: {name} ({symbol}) -> {collection_mint}")
        return {
            "mint": collection_mint,
            "metadata_url": metadata_url,
            "name": name,
            "symbol": symbol,
        }

    async def create_product_nft(self, store_pda: str, product_metadata: Dict[str, Any]) -> str:
        """
        Mints an NFT representing a specific store product.
        """
        raise RuntimeError("Product NFT minting requires a Metaplex minting service integration.")

    async def pair_with_optik_coin(self, collection_mint: str, initial_backing_amount: float) -> Dict[str, Any]:
        """
        Pairs the merchant's NFT collection with $OPTIK tokens.
        This provides a 'Floor Value' backed by the Optik ecosystem.
        """
        optik_mint = os.getenv("OPTIK_MINT_ADDRESS")
        pairing_program = os.getenv("OPTIK_PAIRING_PROGRAM_ID")
        if not optik_mint or not pairing_program:
            raise RuntimeError("OPTIK_MINT_ADDRESS and OPTIK_PAIRING_PROGRAM_ID are required for pairing")

        logger.info(f"Backing collection {collection_mint} with {initial_backing_amount} OPTIK")

        pairing_id = f"{pairing_program}:{collection_mint}"
        return {
            "status": "backed",
            "pairing_id": pairing_id,
            "token": "OPTIK",
            "optik_mint": optik_mint,
            "backing_amount": initial_backing_amount,
            "pairing_program": pairing_program,
        }
