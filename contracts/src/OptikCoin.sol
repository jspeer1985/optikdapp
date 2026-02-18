// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";
import {AccessControl} from "@openzeppelin/contracts/access/AccessControl.sol";
import {Pausable} from "@openzeppelin/contracts/utils/Pausable.sol";

/// @title OptikCoin - Platform pairing token for all NFTs on Optik
/// @notice Canonical ERC20 used to denominate primary and secondary NFT flows.
contract OptikCoin is ERC20, ERC20Permit, AccessControl, Pausable {
    bytes32 public constant MINTER_ROLE = keccak256("MINTER_ROLE");
    bytes32 public constant PAUSER_ROLE = keccak256("PAUSER_ROLE");

    event Mint(address indexed to, uint256 amount);
    event Burn(address indexed from, uint256 amount);

    constructor(
        string memory name_,
        string memory symbol_,
        address admin,
        address initialMinter,
        uint256 initialSupply
    ) ERC20(name_, symbol_) ERC20Permit(name_) {
        _grantRole(DEFAULT_ADMIN_ROLE, admin);
        _grantRole(MINTER_ROLE, initialMinter);
        _grantRole(PAUSER_ROLE, admin);
        if (initialSupply > 0) {
            _mint(admin, initialSupply);
            emit Mint(admin, initialSupply);
        }
    }

    function mint(address to, uint256 amount) external whenNotPaused onlyRole(MINTER_ROLE) {
        _mint(to, amount);
        emit Mint(to, amount);
    }

    function burn(uint256 amount) external whenNotPaused {
        _burn(msg.sender, amount);
        emit Burn(msg.sender, amount);
    }

    function pause() external onlyRole(PAUSER_ROLE) {
        _pause();
    }

    function unpause() external onlyRole(PAUSER_ROLE) {
        _unpause();
    }
}
