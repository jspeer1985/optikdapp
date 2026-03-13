use anchor_lang::prelude::*;
use anchor_spl::token::{Token, TokenAccount, Mint};
use anchor_spl::associated_token::AssociatedToken;

declare_id!("9dKgjdntLkaMpqFoeA4mVMa3gerh9DQbLt4hH2aebANX");

// ─── Constants ───────────────────────────────────────────────────────────────
pub const MAX_ROYALTY_BPS: u16 = 10_000; // 100%
pub const MAX_CREATORS: usize = 5;
pub const PAIRING_SEED: &[u8] = b"pairing";
pub const REGISTRY_SEED: &[u8] = b"registry";
pub const ESCROW_SEED: &[u8] = b"escrow";

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

        // Validate royalty splits sum to 10000 bps (100%)
        let total_bps: u16 = params
            .creators
            .iter()
            .map(|c| c.share_bps)
            .sum();
        require!(total_bps == MAX_ROYALTY_BPS, PairingError::InvalidRoyaltySplit);
        require!(
            params.creators.len() <= MAX_CREATORS,
            PairingError::TooManyCreators
        );
        require!(
            params.royalty_bps <= 3_000, // max 30% royalty
            PairingError::FeeTooHigh
        );

        // Verify caller owns or has authority over both NFTs
        require!(
            ctx.accounts.nft_a_token.owner == ctx.accounts.authority.key(),
            PairingError::NotNFTOwner
        );
        require!(
            ctx.accounts.nft_b_token.owner == ctx.accounts.authority.key(),
            PairingError::NotNFTOwner
        );

        // Verify NFTs have supply of 1 (true NFTs)
        require!(
            ctx.accounts.nft_a_mint.supply == 1,
            PairingError::NotNFT
        );
        require!(
            ctx.accounts.nft_b_mint.supply == 1,
            PairingError::NotNFT
        );

        // Verify NFTs are not already paired
        require!(
            !ctx.accounts.pairing.is_initialized(),
            PairingError::AlreadyPaired
        );

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
            nft_a_mint: pairing.nft_a_mint,
            nft_b_mint: pairing.nft_b_mint,
            royalty_bps: pairing.royalty_bps,
            authority: pairing.authority,
        });

        Ok(())
    }

    /// Distribute royalties for a sale of a paired NFT
    pub fn distribute_royalties(
        ctx: Context<DistributeRoyalties>,
        sale_amount_lamports: u64,
    ) -> Result<()> {
        require!(
            ctx.accounts.pairing.active,
            PairingError::PairingInactive
        );
        require!(sale_amount_lamports > 0, PairingError::InvalidAmount);

        let pairing = &ctx.accounts.pairing;
        let registry = &ctx.accounts.registry;

        // Calculate platform fee
        let platform_fee = sale_amount_lamports
            .checked_mul(registry.platform_fee_bps as u64)
            .ok_or(PairingError::Overflow)?
            .checked_div(MAX_ROYALTY_BPS as u64)
            .ok_or(PairingError::Overflow)?;

        // Calculate total royalty amount
        let royalty_pool = sale_amount_lamports
            .checked_mul(pairing.royalty_bps as u64)
            .ok_or(PairingError::Overflow)?
            .checked_div(MAX_ROYALTY_BPS as u64)
            .ok_or(PairingError::Overflow)?;

        // Pay platform fee
        if platform_fee > 0 {
            let cpi_context = CpiContext::new(
                ctx.accounts.system_program.to_account_info(),
                anchor_lang::system_program::Transfer {
                    from: ctx.accounts.payer.to_account_info(),
                    to: ctx.accounts.platform_treasury.to_account_info(),
                },
            );
            anchor_lang::system_program::transfer(cpi_context, platform_fee)?;
        }

        // Distribute royalties to each creator
        let mut total_distributed: u64 = 0;
        for (i, creator) in pairing.creators.iter().enumerate() {
            let creator_share = royalty_pool
                .checked_mul(creator.share_bps as u64)
                .ok_or(PairingError::Overflow)?
                .checked_div(MAX_ROYALTY_BPS as u64)
                .ok_or(PairingError::Overflow)?;

            if creator_share > 0 {
                let creator_account = ctx.remaining_accounts
                    .get(i)
                    .ok_or(PairingError::MissingCreatorAccount)?;

                require!(
                    creator_account.key() == creator.address,
                    PairingError::CreatorMismatch
                );

                let cpi_context = CpiContext::new(
                    ctx.accounts.system_program.to_account_info(),
                    anchor_lang::system_program::Transfer {
                        from: ctx.accounts.payer.to_account_info(),
                        to: creator_account.clone(),
                    },
                );
                anchor_lang::system_program::transfer(cpi_context, creator_share)?;
                total_distributed = total_distributed
                    .checked_add(creator_share)
                    .ok_or(PairingError::Overflow)?;
            }
        }

        // Update pairing stats
        let pairing = &mut ctx.accounts.pairing;
        pairing.total_sales = pairing.total_sales
            .checked_add(sale_amount_lamports)
            .ok_or(PairingError::Overflow)?;
        pairing.total_royalties_paid = pairing.total_royalties_paid
            .checked_add(total_distributed)
            .ok_or(PairingError::Overflow)?;

        emit!(RoyaltiesDistributed {
            pairing: ctx.accounts.pairing.key(),
            sale_amount: sale_amount_lamports,
            royalty_pool,
            platform_fee,
            total_distributed,
        });

        Ok(())
    }

    /// Update pairing metadata URI (authority only)
    pub fn update_pairing_metadata(
        ctx: Context<UpdatePairing>,
        new_metadata_uri: String,
    ) -> Result<()> {
        require!(
            new_metadata_uri.len() <= 200,
            PairingError::MetadataTooLong
        );
        let pairing = &mut ctx.accounts.pairing;
        pairing.metadata_uri = new_metadata_uri;

        emit!(PairingUpdated {
            pairing: ctx.accounts.pairing.key(),
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

    /// Emergency pause registry (authority only)
    pub fn set_registry_paused(
        ctx: Context<UpdateRegistry>,
        paused: bool,
    ) -> Result<()> {
        ctx.accounts.registry.paused = paused;
        Ok(())
    }

    /// Update platform fee (authority only)
    pub fn update_platform_fee(
        ctx: Context<UpdateRegistry>,
        new_fee_bps: u16,
    ) -> Result<()> {
        require!(new_fee_bps <= 1_000, PairingError::FeeTooHigh);
        ctx.accounts.registry.platform_fee_bps = new_fee_bps;
        Ok(())
    }
}

// ─── Account Contexts ─────────────────────────────────────────────────────────

#[derive(Accounts)]
pub struct InitializeRegistry<'info> {
    #[account(
        init,
        payer = authority,
        space = PairingRegistry::LEN,
        seeds = [REGISTRY_SEED, authority.key().as_ref()],
        bump
    )]
    pub registry: Account<'info, PairingRegistry>,

    #[account(mut)]
    pub authority: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct CreatePairing<'info> {
    #[account(
        init,
        payer = authority,
        space = PairingAccount::LEN,
        seeds = [
            PAIRING_SEED,
            nft_a_mint.key().as_ref(),
            nft_b_mint.key().as_ref()
        ],
        bump
    )]
    pub pairing: Account<'info, PairingAccount>,

    #[account(
        mut,
        seeds = [REGISTRY_SEED, authority.key().as_ref()],
        bump = registry.bump
    )]
    pub registry: Account<'info, PairingRegistry>,

    pub nft_a_mint: Account<'info, Mint>,
    pub nft_b_mint: Account<'info, Mint>,

    #[account(
        associated_token::mint = nft_a_mint,
        associated_token::authority = authority
    )]
    pub nft_a_token: Account<'info, TokenAccount>,

    #[account(
        associated_token::mint = nft_b_mint,
        associated_token::authority = authority
    )]
    pub nft_b_token: Account<'info, TokenAccount>,

    #[account(mut)]
    pub authority: Signer<'info>,

    pub token_program: Program<'info, Token>,
    pub associated_token_program: Program<'info, AssociatedToken>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct DistributeRoyalties<'info> {
    #[account(
        mut,
        seeds = [
            PAIRING_SEED,
            pairing.nft_a_mint.as_ref(),
            pairing.nft_b_mint.as_ref()
        ],
        bump = pairing.bump
    )]
    pub pairing: Account<'info, PairingAccount>,

    #[account(
        seeds = [REGISTRY_SEED, registry.authority.as_ref()],
        bump = registry.bump
    )]
    pub registry: Account<'info, PairingRegistry>,

    /// CHECK: Validated against registry.authority treasury
    #[account(
        mut,
        constraint = platform_treasury.key() == registry.authority @ PairingError::InvalidTreasury
    )]
    pub platform_treasury: AccountInfo<'info>,

    #[account(mut)]
    pub payer: Signer<'info>,

    pub system_program: Program<'info, System>,
    // remaining_accounts: creator wallet accounts in order matching pairing.creators
}

