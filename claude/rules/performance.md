# Performance

## Frontend

- **Lazy load** routes and heavy components. Don't bundle everything into the initial payload.
- Be conscious of bundle size. Before adding a dependency, check its gzipped size. Prefer tree-shakeable libraries.
- Avoid unnecessary re-renders. Memoize expensive computations (`useMemo`), stabilize callback references (`useCallback`) when passed as props, and avoid creating new objects/arrays in render.
- **Don't optimize prematurely.** Profile first, optimize second. React DevTools Profiler and browser Performance tab are your tools — not guesswork.
- Images: use appropriate formats (WebP/AVIF), lazy load below-fold images, serve responsive sizes.

## Backend

- **No blocking I/O in async handlers.** Synchronous file reads, CPU-heavy computation, or synchronous HTTP calls in an async endpoint will block the event loop and kill throughput.
- Watch for N+1 queries. If you're hitting the database inside a loop, batch the query.
- Use database connection pooling. Don't open a new connection per request.
- Cache expensive, stable computations. But cache deliberately — stale cache is worse than no cache.
- Set appropriate timeouts on external service calls. Don't let a slow third-party hang your entire request.

## API

- Paginate list endpoints. Never return unbounded result sets.
- Use cursor-based pagination for large/real-time datasets. Offset pagination is fine for small, stable sets.
- Compress responses (gzip/brotli). Most frameworks handle this automatically — verify it's enabled.
- Return only the fields the client needs. Avoid sending the entire database row when the UI only uses three fields (but don't over-optimize with per-field selection unless it's a real bottleneck).

## Database

- Index columns used in WHERE, JOIN, ORDER BY. Review slow query logs regularly.
- Use `EXPLAIN ANALYZE` before assuming an index will help.
- Avoid `SELECT *` in production code. Select the columns you need.
- Batch inserts/updates when processing multiple records. Don't insert one row at a time in a loop.

## General

- **Measure, don't guess.** Performance intuitions are frequently wrong. Use profilers, flame graphs, and metrics.
- Set performance budgets for critical paths (page load, API response time, query time) and monitor them.
- Performance is a feature, not an afterthought. Consider it during design, not just when things are slow.
