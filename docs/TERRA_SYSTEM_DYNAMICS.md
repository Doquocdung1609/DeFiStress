# Terra System Dynamics Model

The aggregate benchmark has no heterogeneous agents. At each hour:

1. depeg and backing stress increase withdrawal intensity;
2. withdrawals create UST sell/redemption flow;
3. redemption reduces UST and mints LUNA;
4. sell pressure depletes liquidity and moves UST;
5. dilution and depeg move LUNA;
6. the new LUNA market capitalization updates backing ratio.

Primary parameters are initial withdrawal shock, confidence sensitivity, arbitrage capacity, redemption friction, and price-impact coefficient. They are frozen at cutoff or pre-specified; evaluation-period values are never fitted.
