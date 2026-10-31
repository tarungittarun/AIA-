@PART: PART VIII — ON-DEVICE AI
@PARTDESC: Scan-to-doc, dictation, the writing assistant, semantic search and read-aloud — every capability running locally, every model a side-loaded SHA-verified pack, every unavailable state explained, nothing ever downloaded.

# Chapter 19 — On-device AI

## 19.1 The five capabilities and their stacks

![The AI stack: five capability modules over the pack manager and device tiers; the assistant row is the single surface where AI meets the user.](figures/fig-ai-stack.png)

| Capability | Engine | Pack | Latency budget (Tier B) |
|---|---|---|---|
| Scan-to-doc OCR | DBNet-lite detection + CRNN recognition, int8, NNAPI/GPU delegate | `ocr-en` ~18 MB (en; hi pack separate) | ≤ 12 s/page incl. capture |
| Dictation | whisper.cpp int8 streaming (Tier A/B) or system `SpeechRecognizer` (Tier C ladder) | `asr-en` ~42 MB | first partial ≤ 1.5 s (UX-10) |
| Writing assistant | gemma-2B 4-bit (q4_0, llama.cpp-compatible runtime), Tier A only | `llm-gemma2b` ~1.4 GB | first token ≤ 2.5 s, then ≥ 8 tok/s |
| Semantic search | MiniLM-L6 int8 quantized embeddings | `embed-minilm` ~23 MB | embed block ≤ 25 ms; query ≤ 40 ms |
| Read aloud | Android system TTS | none | system-provided |

Model runtimes are pinned (exact versions in Appendix F). Runtimes are compiled into the app as AAR/native libs; **models are never bundled** — they install as side-loaded `.odpack` files (F-078), keeping the APK ≤ 25 MB (§26.4) and letting owners choose what fits their device.

## 19.2 Scan-to-doc (F-071 … F-073)

Flow: camera screen (CameraX, no internet-capable extensions) → auto-capture on focus → perspective crop editor (drag 4 corners, rotate) → per-page OCR → review screen where recognized text sits beside the page image with **confidence coloring + underline style** (UX-41, DQ-4): low-confidence words (score < 0.82) are marked; tapping a word focuses an inline fix field. "Insert into document" appends pages as paragraph blocks (page headers as separators); the source images attach as assets linked in the conversion note. Without the OCR pack the flow ends after crop at "Save image to document" with a one-line reason (F-073, F-082). Multi-page (F-072): pages queue with thumbnails, reorder before OCR batch runs.

## 19.3 Dictation (F-074)

The dictation strip appears above the keyboard: live partial transcript, stop → preview card with the full text (editable) → Insert at cursor as one grouped op (undoable as one step, UX-06). Language: pack language or system locale for the SpeechRecognizer rung; never both at once. Mic permission is requested the first time dictation opens (UX-32: no pre-prompt), and audio is never buffered to disk — frames live in memory until transcription, then are dropped (§20.4).

## 19.4 The availability ladder (F-076, F-082 — normative)

![Every AI capability descends exactly one ladder: best pack → lighter model → system service → hidden with reason.](figures/fig-ai-ladder.png)

| Rung | When | Example (assistant) |
|---|---|---|
| 1 | requested | user taps Summarize |
| 2 | pack present, SHA ok, RAM+thermal ok | gate check passes |
| 3 | best on-device model | gemma-2B 4-bit (Tier A) |
| 4 | lighter local method, no LLM | extractive summary (TextRank over block embeddings or sentence scoring) |
| 5 | system service | system SpeechRecognizer for dictation on Tier C |
| 6 | hidden with reason | control not shown; long-press explains: tier / pack missing / RAM |

Rules: the ladder step taken is recorded in the preview card (UX-47) and diagnostics; rung 6 is a *hidden control*, never a disabled one (F-082) and never an error dialog. Thermal/RAM gates: before loading the LLM, `ActivityManager` memory class + a thermal-status check (PowerManager.OnThermalStatusChangedListener); at "severe" the runtime swaps to rung 4 mid-session and says so in the card.

## 19.5 The assistant surface (F-075, F-077)

Four verbs: **Summarize** (selection → bullet digest; doc → abstract), **Rewrite** (polish / formal / casual), **Continue writing** (two-sentence continuation from cursor, style-matched), **Fix grammar** (selection-level corrections presented as a diff list, each item individually accepted). Every output lands in a **preview card** with method label, token-stream rendering, Cancel, and explicit Insert/Replace — insertion snapshots `pre_edit` first (F-077, Law L10). The card is the only AI surface; there is no ambient/inline ghost-text anywhere in v1.0 (deliberate: Law L10 plus battery discipline).

Prompting: fixed system prompts stored in `core-ai/assets/prompts.json` (versioned, deterministic, temperature 0.3, max 512 new tokens); the document context is truncated by block boundaries to the model's window; prompts never contain metadata beyond the selected text. The prompts and decoding params are acceptance-tested: TC-AI-010 pins a set of summarization fixtures with quality rubric checks (extractive-faithfulness heuristics) and runtime-invariance checks (same input → same output).

