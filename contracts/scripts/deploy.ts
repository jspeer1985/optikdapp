import { ethers } from "hardhat";

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deployer:", deployer.address);

  const name = process.env.OPTIK_NAME || "OptikCoin";
  const symbol = process.env.OPTIK_SYMBOL || "OPTK";
  const initialSupply = process.env.OPTIK_SUPPLY ? ethers.parseUnits(process.env.OPTIK_SUPPLY, 18) : 0n;
  const platformTreasury = process.env.PLATFORM_TREASURY || deployer.address;

  const OptikCoin = await ethers.getContractFactory("OptikCoin");
  const optik = await OptikCoin.deploy(name, symbol, deployer.address, deployer.address, initialSupply);
  await optik.waitForDeployment();
  console.log("OptikCoin:", await optik.getAddress());

  const MerchantRegistry = await ethers.getContractFactory("MerchantRegistry");
  const registry = await MerchantRegistry.deploy(deployer.address);
  await registry.waitForDeployment();
  console.log("MerchantRegistry:", await registry.getAddress());

  const PairedNFT = await ethers.getContractFactory("PairedNFT");
  const pairedNFT = await PairedNFT.deploy("Optik NFT", "OP-NFT", deployer.address, await optik.getAddress(), await registry.getAddress());
  await pairedNFT.waitForDeployment();
  console.log("PairedNFT:", await pairedNFT.getAddress());

  const PairingRouter = await ethers.getContractFactory("PairingRouter");
  const router = await PairingRouter.deploy(deployer.address, await optik.getAddress(), await registry.getAddress(), platformTreasury);
  await router.waitForDeployment();
  console.log("PairingRouter:", await router.getAddress());

  // wire router to NFT
  const tx = await pairedNFT.setRouter(await router.getAddress());
  await tx.wait();
  console.log("Router set on PairedNFT");

  // example merchant add (optional):
  // const addTx = await registry.addMerchant(deployer.address, deployer.address, 500, 250, 1);
  // await addTx.wait();
  // console.log("Added sample merchant", deployer.address);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
