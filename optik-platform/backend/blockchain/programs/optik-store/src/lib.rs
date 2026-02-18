use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount, Transfer};

declare_id!("5kat1PUqnGRwMLZhsZ7ryDXcRtwaGPiFe8hEknLQ32dC");

#[program]
pub mod optik_store {
    use super::*;

    pub fn initialize_platform(ctx: Context<InitializePlatform>, treasury: Pubkey) -> Result<()> {
        let admin_state = &mut ctx.accounts.admin_state;
        admin_state.treasury = treasury;
        admin_state.admin = ctx.accounts.admin.key();
        Ok(())
    }

    pub fn initialize_merchant(ctx: Context<InitializeMerchant>, fee_bps: u16) -> Result<()> {
        let merchant_account = &mut ctx.accounts.merchant_account;
        merchant_account.owner = ctx.accounts.owner.key();
        merchant_account.fee_bps = fee_bps;
        merchant_account.total_revenue = 0;
        Ok(())
    }

    pub fn process_payment(ctx: Context<ProcessPayment>, amount: u64) -> Result<()> {
        let merchant_account = &mut ctx.accounts.merchant_account;
        let admin_state = &ctx.accounts.admin_state;

        // Security Check: Ensure treasury_token_account is the platform's verified account
        require_keys_eq!(
            ctx.accounts.treasury_token_account.owner,
            admin_state.treasury,
            ErrorCode::InvalidTreasury
        );

        // Calculate platform fee
        let fee = (amount as u128 * merchant_account.fee_bps as u128 / 10000) as u64;
        let merchant_amount = amount - fee;

        // Perform transfer to merchant
        let cpi_accounts = Transfer {
            from: ctx.accounts.buyer_token_account.to_account_info(),
            to: ctx.accounts.merchant_token_account.to_account_info(),
            authority: ctx.accounts.buyer.to_account_info(),
        };
        let cpi_program = ctx.accounts.token_program.to_account_info();
        let cpi_ctx = CpiContext::new(cpi_program, cpi_accounts);
        token::transfer(cpi_ctx, merchant_amount)?;

        // Perform transfer to platform treasury
        let cpi_accounts_fee = Transfer {
            from: ctx.accounts.buyer_token_account.to_account_info(),
            to: ctx.accounts.treasury_token_account.to_account_info(),
            authority: ctx.accounts.buyer.to_account_info(),
        };
        let cpi_ctx_fee = CpiContext::new(
            ctx.accounts.token_program.to_account_info(),
            cpi_accounts_fee,
        );
        token::transfer(cpi_ctx_fee, fee)?;

        merchant_account.total_revenue += merchant_amount;

        Ok(())
    }
}

#[derive(Accounts)]
pub struct InitializePlatform<'info> {
    #[account(init, payer = admin, space = 8 + 32 + 32)]
    pub admin_state: Account<'info, AdminState>,
    #[account(mut)]
    pub admin: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct InitializeMerchant<'info> {
    #[account(init, payer = owner, space = 8 + 32 + 2 + 8)]
    pub merchant_account: Account<'info, MerchantAccount>,
    #[account(mut)]
    pub owner: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct ProcessPayment<'info> {
    #[account(mut)]
    pub merchant_account: Account<'info, MerchantAccount>,
    pub admin_state: Account<'info, AdminState>,
    #[account(mut)]
    pub buyer: Signer<'info>,
    #[account(mut)]
    pub buyer_token_account: Account<'info, TokenAccount>,
    #[account(mut)]
    pub merchant_token_account: Account<'info, TokenAccount>,
    #[account(mut)]
    pub treasury_token_account: Account<'info, TokenAccount>,
    pub token_program: Program<'info, Token>,
}

#[account]
pub struct AdminState {
    pub admin: Pubkey,
    pub treasury: Pubkey,
}

#[account]
pub struct MerchantAccount {
    pub owner: Pubkey,
    pub fee_bps: u16,
    pub total_revenue: u64,
}

#[error_code]
pub enum ErrorCode {
    #[msg("The provided treasury account does not match the platform configuration.")]
    InvalidTreasury,
}
