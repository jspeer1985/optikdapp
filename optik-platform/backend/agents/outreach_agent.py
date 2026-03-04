import logging
import json
from typing import Dict, Optional
from datetime import datetime
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from utils.database import db

logger = logging.getLogger("SalesmanAgent")

class OutreachAgent:
    def __init__(self):
        self.llm = ChatAnthropic(model="claude-3-5-sonnet-20240620", temperature=0.7)
        self.pitch_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are the Lead Growth Agent for Optik Platform. 
            Optik converts traditional E-commerce stores into Web3 Solana DApps.
            
            Your goal is to write a highly compelling, professional, and personalized outreach message 
            to a store owner whose store has already been converted into a live demo DApp.
            
            Key Value Props:
            - Accept SOL/USDC and Credit Cards with 0% setup fee.
            - Brand new audience in the Solana ecosystem.
            - Low transaction fees compared to Shopify/Stripe.
            - NFT-based loyalty programs are ready to go.
            
            Keep the message concise, exciting, and include the custom DApp URL.
            """),
            ("human", """Generate a pitch for:
            Store Name: {store_name}
            Original URL: {store_url}
            Deployed DApp URL: {dapp_url}
            Tier: {tier}
            """)
        ])

    async def generate_pitch(self, job_id: str) -> Optional[Dict]:
        """Generates a personalized pitch for a converted job."""
        # 1. Get job data
        job = await db.get_job_status(job_id)
        if not job or job.get("status") != "deployed":
            logger.warning(f"Job {job_id} is not deployed yet. Cannot generate pitch.")
            return None

        store_name = job.get("store_name") or job.get("store_url", "").split("/")[-1]
        
        # 2. Fire LLM to generate pitch
        try:
            chain = self.pitch_prompt | self.llm
            response = await chain.ainvoke({
                "store_name": store_name,
                "store_url": job.get("store_url"),
                "dapp_url": f"http://localhost:3003/dapps/{job_id}", # In dev, use local link
                "tier": job.get("tier", "Basic")
            })
            
            pitch_content = response.content
            
            # 3. Store pitch in DB (we might need a column for this or a separate table)
            # For now, let's just log it and return it
            return {
                "job_id": job_id,
                "store_name": store_name,
                "pitch": pitch_content,
                "generated_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Failed to generate pitch for {job_id}: {e}")
            return None

    async def run_outreach_cycle(self):
        """Finds all deployed jobs without a pitch and generates them."""
        query = "SELECT id FROM jobs WHERE status = 'deployed'"
        jobs = await db.database.fetch_all(query=query)
        
        results = []
        for job_row in jobs:
            job_id = job_row["id"]
            logger.info(f"Generating pitch for successfully deployed store: {job_id}")
            pitch_data = await self.generate_pitch(job_id)
            if pitch_data:
                results.append(pitch_data)
        
        return results

# Singleton instance
outreach_agent = OutreachAgent()