## 19.6 Pack manager (F-078, F-079)

Packs are `.odpack` zips: `manifest.json` (name, version, minRamMb, tier, license, files[] with sha256), model files, license text. Install: SAF pick → streaming SHA-256 verify → copy into `files/packs/<name>/` → registry row in `meta` → capability appears. Verify runs again at every load (files can rot on disk); mismatch ⇒ refused with both hashes shown (UX-48) and ladder descent. Delete frees space with confirm. The manager shows per pack: size, tier requirement, license name, verification state. No pack ever ships inside the APK; no download path exists anywhere in the code (C5) — the direct-APK QA proves network silence during every AI flow (TC-SEC-P-03).

## 19.7 Read aloud (F-080, F-081)

System `TextToSpeech` only — no neural pack in v1.0 (recorded as a D-reserved decision for v1.1). Sentence highlight follows `onRangeStart`; the reader controls are play/pause/stop + rate via system settings. If no TTS engine exists (rare), the control hides with reason (ladder rung 6).

## 19.8 AI performance and memory budgets

| Capability | Model | Tier B (3 GB AVD) budget | Tier A (8 GB) budget | Enforced by |
|---|---|---|---|---|
| OCR | DBNet-lite+CRNN int8 | ≤ 12 s/page; peak RSS +250 MB | ≤ 6 s/page | TC-AI-001 timed |
| ASR | whisper int8 streaming | RTF ≤ 0.6; first partial ≤ 1.5 s | RTF ≤ 0.35 | TC-AI-003 timed |
| LLM | gemma-2B q4_0 | not loaded (Tier gate) | first token ≤ 2.5 s; ≥ 8 tok/s; peak RSS +1.9 GB | TC-AI-005 timed |
| Embeddings | MiniLM-L6 int8 | ≤ 25 ms/block; index 10k blocks ≤ 60 s idle | ≤ 12 ms/block | TC-SRCH-005 timed |
| Read aloud | system TTS | system-provided | system-provided | TC-AI-007 |

Budget breach = S2 defect (§25.2). The AI executors run at `THREAD_PRIORITY_BACKGROUND` except during an active user action; embedding backfills yield to any user interaction (checked by a scheduler test).

## 19.9 AI privacy rules (all capabilities)

1. No audio, image, text, or embedding ever leaves the process (structural: no network path exists — C1; probes re-verify per RC: TC-SEC-P-03).
2. Audio frames are memory-only, dropped after insert (§20.4); scan images are written only when the user chooses "save image asset".
3. Embeddings are stored per-block in `vectors` with the pack's model id; deleting the pack deletes its vectors (space honesty, F-078).
4. The assistant's context window contains document text only — never metadata, never other documents.
5. Every AI surface labels its method and model (UX-47); diagnostics show last-run stats (duration, rung) but no content.

## 19.10 The prompt library (verbatim, versioned in `core-ai/assets/prompts.json`)

System prompt — SUMMARIZE:
```
You are a concise summarizer inside an offline writing app. Summarize the TEXT
for the document's author. Use at most 6 bullets or 2 sentences, whichever
fits the content. Quote key figures exactly. Never invent facts. Output only
the summary, no preamble.
```

System prompt — REWRITE (variant slot: polish / formal / casual):
```
You are a careful rewriter inside an offline writing app. Rewrite the TEXT in
a {polish|formal|casual} register. Preserve meaning, names, numbers and
formatting cues. Keep length within ±20%. Output only the rewritten text.
```

System prompt — CONTINUE:
```
You are a co-writer inside an offline writing app. Continue the TEXT with at
most two sentences that match its voice, tense and formatting. Do not repeat
existing phrases. Output only the continuation.
```

System prompt — FIX GRAMMAR:
```
You are a precise copy editor inside an offline writing app. List each grammar
or spelling fix in the TEXT as: ORIGINAL -> CORRECTED. One per line, in order.
If there are no issues output exactly: NO_ISSUES. Never change meaning.
```

Decoding: temperature 0.3, top-p 0.9, max 512 new tokens, seed pinned per run (invariance tested, TC-AI-010). Changing any prompt is a D-nnn decision + TC-AI-010 re-run.

## 19.11 The .odpack format (normative)

```
pack.odocpack (zip, store or deflate)
├─ manifest.json
├─ models/<files…>          # exact names per manifest
└─ LICENSE.txt
manifest.json:
{
  "format": 1,                        # pack format version (app accepts ≤ 2)
  "name": "ocr-en",                   # registry key
  "capability": "ocr|asr|llm|embed",
  "version": "1.3.0",
  "language": "en",
  "minRamMb": 2048,
  "tier": "A|B|C",                    # minimum tier for any use
  "files": [ {"path": "models/det.onnx", "sha256": "…", "bytes": 9123441} ],
  "license": "Apache-2.0",            # spdx id; full text in LICENSE.txt
  "runtime": {"engine": "onnxruntime", "min": "1.17.0"}   # app refuses older runtimes
}
```

