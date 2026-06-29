# Decision Frameworks (Phase 1.5 reference)

**Choose boring, proven technology and spend your innovation budget narrowly.** Justify each choice against an NFR.

## SQL vs NoSQL vs other stores
Modern practice is **polyglot persistence** — the right store per workload — but most apps start with one relational database and add others only when a specific need appears.

| Need | Reach for |
|---|---|
| Relationships, multi-entity transactions, complex/aggregate queries, strong integrity (finance, orders, most apps) | **Relational / SQL** — PostgreSQL is the sane default. ACID, joins, mature. |
| Flexible/evolving schema, document-shaped data, scale writes horizontally | **Document NoSQL** — MongoDB, DynamoDB |
| Simple key->value lookups, caching, sessions, low latency | **Key-value** — Redis, DynamoDB |
| Highly connected data, traversals (social, recommendations, fraud) | **Graph** — Neo4j, Neptune |
| Append-heavy metrics/events over time | **Time-series** — TimescaleDB, InfluxDB |
| Full-text / fuzzy search, ranking | **Search** — Elasticsearch, OpenSearch |
| Large files, images, video | **Blob/object store** — S3 et al. (never the DB) |
| Global scale + SQL semantics | **NewSQL / distributed SQL** — CockroachDB, Spanner |

Three questions settle most cases: *(1) Transactions across multiple entities? -> SQL. (2) Schema changes constantly? -> NoSQL leans easier. (3) Scale writes globally? -> NoSQL/NewSQL are built for it; SQL needs sharding, which is hard.*

Remember CAP: SQL tends to **CP** (consistent, may be unavailable during a partition); many NoSQL stores tend to **AP** (available, may serve stale data). Pick on purpose; don't expect SQL consistency from an AP store.

## Data access: raw vs ORM
**ORM** for fast CRUD and velocity; drop to **raw / query-builder** for hot paths and complex queries where you need to see the SQL. Hybrid is normal. Watch the **N+1 problem** (see [`31_data_layer.md`](31_data_layer.md)).

## Architecture style

| Start here | Move when |
|---|---|
| **Single module / script** | it's a throwaway or a library |
| **Modular monolith** (default for real products) | one deployable, clean internal boundaries — most "microservice" benefits with none of the distributed-systems tax |
| **Services / microservices** | independent scaling/deploy of parts, large autonomous teams, hard isolation — accept the operational cost (network failure, distributed tracing, cross-service consistency) |
| **Serverless / functions** | spiky/low traffic, event-driven glue, zero ops — accept cold starts and vendor lock-in |

**Don't start with microservices.** Extract them from a modular monolith once you have evidence you need to.

## Sync vs async
**Sync request/response** when the caller needs the answer now and work is fast. **Async (queue/event/stream)** when work is slow, spiky, retriable, or fans out — buys buffering, backpressure, resilience, at the cost of eventual consistency and harder debugging.

## API style

| Style | Best for |
|---|---|
| **REST** | the default — public APIs, CRUD, broad tooling, cacheable |
| **GraphQL** | clients need flexible/aggregated reads, many shapes, avoid over/under-fetch |
| **gRPC** | internal service-to-service, low latency, streaming, strict contracts |
| **none** | it's a library — ship a clean function API, not a network layer |

## Build vs buy vs adopt
For undifferentiated heavy lifting — **auth, payments, email, search, identity** — **buy or adopt** a proven provider/library rather than building. Build only your actual differentiator. Axes: is it core to your value? total cost (build + maintain forever) vs license? security/compliance burden you'd own? (Auth and payments especially: rolling your own almost never justifies the risk.)

## Hosting
**Managed PaaS** (Render, Fly, App Runner) to start — least ops. **Containers + orchestration** (k8s) when you need portability and fine control, accepting complexity. **Serverless** for event-driven/spiky. **VMs** only for full control or specific constraints.
