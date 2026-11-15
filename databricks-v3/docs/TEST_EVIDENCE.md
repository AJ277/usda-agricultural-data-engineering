# Test evidence — observed Databricks lab results

This file records results reported by the operator during hands-on notebook exercises; it is **not** an independently executed CI test suite or GitHub Actions build. All 2026 yields below are fictional training values.

| Scenario | Input and expected behavior | Observed result |
| --- | --- | --- |
| Montana V3 completed-batch replay | 6 incoming = 2 accepted + 2 quarantine + 2 duplicate occurrences | `SKIPPED_COMPLETED`; full reconciliation passed |
| Montana four-table verification | Target 257; 2 Montana quarantine; 1 audit; 1 accounting; zero duplicate keys | Passed |
| Dakotas new batch | 5 incoming = 2 accepted + 2 quarantine + 1 duplicate | Target 257 → 259; 1 South Dakota and 1 North Dakota record; zero duplicate keys |
| Dakota completed-batch retry | Existing completed batch should be skipped | Counts unchanged: target 259, quarantine 2, audit 1, accounting 1 |
| Source mutation attempt | Same Dakota batch ID, changed South Dakota yield 170 → 180 | `BATCH SOURCE MISMATCH` raised; stored 170 preserved, 180 absent |
| Artificial partial-batch decision | No audit, quarantine exists | `INVESTIGATE_PARTIAL` |
| Real interrupted Vermont attempt | 3 incoming = 1 accepted + 2 quarantine; persist quarantine, omit MERGE/audit | Audit 0, quarantine 2, matching accepted 0; `INVESTIGATE_PARTIAL` |
| V3 interruption guard | Resume attempted with partial state | Raised `Potentially interrupted batch. Investigation required.`; target remained 259 |
| Vermont quarantine verification | Compare actual and expected quarantine multisets | 0 missing, 0 unexpected; passed |
| Vermont recovery preflight | Source, accounting, quarantine, absent key, missing audit | `SAFE_TO_RESUME_AFTER_QUARANTINE` |
| Vermont controlled completion | MERGE one accepted record and insert one audit | Target 260, Vermont 1, quarantine 2, audit 1, duplicate keys 0 |
| Vermont V3 replay | Previously recovered batch should be verified and skipped | `COMPLETED BATCH FULL RECONCILIATION PASSED`; `SKIPPED_COMPLETED` |
| Reusable notebook `%run` | Restore 14 V3 functions | 14 ready, 0 missing; loaded successfully |
| SQL views | Pipeline health, batch status, monitoring coverage | All three view checks passed |
| Published dashboard | Dashboard with 5 KPIs and batch table | Published dashboard screenshot showed expected counts |

## Final health view snapshot

```text
target_records: 260
duplicate_target_keys: 0
completed_audit_records: 10
quarantine_records: 20
duplicate_accounting_records: 3
registered_fingerprints: 5
```

## Completed-batch monitoring coverage

```text
completed_batches: 10
with_fingerprints: 4
with_accounting: 3
with_both_controls: 3
full_coverage_pct: 30.00
```

**Caution:** Static counts are point-in-time results from a sequential training lab. A screenshot of one check does not establish concurrency safety, cross-table atomicity, full historical provenance or ongoing availability.
