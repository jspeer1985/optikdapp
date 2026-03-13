use anchor_lang::prelude::*;
use anchor_spl::token::{Token, TokenAccount, Mint};

declare_id!("9dKgjdntLkaMpqFoeA4mVMa3gerh9DQbLt4hH2aebANX");

// ─── Constants ───────────────────────────────────────────────────────────────
pub const MAX_ROYALTY_BPS: u16 = 10_000; // 100%
pub const MAX_CREATORS: usize = 5;
pub const PAIRING_SEED: &[u8] = b"pairing";
pub const REGISTRY_SEED: &[u8] = b"registry";

#[program]
pub mod nft_pairer {
    use super::*;

    /// Initialize the global pairing registry for a platform operator
    pub fn initialize_registry(
        ctx: Context<InitializeRegistry>,
        platform_fee_bps: u16,
    ) -> Result<()> {
        require!(
            platform_fee_bps <= 1_000, // max 10% platform fee
            PairingError::FeeTooHigh
        );

        let registry = &mut ctx.accounts.registry;
        registry.authority = ctx.accounts.authority.key();
        registry.platform_fee_bps = platform_fee_bps;
        registry.total_pairings = 0;
        registry.paused = false;
        registry.bump = ctx.bumps.registry;

        emit!(RegistryInitialized {
            authority: registry.authority,
            platform_fee_bps,
        });

        Ok(())
    }

    /// Create a pairing between two NFTs with royalty configuration
    pub fn create_pairing(
        ctx: Context<CreatePairing>,
        params: CreatePairingParams,
    ) -> Result<()> {
        let registry = &ctx.accounts.registry;
        require!(!registry.paused, PairingError::RegistryPaused);

        let pairing = &mut ctx.accounts.pairing;
        pairing.authority = ctx.accounts.authority.key();
        pairing.nft_a_mint = ctx.accounts.nft_a_mint.key();
        pairing.nft_b_mint = ctx.accounts.nft_b_mint.key();
        pairing.royalty_bps = params.royalty_bps;
        pairing.creators = params.creators;
        pairing.metadata_uri = params.metadata_uri;
        pairing.pairing_type = params.pairing_type;
        pairing.created_at = Clock::get()?.unix_timestamp;
        pairing.active = true;
        pairing.total_sales = 0;
        pairing.total_royalties_paid = 0;
        pairing.bump = ctx.bumps.pairing;

        // Increment registry counter
        let registry = &mut ctx.accounts.registry;
        registry.total_pairings = registry
            .total_pairings
            .checked_add(1)
            .ok_or(PairingError::Overflow)?;

        emit!(PairingCreated {
            pairing: ctx.accounts.pairing.key(),
            nft_a_mint: ctx.accounts.nft_a_mint.key(),
            nft_b_mint: ctx.accounts.nft_b_mint.key(),
            royalty_bps: params.royalty_bps,
            authority: ctx.accounts.authority.key(),
        });

        Ok(())
    }

    /// Deactivate a pairing (authority only, irreversible)
    pub fn deactivate_pairing(ctx: Context<UpdatePairing>) -> Result<()> {
        let pairing = &mut ctx.accounts.pairing;
        require!(pairing.active, PairingError::PairingInactive);
        pairing.active = false;

        emit!(PairingDeactivated {
            pairing: ctx.accounts.pairing.key(),
            nft_a_mint: pairing.nft_a_mint,
            nft_b_mint: pairing.nft_b_mint,
        });

        Ok(())
    }
}

// ─── Accounts ───────────────────────────────────────────────────────────────
#[derive(Accounts)]
pub struct InitializeRegistry<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + Registry::INIT_SPACE,
        seeds = [REGISTRY_SEED],
        bump
    )]
    pub registry: Account<'info, Registry>,

    #[account(mut)]
    pub authority: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct CreatePairing<'info> {
    #[account(
        init,
        payer = authority,
        space = 8 + Pairing::INIT_SPACE,
        seeds = [PAIRING_SEED, nft_a_mint.key().as_ref(), nft_b_mint.key().as_ref()],
        bump
    )]
    pub pairing: Account<'info, Pairing>,

    pub registry: Account<'info, Registry>,

    pub nft_a_mint: Account<'info, Mint>,
    pub nft_b_mint: Account<'info, Mint>,

    #[account(mut)]
    pub authority: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct UpdatePairing<'info> {
    #[account(mut)]
    pub pairing: Account<'info, Pairing>,

    pub authority: Signer<'info>,
}

// ─── Data Structures ───────────────────────────────────────────────────────
#[account]
#[derive(InitSpace)]
pub struct Registry {
    pub authority: Pubkey,
    pub platform_fee_bps: u16,
    pub total_pairings: u64,
    pub paused: bool,
    pub bump: u8,
}

#[account]
#[derive(InitSpace)]
pub struct Pairing {
    pub authority: Pubkey,
    pub nft_a_mint: Pubkey,
    pub nft_b_mint: Pubkey,
    pub royalty_bps: u16,
    #[max_len(5)]
    pub creators: Vec<Creator>,
    #[max_len(200)]
    pub metadata_uri: String,
    pub pairing_type: PairingType,
    pub created_at: i64,
    pub active: bool,
    pub total_sales: u64,
    pub total_royalties_paid: u64,
    pub bump: u8,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, InitSpace)]
pub struct Creator {
    pub address: Pubkey,
    pub share_bps: u16,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, PartialEq, Eq, InitSpace)]
pub enum PairingType {
    ProductNFT,
    NFTBundle,
    RoyaltySplit,
    Exclusive,
}

#[derive(AnchorSerialize, AnchorDeserialize)]
pub struct CreatePairingParams {
    pub royalty_bps: u16,
    #[max_len(5)]
    pub creators: Vec<Creator>,
    #[max_len(200)]
    pub metadata_uri: String,
    pub pairing_type: PairingType,
}

// ─── Events ───────────────────────────────────────────────────────────────
#[event]
pub struct RegistryInitialized {
    pub authority: Pubkey,
    pub platform_fee_bps: u16,
}

#[event]
pub struct PairingCreated {
    pub pairing: Pubkey,
    pub nft_a_mint: Pubkey,
    pub nft_b_mint: Pubkey,
    pub royalty_bps: u16,
    pub authority: Pubkey,
}

#[event]
pub struct PairingDeactivated {
    pub pairing: Pubkey,
    pub nft_a_mint: Pubkey,
    pub nft_b_mint: Pubkey,
}

// ─── Errors ───────────────────────────────────────────────────────────────
#[error_code]
pub enum PairingError {
    #[msg("Fee too high")]
    FeeTooHigh,
    #[msg("Registry is paused")]
    RegistryPaused,
    #[msg("Already paired")]
    AlreadyPaired,
    #[msg("Pairing inactive")]
    PairingInactive,
    #[msg("Invalid amount")]
    InvalidAmount,
    #[msg("Math overflow")]
    Overflow,
}
