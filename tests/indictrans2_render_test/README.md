# IndicTrans2 True Lean CT2 INT8 Validation Harness

## Prototype Validation Status

This directory contains an isolated, standalone prototype validation harness for evaluating the official **AI4Bharat IndicTrans2 CTranslate2 INT8 (`ct2_int8_model`)** runtime in a resource-constrained container environment.

> [!IMPORTANT]
> **Independent Prototype — Not Production SpecWise**: IndicTrans2 is **not** integrated into the SpecWise production engine, API, or frontend. No multilingual capabilities are claimed or deployed in production. A successful test run verifies only isolated model-loading and translation accuracy for this specific harness.
>
> In any future SpecWise multilingual integration, original procurement text must remain preserved alongside any translation for audit and validation purposes. This benchmark does not establish production multilingual accuracy, BIS approval, nationwide coverage, or legal compliance.

## Render Deployment History

| Commit | Status | Notes |
|--------|--------|-------|
| `51596c3` | ❌ Build failed | Original PyTorch/Transformers harness — too heavy |
| `0cf00d7` | ❌ Build failed | Switched to lean CT2; executable-stack error with ct2 4.5.0 |
| `39f711b` | ❌ Runtime error | ct2 4.6.0 loads; model download failed: `GatedRepoError: 401` — `HF_TOKEN` not set in Render env |
| `df8a85b` | ❌ Runtime error | Fixed NameError `tgt_sp_file`; HF_TOKEN preflight + explicit auth added |
| `HEAD` | 🔄 Pending | README update + auth documentation |

### Gated Model Authentication

`ai4bharat/indictrans2-indic-en-dist-200M` is a **gated Hugging Face repository**. The Render deployment will fail at model download with `GatedRepoError: 401` unless a valid token is configured.

**To fix the 401 on Render:**
1. Go to the Render service dashboard → **Environment** tab.
2. Add a secret environment variable: `HF_TOKEN` = `<your Hugging Face User Access Token>`.
3. Ensure your HF account has **requested and been granted access** to the gated repo at [huggingface.co/ai4bharat/indictrans2-indic-en-dist-200M](https://huggingface.co/ai4bharat/indictrans2-indic-en-dist-200M).
4. The token must have at minimum **Read** permission.
5. Redeploy.

**Security constraints (enforced in code):**
- `HF_TOKEN` is read from the environment at runtime — never committed to source, Dockerfile, or `requirements.txt`.
- The harness prints only `HF_TOKEN_PRESENT=true` or `HF_TOKEN_PRESENT=false` — the token value is never logged, printed, or exposed.
- If `HF_TOKEN` is absent, the harness exits immediately with `sys.exit(1)` before any network call.
- All exception messages have the token value replaced with `[REDACTED]` via `safe_exception()`.

## True Lean CT2 INT8 Architecture

The harness decouples completely from heavy machine learning wrappers:

- **Execution Engine**: Single instance of `ctranslate2.Translator(compute_type="int8", device="cpu")`.
- **Completely Removed Frameworks**:
  - `torch` / `torchvision`
  - `transformers` / `tokenizers`
  - `IndicTransToolkit`
  - `sacrebleu`, `nltk`, `fairseq`, `tqdm`, `cython`, `pandas`, `lxml`, `sphinx`
- **Pinned Validated Dependencies**:
  ```txt
  ctranslate2==4.6.0
  sentencepiece==0.2.0
  indic-nlp-library-itt==0.1.1
  sacremoses==0.1.1
  huggingface_hub==0.28.1
  psutil==5.9.8
  ```
- **Render Compatibility Note**:
  - `ctranslate2==4.5.0` failed in the Render Free Linux container environment with an executable-stack loader error (`ImportError: libctranslate2-bc15bf3f.so.4.5.0: cannot enable executable stack as shared object requires: Invalid argument`).
  - `ctranslate2==4.6.0` is used because its upstream release notes indicate `-Wl,-z,noexecstack` linker flags were added to prevent executable-stack security denials on hardened Linux kernels.
  - This is a Render compatibility test, not a production integration.

## Official Preprocessing Order

The harness strictly preserves the official AI4Bharat 5-stage Indic $\rightarrow$ English preprocessing pipeline:

1. **Punctuation Normalization**: `punc_norm()` (official pure-Python normalization for quotes, dashes, non-breaking spaces).
2. **Regex & Entity Normalization**: `normalize_regex()` (official AI4Bharat spacing rules around punctuation and alphanumeric tokens).
3. **Indic Unicode Normalization**: `IndicNormalizerFactory().get_normalizer(lang)` for `hi` and `kn`.
4. **Indic Trivial Tokenization**: `trivial_tokenize(text, lang=lang)`.
5. **Script Transliteration**: `UnicodeIndicTransliterator.transliterate(text, "kn", "hi")` for Kannada $\rightarrow$ unified Devanagari vocabulary (identity for Hindi).
6. **SentencePiece Encoding**: `src_sp.encode_as_pieces()`.
7. **Framing & Truncation**: `[src_lang] + subwords[:254] + ["</s>"]`.
8. **CTranslate2 INT8 Beam Search**: `beam_size=5`, target prefix `[tgt_lang]`.
9. **SentencePiece Decoding**: `tgt_sp.decode_pieces()`.
10. **English Target Postprocessing**: `MosesDetokenizer("en")` and punctuation cleanup.

## Memory & Resource Target

- **Observed Colab Benchmark**:
  - Model load RSS: ~490.44 MiB
  - Peak RSS: ~506.85 MiB
  - Average inference latency: ~0.565 s
- **Render Free Tier Notice**: While the 506.85 MiB peak RSS was measured in Colab, **Render Free tier (512 MiB ceiling) compatibility remains UNVERIFIED until an actual Render deployment executes**. Operating system container overhead and memory fragmentation on Render may differ.

## Validation Cases & References

The harness validates four procurement cases with deterministic parity checking:

1. **Hindi**: `सिंचाई के लिए 5 HP ओपनवेल सबमर्सिबल पंपसेट की आपूर्ति करें।`
   - Reference: `Supply 5 HP openwell submersible pumpsets for irrigation.`
2. **Kannada**: `ನೀರಾವರಿಗಾಗಿ 5 HP ಓಪನ್ವೆಲ್ ಸಬ್ಮರ್ಸಿಬಲ್ ಪಂಪ್ಸೆಟ್ ಪೂರೈಸಬೇಕು.`
   - Reference: `A 5 HP openwell submersible pumpset should be supplied for irrigation.`
3. **Hindi technical**: `IS 14220:2018 के अनुसार सिंचाई के लिए 5 HP ओपनवेल पंपसेट और 25 mm पाइप दें।`
   - Reference: `Give 5 HP open well pumpsets and 25 mm pipes for irrigation as per IS 14220:2018.`
4. **Kannada technical**: `IS 14220:2018 ಪ್ರಕಾರ ನೀರಾವರಿಗಾಗಿ 5 HP ಓಪನ್ವೆಲ್ ಪಂಪ್ಸೆಟ್ ಮತ್ತು 25 mm ಪೈಪ್ ಒದಗಿಸಿ.`
   - Reference: `Provide a 5 HP openwell pumpset and 25 mm pipe for irrigation according to IS 14220:2018.`

## Security & Secrets

- `HF_TOKEN` is supplied strictly as a runtime environment variable for gated model access.
- It is never logged, stored in images, or committed to source control. All exceptions mask tokens with `[REDACTED]`.