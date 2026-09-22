// SPDX-License-Identifier: MIT
pragma solidity ^0.8.30;

import {ValidationProbe} from "../src/ValidationProbe.sol";

interface Vm {
    function createSelectFork(string calldata rpcAlias, uint256 blockNumber) external returns (uint256);
    function envAddress(string calldata name) external returns (address);
    function envUint(string calldata name) external returns (uint256);
    function startPrank(address sender) external;
    function stopPrank() external;
}

interface IERC20 {
    function approve(address spender, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

interface IAavePool {
    function getUserAccountData(address user)
        external
        view
        returns (uint256, uint256, uint256, uint256, uint256, uint256);

    function liquidationCall(
        address collateralAsset,
        address debtAsset,
        address user,
        uint256 debtToCover,
        bool receiveAToken
    ) external;
}

interface IQuoterV2 {
    struct QuoteExactInputSingleParams {
        address tokenIn;
        address tokenOut;
        uint256 amountIn;
        uint24 fee;
        uint160 sqrtPriceLimitX96;
    }

    function quoteExactInputSingle(QuoteExactInputSingleParams calldata params)
        external
        returns (uint256 amountOut, uint160 sqrtPriceX96After, uint32 initializedTicksCrossed, uint256 gasEstimate);
}

interface ISwapRouter02 {
    struct ExactInputSingleParams {
        address tokenIn;
        address tokenOut;
        uint24 fee;
        address recipient;
        uint256 amountIn;
        uint256 amountOutMinimum;
        uint160 sqrtPriceLimitX96;
    }

    function exactInputSingle(ExactInputSingleParams calldata params) external payable returns (uint256 amountOut);
}

contract ForkValidationTest {
    Vm private constant vm = Vm(address(uint160(uint256(keccak256("hevm cheat code")))));
    IAavePool private constant AAVE_POOL = IAavePool(0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2);
    IQuoterV2 private constant QUOTER_V2 = IQuoterV2(0x61fFE014bA17989E743c5F6cB21bF9697530B21e);
    ISwapRouter02 private constant SWAP_ROUTER_02 =
        ISwapRouter02(0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45);
    address private constant WETH = 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2;
    address private constant USDC = 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48;

    function testPinnedAaveAccountRead() external {
        uint256 blockNumber = vm.envUint("SNAPSHOT_BLOCK");
        address borrower = vm.envAddress("BORROWER_ADDRESS");
        vm.createSelectFork("mainnet", blockNumber);
        require(block.chainid == 1, "not mainnet fork");
        ValidationProbe probe = new ValidationProbe();
        uint256[6] memory values = probe.accountData(borrower);
        require(values[5] > 0 || values[1] == 0, "invalid HF response");
    }

    function testLiquidationEligibilityAtPinnedBlock() external {
        _selectFork();
        address borrower = vm.envAddress("LIQUIDATABLE_BORROWER");
        (,,,,, uint256 healthFactor) = AAVE_POOL.getUserAccountData(borrower);
        require(healthFactor < 1e18, "sample is not liquidatable at snapshot block");
    }

    function testLiquidationCallRepayAndSeize() external {
        _selectFork();
        address borrower = vm.envAddress("LIQUIDATABLE_BORROWER");
        address fundedLiquidator = vm.envAddress("FUNDED_LIQUIDATOR");
        uint256 debtToCover = vm.envUint("DEBT_TO_COVER");
        uint256 debtBefore = IERC20(USDC).balanceOf(fundedLiquidator);
        uint256 collateralBefore = IERC20(WETH).balanceOf(fundedLiquidator);
        require(debtBefore >= debtToCover, "funded liquidator lacks USDC");

        vm.startPrank(fundedLiquidator);
        IERC20(USDC).approve(address(AAVE_POOL), debtToCover);
        AAVE_POOL.liquidationCall(WETH, USDC, borrower, debtToCover, false);
        vm.stopPrank();

        uint256 debtSpent = debtBefore - IERC20(USDC).balanceOf(fundedLiquidator);
        uint256 collateralReceived = IERC20(WETH).balanceOf(fundedLiquidator) - collateralBefore;
        require(debtSpent > 0 && debtSpent <= debtToCover, "invalid debt repaid");
        require(collateralReceived > 0, "no collateral seized");
    }

    function testUniswapQuoterV2Reference() external {
        _selectFork();
        uint256 amountIn = vm.envUint("WETH_QUOTE_AMOUNT");
        uint24 fee = uint24(vm.envUint("UNISWAP_FEE"));
        (uint256 amountOut,, uint32 ticksCrossed,) = QUOTER_V2.quoteExactInputSingle(
            IQuoterV2.QuoteExactInputSingleParams(WETH, USDC, amountIn, fee, 0)
        );
        require(amountOut > 0, "empty quote");
        require(ticksCrossed < type(uint32).max, "invalid tick count");
    }

    function testUniswapLocalForkSwap() external {
        _selectFork();
        address fundedWethHolder = vm.envAddress("FUNDED_WETH_HOLDER");
        uint256 amountIn = vm.envUint("WETH_SWAP_AMOUNT");
        uint24 fee = uint24(vm.envUint("UNISWAP_FEE"));
        require(IERC20(WETH).balanceOf(fundedWethHolder) >= amountIn, "funded holder lacks WETH");

        vm.startPrank(fundedWethHolder);
        IERC20(WETH).approve(address(SWAP_ROUTER_02), amountIn);
        uint256 amountOut = SWAP_ROUTER_02.exactInputSingle(
            ISwapRouter02.ExactInputSingleParams(WETH, USDC, fee, fundedWethHolder, amountIn, 0, 0)
        );
        vm.stopPrank();
        require(amountOut > 0, "fork swap produced no USDC");
    }

    function _selectFork() private {
        vm.createSelectFork("mainnet", vm.envUint("SNAPSHOT_BLOCK"));
        require(block.chainid == 1, "not mainnet fork");
    }
}