#[derive(Accounts)]
pub struct UpdatePairing<'info> {
    #[account(
        mut,
        seeds = [
            PAIRING_SEED,
            pairing.nft_a_mint.as_ref(),
            pairing.nft_b_mint.as_ref()
        ],
        bump = pairing.bump,
        has_one = authority @ PairingError::Unauthorized
    )]
    pub pairing: Account<'info, PairingAccount>,

    pub authority: Signer<'info>,
}

#[derive(Accounts)]
pub struct UpdateRegistry<'info> {
    #[account(
        mut,
        seeds = [REGISTRY_SEED, authority.key().as_ref()],
        bump = registry.bump,
        has_one = authority @ PairingError::Unauthorized
    )]
    pub registry: Account<'info, PairingRegistry>,

    pub authority: Signer<'info>,
}

// ─── Account Structs ──────────────────────────────────────────────────────────

#[account]
pub struct PairingRegistry {
    pub authority: Pubkey,        // 32
    pub platform_fee_bps: u16,    // 2
    pub total_pairings: u64,      // 8
    pub paused: bool,             // 1
    pub bump: u8,                 // 1
}

impl PairingRegistry {
    pub const LEN: usize = 8 + 32 + 2 + 8 + 1 + 1 + 64; // 64 padding
}

#[account]
pub struct PairingAccount {
    pub authority: Pubkey,              // 32
    pub nft_a_mint: Pubkey,             // 32
    pub nft_b_mint: Pubkey,             // 32
    pub royalty_bps: u16,               // 2
    pub creators: Vec<CreatorShare>,    // 4 + (MAX_CREATORS * 34)
    pub metadata_uri: String,           // 4 + 200
    pub pairing_type: PairingType,      // 1
    pub created_at: i64,                // 8
    pub active: bool,                   // 1
    pub total_sales: u64,               // 8
    pub total_royalties_paid: u64,      // 8
    pub bump: u8,                       // 1
}

