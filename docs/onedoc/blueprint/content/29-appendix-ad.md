# Appendix AD — Locale deck (hi + mr for the P.1–P.5 core keys)

Translation register: formal-polite (आप), same sentence-case discipline (no exclamation marks), numbers in Devanagari-friendly humanized form. Keys mirror Appendix P exactly; the strings lint fails a release if any key is missing in any shipped locale (F-090).

## hi (हिन्दी) — core keys

| Key | String |
|---|---|
| action.new.doc | नया दस्तावेज़ |
| action.export | निर्यात |
| action.rename | नाम बदलें |
| action.move.trash | ट्रैश में ले जाएँ |
| action.restore | पुनर्स्थापित करें |
| editor.count | {words} शब्द · {chars} अक्षर |
| editor.find.count | {total} में से {n} |
| ai.summarize / rewrite / continue / fix | सारांश · फिर से लिखें · आगे लिखें · व्याकरण ठीक करें |
| ai.unavailable.ram | {model} को {need} GB RAM चाहिए — इस फ़ोन में {have} GB है। |
| pack.verify.fail | जाँच असफल। अपेक्षित {expected}, मिला {found}। |
| trash.retention | मिटाए दस्तावेज़ 30 दिन रहते हैं। {days} दिन बाकी। |
| welcome.title | आपके शब्द, आपका फ़ोन। |
| welcome.body | OneDoc पूरी तरह ऑफ़लाइन चलता है। न अकाउंट, न विज्ञापन, न ट्रैकिंग। |
| welcome.cta | लिखना शुरू करें |

## mr (मराठी) — core keys

| Key | String |
|---|---|
| action.new.doc | नवीन दस्तऐवज |
| action.export | निर्यात |
| action.rename | नाव बदला |
| action.move.trash | कचरात हलवा |
| action.restore | पुन्हा आणा |
| editor.count | {words} शब्द · {chars} अक्षरे |
| editor.find.count | {total} पैकी {n} |
| ai.summarize / rewrite / continue / fix | सारांश · पुन्हा लिहा · पुढे लिहा · व्याकरण दुरुस्त |
| ai.unavailable.ram | {model} ला {need} GB RAM लागते — या फोनमध्ये {have} GB आहे. |
| pack.verify.fail | तपासणी अयशस्वी. अपेक्षित {expected}, आढळले {found}. |
| trash.retention | काढलेले दस्तऐवज 30 दिवस राहतात. {days} दिवस शिल्लक. |
| welcome.title | तुमचे शब्द, तुमचा फोन. |
| welcome.body | OneDoc पूर्णपणे ऑफलाइन चालते. खाते नाही, जाहिराती नाही, ट्रॅकिंग नाही. |
| welcome.cta | लिहायला सुरुवात करा |

(The full 120-key deck lives in `core/designsystem/strings.csv` generated with the build; this appendix pins the register and the highest-traffic strings. Locale runs per §23.5 verify rendering + truncation at 200%.)

# Appendix AE — Test-data provenance and privacy statement

All fixtures (Appendix J) are synthetic: generated letters, TTS-spoken audio with no real person, no real names, no GPS. No fixture encodes personal data; the EXIF fixture's GPS point is a null-island coordinate. This matters for two reasons: runs are reproducible byte-for-byte anywhere (Law L6 spirit), and the evidence PDF can be shared publicly without redaction. If the owner later contributes real documents for testing, they enter a separate `contrib/` directory (git-ignored by default, owner-synced), never the committed corpus.

# Appendix AO — Owner FAQ (the ten questions, answered once)

1. **Where do my documents live?** Inside the app's private storage on your phone, encrypted where your phone has a lock screen (§11.5). Backups go only where you choose.
2. **Can OneDoc send my text anywhere?** No — there is no internet permission in the app at all (C1); tests on the release APK prove zero network use (TC-SEC-P-03).
3. **What are the packs?** Optional AI models you side-load from files you hold; each is hash-verified; the app never downloads (§19.6).
4. **Why does the assistant disappear on my phone?** Its controls hide when the hardware can't run them — long-press any AI spot for the reason (§19.4). Nothing is broken.
5. **What happens if the app is killed mid-sentence?** Nothing is lost; the journal has it (Law L3, proven by 100 kill tests).
6. **Can I get my work into Word/Google Docs?** Yes — export DOCX/PDF/Markdown/HTML with stated fidelity (§18.2); the conversion note tells you exactly what kept or dropped.
7. **Does it work in airplane mode?** One hundred percent of it — that is the product (P1).
8. **Why no comments/co-editing?** OneDoc is a single-user, single-device studio by charter (§1.4); collaboration needs servers, and servers break every promise above.
9. **How do I know a release is the real one?** Compare the APK's SHA-256 to the provenance file; 5-minute runbook in §28.5.
10. **What if I find a bug?** The evidence PDF and defect tracker (§25) show how every claim is tested; report it and it joins the same system with a test that fails first.
