# Polymarket API investigation

Inspected 2026-09-21. Documentation is current guidance, not proof of eligibility or liquidity for any specific pair of MLB props. No authenticated calls or orders were made.

| Question | Finding |
| --- | --- |
| Sports discovery | Gamma `GET /sports`, `/sports/market-types`, and paginated `/events` or `/markets/keyset`; discover league tags instead of fixing IDs in code. Companion events can contain player props; use the game ID to discover them. |
| Prices and books | CLOB `GET /book?token_id=...` exposes levels. Gamma outcome prices are indicative metadata. Match outcome labels to token IDs rather than assuming YES is first. |
| Combo markets | Public RFQ `GET https://combos-rfq-api.polymarket.com/v1/rfq/combo-markets` is a cursor-paginated catalog of eligible component markets. It is not a feed of every possible combo and its executable price. |
| Components | RFQ request/response structures identify components with `leg_position_ids`. Underlying outcome IDs and catalog metadata can support joins. Do not confuse RFQ position IDs with CLOB token IDs. |
| Programmatic combo quotes | Documented, but creating an RFQ requires authenticated requester calls. This is not a public read-only price query. Not implemented here. |
| Same-player multi-leg support | Documentation requires compatible legs. I found no blanket guarantee that same-player or logically redundant MLB props are accepted; catalog presence alone cannot establish this. Specific combinations and available quotes remain unverified. |

Sources: [market discovery](https://docs.polymarket.com/market-data/discover-markets), [order books](https://docs.polymarket.com/market-data/prices-order-books), [combo overview](https://docs.polymarket.com/trading/combos/overview), [requester workflow](https://docs.polymarket.com/trading/combos/requesters).

The requester workflow uses `https://combos-rfq-gateway-requester-api.polymarket.com` and the `/v1/requester/rfq` base path. It separates creating a quote request from accepting a trade. Exact expiry is response-specific; use the returned timestamp rather than a hard-coded duration. This project does neither operation.

The minimal adapters retain raw catalog and book responses. Player identity, thresholds, game alignment, void rules and quote normalization are deliberately not inferred from free text. Returned pagination is explicit. Use a **new timestamped cache directory per market snapshot**: the immutable cache is intended for reproducibility and will otherwise return an old book. Do not call cached books live or executable. Production snapshot freshness enforcement is future work.

For an eventual comparison, `q_combo/q_anchor` is only an effective conditional-price diagnostic. It is not necessarily a coherent probability under fees, bid/ask spreads or different trade sizes. Calculate all-in executable cost per payout share, preserve quote time/expiry, and align settlement. An exact statistical implication does not imply market contract equivalence or executable arbitrage.