impl PairingAccount {
    pub const LEN: usize = 8   // discriminator
        + 32   // authority
        + 32   // nft_a_mint
        + 32   // nft_b_mint
        + 2    // royalty_bps
        + 4 + (MAX_CREATORS * (32 + 2)) // creators vec
        + 4 + 200 // metadata_uri string
        + 1    // pairing_type
        + 8    // created_at
        + 1    // active
        + 8    // total_sales
        + 8    // total_royalties_paid
        + 1    // bump
        + 64;  // padding

    pub fn is_initialized(&self) -> bool {
        self.created_at > 0
    }
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug)]
pub struct CreatorShare {
    pub address: Pubkey,  // 32
    pub share_bps: u16,   // 2 — basis points of royalty pool
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Debug, PartialEq)]
pub enum PairingType {
    ProductNFT,     // Physical product paired with NFT
    NFTBundle,      // Two NFTs bundled together
    RoyaltySplit,   // Revenue sharing between NFT holders
    Exclusive,      // 1:1 exclusive pairing with transfer lock
}

// ─── Parameters ───────────────────────────────────────────────────────────────

#[derive(AnchorSerialize, AnchorDeserialize, Clone)]
pub struct CreatePairingParams {
    pub royalty_bps: u16,
    pub creators: Vec<CreatorShare>,
    pub metadata_uri: String,
    pub pairing_type: PairingType,
}

// ─── Events ───────────────────────────────────────────────────────────────────

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
pub struct PairingUpdated {
    pub pairing: Pubkey,
    pub authority: Pubkey,
}

#[event]
pub struct PairingDeactivated {
    pub pairing: Pubkey,
    pub nft_a_mint: Pubkey,
    pub nft_b_mint: Pubkey,
}

#[event]
pub struct RoyaltiesDistributed {
    pub pairing: Pubkey,
    pub sale_amount: u64,
    pub royalty_pool: u64,
    pub platform_fee: u64,
    pub total_distributed: u64,
}

// ─── Errors ───────────────────────────────────────────────────────────────────

#[error_code]
pub enum PairingError {
    #[msg("Royalty basis points split must sum to 10000")]
    InvalidRoyaltySplit,
    #[msg("Fee exceeds maximum allowed")]
    FeeTooHigh,
    #[msg("Caller is not the NFT owner")]
    NotNFTOwner,
    #[msg("Token supply must be 1 to qualify as NFT")]
    NotNFT,
    #[msg("These NFTs are already paired")]
    AlreadyPaired,
    #[msg("Pairing is inactive")]
    PairingInactive,
    #[msg("Registry is paused")]
    RegistryPaused,
    #[msg("Arithmetic overflow")]
    Overflow,
    #[msg("Too many creators — maximum is 5")]
    TooManyCreators,
    #[msg("Missing creator wallet account in remaining_accounts")]
    MissingCreatorAccount,
    #[msg("Creator account does not match pairing record")]
    CreatorMismatch,
    #[msg("Invalid platform treasury address")]
    InvalidTreasury,
    #[msg("Metadata URI exceeds 200 characters")]
    MetadataTooLong,
    #[msg("Unauthorized — must be pairing authority")]
    Unauthorized,
    #[msg("Sale amount must be greater than zero")]
    InvalidAmount,
}
