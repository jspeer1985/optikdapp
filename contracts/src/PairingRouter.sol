// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import {SafeERC20} from "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";
import {ReentrancyGuard} from "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

interface IMerchantRegistry {
    function merchants(address) external view returns (
        bool active,
        uint16 primaryFeeBps,
        uint16 secondaryFeeBps,
        address payout,
        uint8 tier
    );
}

interface IPairedNFT {
    function mintPaired(address merchant, address to, uint256 priceOptik, string calldata tokenURI_) external returns (uint256 tokenId);
}

/// @title PairingRouter - Handles OptikCoin settlement for NFT mints and routes fees
contract PairingRouter is AccessControl, ReentrancyGuard {
    using SafeERC20 for IERC20;

    bytes32 public constant TREASURER_ROLE = keccak256("TREASURER_ROLE");

    IERC20 public immutable optik;
    IMerchantRegistry public immutable registry;
    address public feeRecipient; // platform fee recipient

    event FeeRecipientUpdated(address indexed account);
    event PrimaryMint(address indexed merchant, address indexed buyer, address indexed nft, uint256 tokenId, uint256 price, uint256 fee, uint256 merchantProceeds, string tokenURI);

    constructor(address admin, address optik_, address registry_, address feeRecipient_) {
        require(admin != address(0) && optik_ != address(0) && registry_ != address(0) && feeRecipient_ != address(0), "zero addr");
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(TREASURER_ROLE, admin);
        optik = IERC20(optik_);
        registry = IMerchantRegistry(registry_);
        feeRecipient = feeRecipient_;
    }

    function setFeeRecipient(address account) external onlyRole(TREASURER_ROLE) {
        require(account != address(0), "zero");
        feeRecipient = account;
        emit FeeRecipientUpdated(account);
    }

    /// @notice Buyer must approve this router to spend OptikCoin before calling
    function mintPrimary(
        address merchant,
        address nft,
        uint256 price,
        string calldata tokenURI_
    ) external nonReentrant returns (uint256 tokenId) {
        (bool active, uint16 primaryFeeBps,, address payout,) = registry.merchants(merchant);
        require(active, "merchant inactive");
        require(price > 0, "price=0");

        uint256 fee = (price * primaryFeeBps) / 10_000;
        uint256 proceeds = price - fee;

        // Pull OptikCoin from buyer
        optik.safeTransferFrom(msg.sender, address(this), price);

        // Route funds
        if (fee > 0) optik.safeTransfer(feeRecipient, fee);
        optik.safeTransfer(payout, proceeds);

        // Mint NFT via router authority
        tokenId = IPairedNFT(nft).mintPaired(merchant, msg.sender, price, tokenURI_);
        emit PrimaryMint(merchant, msg.sender, nft, tokenId, price, fee, proceeds, tokenURI_);
    }
}
