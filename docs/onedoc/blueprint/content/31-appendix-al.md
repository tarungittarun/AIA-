
# Appendix AL — UX criteria → verification method map

| UX | Criterion (short) | Automated as |
|---|---|---|
| UX-01 | FAB → editor directly, doc on first keystroke | driver timing + tap-count |
| UX-02 | Blank→first char ≤ 2 taps, ≤ 2 s | driver timing + tap-count |
| UX-03 | Export PDF ≤ 3 taps | tap-count + state walk |
| UX-04 | Import ≤ 2 taps | tap-count + state walk |
| UX-05 | Find bar remembers term, clean dismiss | tap-count + state walk |
| UX-06 | AI/paste inserts undo as one group | timed procedure (budget) |
| UX-07 | Restore ≤ 30 s / 50 pages | timed procedure (budget) |
| UX-08 | Search results from ≤ 2 chars | timed procedure (budget) |
| UX-09 | Scan page → text ≤ 60 s Tier B | timed procedure (budget) |
| UX-10 | Dictation first partial ≤ 1.5 s | timed procedure (budget) |
| UX-11 | kill mid-typing: zero loss | kill-trial (STATE-005 evidence) |
| UX-12 | Rotation/split keeps cursor + composition | rotation/IME instrumentation |
| UX-13 | No save dialogs, autosave silent | silent-save assert |
| UX-14 | Trash undo 7 s; 30-day retention | snackbar timing probe |
| UX-15 | Failed import: no empty doc, clipboard intact | corruption drill variant |
| UX-16 | Replace-all: confirm + pre-edit version + undo | corruption drill variant |
| UX-17 | Storage-full: in-memory continue, auto retry | corruption drill variant |
| UX-18 | Export failure: no partial file, specific reason | corruption drill variant |
| UX-19 | Toolbar never covers selection | geometry unit test + dp audit |
| UX-20 | Targets ≥ 48 dp (44 toolbar) | geometry unit test + dp audit |
| UX-21 | System-standard long-press select; stylus/mouse | instrumented interaction |
| UX-22 | IME composition: no flicker/dup/loss | IME scripts + recording |
| UX-23 | Enter continues list; exits on empty | instrumented interaction |
| UX-24 | Style switch preserves marks | instrumented interaction |
| UX-25 | Scroll anchored during IME show/hide | instrumented interaction |
| UX-26 | No whole-doc reflow while typing | instrumented interaction |
| UX-27 | Scroll mid-composition cancels cleanly | rotation/IME instrumentation |
| UX-28 | Hardware shortcuts match platform; undo parity | instrumented interaction |
| UX-29 | AI only via preview + explicit insert | UI state + string assertions |
| UX-30 | Unavailable AI says why in one line | UI state + string assertions |
| UX-31 | No notifications beyond user-created/progress | notification listener probe |
| UX-32 | One-card first launch; permissions at use | fresh-install run |
| UX-33 | Delete warns version count; trash double-confirm | flow + confirm-count assert |
| UX-34 | Diagnostics on-device only, self-test ≤ 20 s | self-test timer probe |
| UX-35 | Destructive: haptic + undoable/double-confirm | flow + confirm-count assert |
| UX-36 | Empty states one line one action | state-walk (DQ-8) |
| UX-37 | TalkBack-complete letter flow | TalkBack full-flow instrumentation |
| UX-38 | Alt-text prompted at insert | insert-flow focus assert |
| UX-39 | 200% scale: no clipping | emulator walk @200% + screenshot diff |
| UX-40 | Dark + high-contrast themes pass contrast | WCAG compute from tokens (DQ-4) |
| UX-41 | Color never sole carrier | render + RTL/locale sweep |
| UX-42 | Primary actions bottom 40% | driver timing + tap-count |
| UX-43 | RTL mirroring correct | render + RTL/locale sweep |
| UX-44 | Reduced-motion honored | reduced-motion toggle test |
| UX-45 | Import states achieved fidelity | UI state + string assertions |
| UX-46 | OCR low-confidence marked/fixable; export honest | UI state + string assertions |
| UX-47 | AI results label method | UI state + string assertions |
| UX-48 | Pack install shows SHA; failure shows both | UI state + string assertions |
| UX-49 | Word count matches export ±1% | pdftotext count diff |
| UX-50 | No marketing/network content ever | network probe + string scan |
