use anchor_lang::prelude::*;

declare_id!("Fg6PaFpoGXkYsidMpWTK6W2BeZ7FEfcYkgMQHGy8yY3x");

#[program]
pub mod secure_counter {
    use super::*;

    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        let counter = &mut ctx.accounts.counter;
        counter.authority = *ctx.accounts.authority.key;
        counter.value = 0;
        Ok(())
    }

    pub fn increment(ctx: Context<Increment>) -> Result<()> {
        let counter = &mut ctx.accounts.counter;

        require!(
            counter.authority == *ctx.accounts.authority.key,
            CustomError::Unauthorized
        );

        counter.value = counter.value.checked_add(1).ok_or(CustomError::Overflow)?;

        emit!(CounterIncremented {
            new_value: counter.value
        });

        Ok(())
    }
}

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(init, payer = authority, space = 8 + 40)]
    pub counter: Account<'info, Counter>,
    #[account(mut)]
    pub authority: Signer<'info>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct Increment<'info> {
    #[account(mut)]
    pub counter: Account<'info, Counter>,
    pub authority: Signer<'info>,
}

#[account]
pub struct Counter {
    pub authority: Pubkey,
    pub value: u64,
}

#[event]
pub struct CounterIncremented {
    pub new_value: u64,
}

#[error_code]
pub enum CustomError {
    #[msg("You are not authorized to perform this action")]
    Unauthorized,
    #[msg("Counter overflow")]
    Overflow,
}
