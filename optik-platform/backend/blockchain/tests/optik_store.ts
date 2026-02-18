import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { OptikStore } from "../target/types/optik_store";
import { expect } from "chai";

describe("optik-store", () => {
    const provider = anchor.AnchorProvider.env();
    anchor.setProvider(provider);

    const program = anchor.workspace.OptikStore as Program<OptikStore>;

    it("Is initialized!", async () => {
        const merchantAccount = anchor.web3.Keypair.generate();
        await program.methods
            .initializeMerchant(500) // 5% fee
            .accounts({
                merchantAccount: merchantAccount.publicKey,
                owner: provider.wallet.publicKey,
                systemProgram: anchor.web3.SystemProgram.programId,
            })
            .signers([merchantAccount])
            .rpc();

        const account = await program.account.merchantAccount.fetch(merchantAccount.publicKey);
        expect(account.feeBps).to.equal(500);
        expect(account.owner.toString()).to.equal(provider.wallet.publicKey.toString());
    });
});