Rules: total unpacked size capped at 8 GB; zip entries validated (count ≤ 64, no absolute/`..` paths — TC-SEC-PK-02); SHA-256 verification streams (no full-load into RAM); verification state cached with file mtime+size re-check on every load. The manager UI never hides the license — install confirm shows spdx id + links (text) to LICENSE.txt inside the pack.

## 19.12 The OCR and ASR pipelines in detail

**OCR preprocessing.** Captured frame → grayscale → local adaptive binarization (Sauvola window 31, k 0.34 — chosen for receipt/whiteboard robustness) → deskew via Hough text-line angle (±15° clamp) → perspective rectify from crop quad → resize to detector input (long edge 960 px, aspect preserved, letterbox).

**Detection (DBNet-lite).** Input 1×960×N; output probability map → threshold 0.3 → connected components → polygon simplify (Douglas-Peucker ε=2 px) → rotated boxes. Page-text filter: drop boxes with height < 8 px source or fill ratio < 0.25 (noise, page edges).

**Recognition (CRNN int8).** Per box (batched ≤ 8): crop → height-32 resize, width ≤ 512 (long boxes tile with 16 px overlap, merged by CTC blank alignment); CTC beam (width 4) over the en charset (94 glyphs + case); output text + per-character confidence = frame posterior max.

**Confidence aggregation.** Word confidence = min of char confidences (pessimistic — marks the word if ANY glyph is unsure); threshold 0.82 (§19.2). Page confidence shown as chip; < 0.6 page-level → "low yield" state offers retake (OD-SCAN-003 states).

**ASR (whisper.cpp) streaming.** 16 kHz mono PCM frames (VAD-gated, 30 ms silence = segment hint); 10 s sliding window with 1 s overlap; partial = decode current window (temperature 0.0, no re-sampling); final on stop = full-buffer decode with condition-on-previous-text; language pinned to pack language; timestamps suppressed (we render live, not timed captions).

Both pipelines are CPU/GPU-delegate configurable with a benchmark at first pack load choosing the delegate (decision cached per device, diagnostics-visible). Numeric defaults above are the v1.0 pins; changing one is a D-nnn entry + TC-AI-001 re-run.

## 19.13 Model cards (what each pack is and is not)

**ocr-en (DBNet-lite + CRNN int8).** Trained for printed Latin text 8–40 pt on plain backgrounds. Strong: books, letters, screenshots of text. Weak: handwriting, dense tables (columns linearize), stylized fonts, low light — hence confidence marks and the fix pass (§19.2). Not a translator, not a layout parser.

**asr-en (whisper int8).** Single-channel near-field speech en-US/en-IN. Strong: dictation pace, meeting proximity. Weak: far-field, heavy accents beyond training, music. Verbatim by design (no silent cleanup) — tidy is explicit (§19.3).

**llm-gemma2b (gemma-2B-it q4_0).** Short-form assist: summaries ≤ 6 bullets, rewrites ±20%, two-sentence continuations, grammar lists. Not: long-form generation, citations, facts from outside the text (prompts forbid invention; TC-AI-010 rubric enforces). Tier A-only; thermal descends to extractive.

**embed-minilm (MiniLM-L6 int8).** English semantic similarity for "related" ranking. Not a search engine replacement — it ranks *below* lexical hits (§17.6), never above; wrong-language packs must not be installed over en corpora (language field checked at load).

Each card ships inside its pack manifest (`about` field) and renders in the pack manager detail sheet — the owner reads what they installed without leaving the app.

## 19.14 Dictation quality expectations per locale (set at v1.0, honestly)

en-US/en-IN (pack + system rungs): WER ≤ 15% near-field (fixture V.2). hi-IN (system rung only in v1.0 — no hi ASR pack; shelf item): WER targets are system-dependent, so the UI promises *not* accuracy but liveness (partials + explicit insert); the pack manager marks hi ASR "coming with pack v1.x" rather than shipping a weak model (§30.2). This is the honesty pattern for every AI capability: ship where the bar is provable, label where it isn't, never fake confidence.

## 19.15 Assistant edge-case matrix (each cell has a behavior + test)

| Input | Behavior | Test |
|---|---|---|
| selection > 4,000 words | auto-chunk summarization (per-chunk bullets, merged, labeled "long text, chunked") | TC-AI-004-b |
| empty / 1-word document | verbs hidden; sheet explains "write a little first" | TC-AI-009-b |
| RTL (Hebrew/Arabic paste) | rewrite preserves direction; preview renders RTL | TC-AI-004-c |
| text inside tables | verbs operate on the selected cell's blocks only | TC-AI-004-d |
| code blocks | excluded from Summarize/Fix (not prose); Continue skips code | TC-AI-004-e |
| mixed-language selection | method label notes dominant language; no translation ever | TC-AI-004-f |
| offline-from-first-launch (never had packs) | every AI surface hidden with pack reason; no crashes, no empty sheets | TC-ENV-004-b |
| generation while typing elsewhere | generation continues in card; insertion only after explicit tap; no caret steal | TC-AI-006-b |
