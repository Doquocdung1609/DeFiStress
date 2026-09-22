# Terra Import Schema

`terra_hourly_state.csv` is a schema template with synthetic example rows. It is not historical evidence.

Required columns are the core prices, supplies, Anchor flows, mint/burn, DEX volume/liquidity/depth, concentration, timestamp, and block height. Optional provenance and secondary Curve/bridge/reserve columns are documented in `TERRA_DATA_DICTIONARY.md`.

Timestamps must include an explicit UTC offset. Rows must be unique and monotonic after sorting. Supplies, flows, and liquidity cannot be negative. `source_name`, `source_type`, `chain_id`, `raw_reference`, and `quality_flag` should be supplied per row or through importer arguments.
