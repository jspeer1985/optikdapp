// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";

/// @title MerchantRegistry - Manages merchant onboarding and fee configuration
contract MerchantRegistry is AccessControl {
    bytes32 public constant MERCHANT_ADMIN_ROLE = keccak256("MERCHANT_ADMIN_ROLE");

    struct Merchant {
        bool active;
        uint16 primaryFeeBps;    // fee taken by platform on primary mints
        uint16 secondaryFeeBps;  // fee on secondary sales
        address payout;
        uint8 tier;              // optional tiering
    }

    event MerchantAdded(address indexed merchant, address payout, uint16 primaryFeeBps, uint16 secondaryFeeBps, uint8 tier);
    event MerchantUpdated(address indexed merchant, address payout, uint16 primaryFeeBps, uint16 secondaryFeeBps, uint8 tier, bool active);

    mapping(address => Merchant) public merchants;

    constructor(address admin) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(MERCHANT_ADMIN_ROLE, admin);
    }

    function addMerchant(
        address merchant,
        address payout,
        uint16 primaryFeeBps,
        uint16 secondaryFeeBps,
        uint8 tier
    ) external onlyRole(MERCHANT_ADMIN_ROLE) {
        require(merchant != address(0), "merchant=0");
        require(payout != address(0), "payout=0");
        require(primaryFeeBps <= 2_000 && secondaryFeeBps <= 2_000, "fee too high");
        Merchant storage m = merchants[merchant];
        require(!m.active, "exists");
        m.active = true;
        m.payout = payout;
        m.primaryFeeBps = primaryFeeBps;
        m.secondaryFeeBps = secondaryFeeBps;
        m.tier = tier;
        emit MerchantAdded(merchant, payout, primaryFeeBps, secondaryFeeBps, tier);
    }

    function setMerchant(
        address merchant,
        address payout,
        uint16 primaryFeeBps,
        uint16 secondaryFeeBps,
        uint8 tier,
        bool active
    ) external onlyRole(MERCHANT_ADMIN_ROLE) {
        require(merchant != address(0), "merchant=0");
        require(payout != address(0), "payout=0");
        require(primaryFeeBps <= 2_000 && secondaryFeeBps <= 2_000, "fee too high");
        Merchant storage m = merchants[merchant];
        m.active = active;
        m.payout = payout;
        m.primaryFeeBps = primaryFeeBps;
        m.secondaryFeeBps = secondaryFeeBps;
        m.tier = tier;
        emit MerchantUpdated(merchant, payout, primaryFeeBps, secondaryFeeBps, tier, active);
    }

    function getMerchant(address merchant) external view returns (Merchant memory) {
        return merchants[merchant];
    }
}
