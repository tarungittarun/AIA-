
# Appendix U — Run manifest (case → gate → AVD → pipeline)

Every catalogue case appears exactly once here; the QA harness consumes this table as the run manifest (§24.7). `— (JVM)` rows run in pr/nightly JVM shards. Variants (TC-AI-004-b …, TC-J2-degraded …) are procedure variants of their base case (§24.5), not separate manifest rows.

| Case | First gate | AVDs | Pipeline | Procedure source |
|---|---|---|---|---|
| TC-A11Y-001 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-A11Y-002 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-A11Y-003 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-AI-001 | G6 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-AI-002 | G6 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-AI-003 | G6 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-AI-004 | G6 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-AI-005 | G6 | 36 + 26/33/35 | instrumented + apk-qa | Appendix C/I |
| TC-AI-006 | G6 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-AI-007 | G6 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-AI-008 | G6 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-AI-009 | G6 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-AI-010 | G6 | 36 + 26/33/35 | instrumented + apk-qa | Appendix C/I |
| TC-AI-PACK-01 | G6 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-AI-PACK-02 | G6 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-DIAG-001 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-EDIT-001 | G3 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-EDIT-002 | G3 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-EDIT-003 | G3 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-EDIT-004 | G3 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-EDIT-005 | G3 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-EDIT-006 | G3 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-EDIT-007 | G3 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-EDIT-008 | G3 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-EDIT-009 | G3 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-EDIT-010 | G3 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-EDIT-011 | G3 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-EDIT-012 | G3 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-EDIT-013 | G3 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-EDIT-014 | G3 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-EDIT-015 | G3 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-EDIT-016 | G3 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-EDIT-017 | G3 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-EDIT-IME-01 | G3 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-EDIT-IME-02 | G3 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-EDIT-IME-03 | G3 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-EDIT-IME-04 | G3 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-ENV-001 | G7 | 26 | apk-qa | Appendix C/I |
| TC-ENV-002 | G7 | 36 (+33 ladder) | apk-qa | Appendix C/I |
| TC-ENV-003 | G7 | 26/33/35/36 tablet | apk-qa | Appendix C/I |
| TC-ENV-004 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-IMG-001 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-IMG-002 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-IMG-003 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-IO-001 | G5 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-IO-002 | G5 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-IO-003 | G5 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-IO-004 | G5 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-IO-005 | G5 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-IO-006 | G5 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-IO-007 | G5 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-IO-008 | G5 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-IO-009 | G5 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-IO-010 | G5 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-IO-011 | G5 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-IO-012 | G5 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-IO-013 | G5 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-LAW-001 | G3 | — (JVM) | pr + nightly | Appendix C/I |
| TC-LAW-002 | G3 | — (JVM) | pr + nightly | Appendix C/I |
| TC-LAW-003 | G3 | — (JVM) | pr + nightly | Appendix C/I |
| TC-LAW-004 | G3 | — (JVM) | pr + nightly | Appendix C/I |
| TC-LIB-001 | G2 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-LIB-002 | G2 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-LIB-003 | G2 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-LIB-004 | G2 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-LIB-005 | G2 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-LIB-006 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-LIB-007 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-LIB-008 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-LIB-009 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-LIB-010 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-PERF-001 | G7 | 33 | apk-qa | Appendix C/I |
| TC-PERF-002 | G7 | 33 | apk-qa | Appendix C/I |
| TC-PROP-P01 | G3 | — (JVM) | pr + nightly | Appendix C/I |
| TC-PROP-P02 | G3 | — (JVM) | pr + nightly | Appendix C/I |
| TC-PROP-P03 | G3 | — (JVM) | pr + nightly | Appendix C/I |
| TC-PROP-P04 | G3 | — (JVM) | pr + nightly | Appendix C/I |
| TC-PROP-P05 | G3 | — (JVM) | pr + nightly | Appendix C/I |
| TC-PROP-P06 | G3 | — (JVM) | pr + nightly | Appendix C/I |
| TC-PROP-P07 | G3 | — (JVM) | pr + nightly | Appendix C/I |
| TC-PROP-P08 | G3 | — (JVM) | pr + nightly | Appendix C/I |
| TC-PROP-P09 | G3 | — (JVM) | pr + nightly | Appendix C/I |
| TC-PROP-P10 | G3 | — (JVM) | pr + nightly | Appendix C/I |
| TC-READ-001 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-SCAN-001 | G6 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-SCAN-002 | G6 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-SEC-IO-01 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-SEC-IO-02 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-SEC-P-01 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-SEC-P-02 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-SEC-P-03 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-SEC-P-04 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-SEC-PK-01 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-SEC-PK-02 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-SEC-ST-01 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-SEC-ST-02 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-SET-001 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-SET-002 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-SET-003 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-SET-004 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-SRCH-001 | G5 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-SRCH-002 | G5 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-SRCH-003 | G5 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-SRCH-004 | G5 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-SRCH-005 | G5 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-STATE-001 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-STATE-002 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-STATE-003 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-STATE-004 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-STATE-005 | G2 | 33 (100 trials) | instrumented + apk-qa | Appendix C/I |
| TC-STATE-006 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-STATE-007 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-STATE-008 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-STATE-009 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-STRUCT-001 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-STRUCT-002 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-STRUCT-003 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-STRUCT-004 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-STRUCT-005 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-STRUCT-006 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-STRUCT-007 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-STRUCT-008 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-STRUCT-009 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-TBL-001 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-TBL-002 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-TPL-001 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-TPL-002 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-TPL-003 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-TPL-004 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-TPL-005 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-TPL-006 | G4 | 33 (+26/35/36 P0 sweep) | instrumented + apk-qa | Appendix C/I |
| TC-UX-001 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-UX-002 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-UX-003 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-UX-004 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-UX-005 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-UX-006 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-UX-007 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-UX-008 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-UX-009 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-UX-010 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |
| TC-UX-011 | G7 | 33 (+26/35/36 P0 sweep) | apk-qa | Appendix C/I |

Count: 142 rows — must equal the catalogue case count (`traceability.py --check` cross-verifies).
