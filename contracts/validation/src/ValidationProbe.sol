// SPDX-License-Identifier: MIT
pragma solidity ^0.8.30;

interface IAavePoolView {
    function getUserAccountData(address user)
        external
        view
        returns (
            uint256 totalCollateralBase,
            uint256 totalDebtBase,
            uint256 availableBorrowsBase,
            uint256 currentLiquidationThreshold,
            uint256 ltv,
            uint256 healthFactor
        );
}

contract ValidationProbe {
    address public constant AAVE_V3_ETHEREUM_POOL = 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2;

    function accountData(address borrower) external view returns (uint256[6] memory values) {
        (
            values[0], values[1], values[2], values[3], values[4], values[5]
        ) = IAavePoolView(AAVE_V3_ETHEREUM_POOL).getUserAccountData(borrower);
    }
}

