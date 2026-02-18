import { expect } from "chai";
import { ethers } from "hardhat";

describe("Optik Pairing", function () {
  it("deploys and mints primary with OptikCoin", async function () {
    const [admin, buyer] = await ethers.getSigners();

    const OptikCoin = await ethers.getContractFactory("OptikCoin");
    const optik = await OptikCoin.deploy("OptikCoin", "OPTK", admin.address, admin.address, ethers.parseUnits("1000000", 18));
    await optik.waitForDeployment();

    const MerchantRegistry = await ethers.getContractFactory("MerchantRegistry");
    const registry = await MerchantRegistry.deploy(admin.address);
    await registry.waitForDeployment();

    const PairedNFT = await ethers.getContractFactory("PairedNFT");
    const pairedNFT = await PairedNFT.deploy("Optik NFT", "OP-NFT", admin.address, await optik.getAddress(), await registry.getAddress());
    await pairedNFT.waitForDeployment();

    const PairingRouter = await ethers.getContractFactory("PairingRouter");
    const router = await PairingRouter.deploy(admin.address, await optik.getAddress(), await registry.getAddress(), admin.address);
    await router.waitForDeployment();

    await (await pairedNFT.setRouter(await router.getAddress())).wait();

    // fund buyer and approve
    await (await optik.transfer(buyer.address, ethers.parseUnits("1000", 18))).wait();

    await (await registry.addMerchant(admin.address, admin.address, 500, 250, 1)).wait();

    const buyerOptik = optik.connect(buyer);
    await (await buyerOptik.approve(await router.getAddress(), ethers.parseUnits("1000", 18))).wait();

    const price = ethers.parseUnits("100", 18);

    await expect(router.connect(buyer).mintPrimary(admin.address, await pairedNFT.getAddress(), price, "ipfs://token/1"))
      .to.emit(pairedNFT, "MintPaired");
  });
});
