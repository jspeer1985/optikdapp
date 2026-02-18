import logging
import asyncio
from typing import Dict, Any, List
from agents.deployer_agent import SolanaDeployerAgent
from utils.smart_contract_deployer import SmartContractDeployer

logger = logging.getLogger(__name__)

class DeploymentPipeline:
    """
    Orchestrates the deployment of a converted store onto the Solana blockchain.
    """
    def __init__(self):
        self.deployer_agent = SolanaDeployerAgent()
        self.contract_tool = SmartContractDeployer()

    async def run(self, job_id: str, conversion_data: Dict[str, Any], config: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Starting LIVE deployment pipeline for job {job_id}")
        
        try:
            from integrations.solana import SolanaIntegration
            solana = SolanaIntegration()

            # 1. Ensure platform wallet has funds for deployment
            min_balance = float(config.get("min_balance_sol", 0.05))
            await solana.require_min_balance(min_balance)

            # 2. Initialize the on-chain store
            merchant_wallet = config.get("wallet_address")
            if not merchant_wallet:
                return {"status": "failed", "error": "TREASURY_WALLET is required"}

            merchant_result = await self.contract_tool.initialize_store(
                merchant_wallet=merchant_wallet,
                fee_bps=config.get("fee_bps", 300)
            )
            
            # 3. Handle NFT Collection deployment
            collection_info = None
            if config.get("enable_nft", True):
                collection_info = await self.contract_tool.deploy_collection(
                    name=conversion_data.get("store_name", "Optik Store"),
                    symbol=config.get("collection_symbol", "OPTIK")
                )
                
                # 4. BACKING STEP: Pair the collection with $OPTIK
                if collection_info and "mint" in collection_info:
                    backing_info = await self.contract_tool.pair_with_optik_coin(
                        collection_mint=collection_info["mint"],
                        initial_backing_amount=config.get("backing_amount", 1000.0) # Default 1000 $OPTIK
                    )
                    collection_info["backing"] = backing_info

            return {
                "status": "success",
                "mode": "live",
                "network": "devnet",
                "tx_hash": merchant_result.get("tx_hash"),
                "merchant_pda": merchant_result.get("merchant"),
                "collection": collection_info,
                "backing_mode": "OPTIK_BACKED",
                "dapp_url": f"https://optik.store/{job_id}"
            }
        except Exception as e:
            logger.error(f"LIVE Deployment pipeline failed: {e}")
            return {"status": "failed", "error": str(e)}
