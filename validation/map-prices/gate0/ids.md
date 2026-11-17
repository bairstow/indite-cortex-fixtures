# Gate 0: trade ids for the map price collector

Read from `data/20261117-103111-data/filters.json` and `stats.json`. Those are GGG's `data/filters` and `data/stats`, fetched 2026-11-17 by `bb poe:trade-sample --data`. Mod text was checked against `validation/map-select/responses/to-roll-covens-originator.json`: 32 Covens T16 Originator maps from the stash API.

## Found

### Population

| What | Where | Id / value |
|---|---|---|
| Instant buyout | `query.status.option` | `securable` ("Instant Buyout"). `available` is "Instant Buyout and In Person" |
| Maps | `type_filters.category` | `map` |
| Rare | `type_filters.rarity` | `rare` |
| Tier 16 | `map_filters.map_tier` | `{"min": 16, "max": 16}` |
| Identified | `misc_filters.identified` | `"true"` |
| Not corrupted | `misc_filters.corrupted` | `"false"` |
| Originator | stat (implicit) | `implicit.stat_2696470877` "Area is Influenced by the Originator's Memories" (on all 32 sample maps, as an implicit) |
| Sale type | `trade_filters.sale_type` | left unset: the default is "Buyout or Fixed Price" |

### Properties

| Property (stash API name) | Trade filter | Id |
|---|---|---|
| Atlas Drops (`[AtlasDropScaling\|Atlas Drops]`) | map filter | `map_filters.map_bonus` ("Atlas Drops") |
| Item Rarity | map filter | `map_filters.map_iir` ("Increased Item Rarity") |
| Monster Pack Size | map filter | `map_filters.map_packsize` ("Increased Packsize") |
| More Currency | pseudo stat | `pseudo.pseudo_map_more_currency_drops` ("More Currency: #%") |
| More Maps | pseudo stat | `pseudo.pseudo_map_more_map_drops` ("More Maps: #%") |
| More Threads (`More [Thread\|Threads]`) | pseudo stat, **unconfirmed** | `pseudo.pseudo_map_more_scarab_drops`. Its text is still "More Scarabs: #%". There is no Threads pseudo. GGG kept the scarab ids when it renamed the text elsewhere (`delirium_reward_scarabs` now reads "Delirium Reward Type: Threads"), so this is very likely the Threads property. Stage B confirms it before relying on it (see Open) |

`map_filters.map_iiq` ("Increased Item Quantity") still exists. 3.30 maps have no Item Quantity property, so it isn't used.

### Suffixes

All five are explicit mods on the sample maps:

| Suffix | Id | Text |
|---|---|---|
| Mirage | `explicit.stat_2436559047` | "Area contains a Mirage" (an `enchant.` twin exists; the maps carry it as explicit, `Area contains a [Mirage]`) |
| Mirror of Delirium | `explicit.stat_2398157267` | "Area contains a Mirror of Delirium" |
| Evocator of K'Tash | `explicit.stat_2896557935` | "Area contains an Evocator of K'Tash" |
| buried Stalker Sentinel | `explicit.stat_2712450522` | "Area contains a buried Stalker Sentinel" |
| buried Apex Sentinel | `explicit.stat_2788592463` | "Area contains a buried Apex Sentinel" |

## Not found

None. Every id the plan asks for has a candidate. More Threads is the one we infer rather than read directly.

## Observed

- Neither `data/` response had a rate-limit header. Both metas have `:headers {}` after the whitelist. The `:data` kind is paced by its 20 s floor alone.

## Bodies

- `bodies/floor.json`: the population above, sorted by price ascending.
- `bodies/capped.json`: the floor, plus `pseudo.pseudo_map_more_currency_drops` with `{"max": 0}`. No map has More Currency at 0, so the total answers whether a max-only filter keeps maps that lack the property.

## Step 4: answers from `search/20261117-104807-search`

- **Max-only drops maps without the property.** The capped search (floor + More Currency `{"max": 0}`) returned **total 0**, while the floor returned **8081**. A max-only stat filter keeps only maps that carry the stat, so **the alts stay uncapped** in Stage B, as the design describes.
- **Auth: anonymous.** Both searches and the fetch went out without the cookie, and none was refused. Instant-buyout (`securable`) search needs no login.
- **Rate limits** (rule `Ip` only; no account rule when anonymous):
  - search (`trade-search-request-limit`): `5:10:60,15:60:300,30:300:1800,600:21600:3600`;
  - fetch (`trade-fetch-request-limit`): `12:4:10,16:12:300,50:300:300,1000:21600:1800`.

  At headroom 0.25 the shares are, per window:
  - search: 1 / 3 / 7 / 150;
  - fetch: 3 / 4 / 12 / 250.

  The 300 s search window allows 7. With `next-at`'s whole-period wait, that comes to about 7 searches per ~8 min. The design's 51 searches would take about an hour, not 20–40 min.
- **Fetch shape.** Each result is `{:id :listing :item}`:
  - `listing` has `method` (`psapi`), `indexed` (ISO time), `stash`, `price` (`{"type": "~b/o", "amount": 4, "currency": "chaos"}`), `fee`, `account` and `whisper`;
  - `item` has the stash API item keys plus `note` and `extended` (stat hashes per domain, base64 item text).

  - `floor-fetch.json` is **redacted**, at the owner's choice. Each listing's `account.name`, `account.lastCharacterName`, `stash.name` and the character and tab names inside `whisper` are replaced by stand-ins: `seller-N`, `seller-N-character` and `seller-N-tab-M`, numbered per file in listing order. The same seller keeps the same N; an empty tab name stays empty. There are 8 sellers across the 10 listings, and seller-1 has three. One listing (seller-8) has no `whisper`, and its account has only `name` and `online`. Everything else is GGG's body, re-serialised compact.

  Properties use the stash API names, so `api_record.cljc`'s reading applies. The floor's 10 cheapest were all 4c.
- **More Threads, partly confirmed.** Fetched items carry `More [Thread|Threads]` as a property. That `pseudo_map_more_scarab_drops` filters on it is still unconfirmed (Stage B's first run).

## Open (Stage B)

- More Threads: confirm `pseudo_map_more_scarab_drops` matches the Threads property. A min search on it should return maps whose fetched items carry `More [Thread|Threads]`.
