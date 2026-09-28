# IndicTrans2 True Lean CT2 INT8 Validation Harness

## Prototype Validation Status

This directory contains an isolated, standalone prototype validation harness for evaluating the official **AI4Bharat IndicTrans2 CTranslate2 INT8 (`ct2_int8_model`)** runtime in a resource-constrained container environment.

> [!IMPORTANT]
> **Independent Prototype — Not Production SpecWise**: IndicTrans2 is **not** integrated into the SpecWise production engine, API, or frontend. No multilingual capabilities are claimed or deployed in production. A successful test run verifies only isolated model-loading and translation accuracy for this specific harness.
>
> In any future SpecWise multilingual integration, original procurement text must remain preserved alongside any translation for audit and validation purposes. This benchmark does not establish production multilingual accuracy, BIS approval, nationwide coverage, or legal compliance.

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
  ctranslate2==4.5.0
  sentencepiece==0.2.0
  indic-nlp-library-itt==0.1.1
  sacremoses==0.1.1
  huggingface_hub==0.28.1
  psutil==5.9.8
  ```
  *These exact pinned versions were verified during the successful Colab validation run. Render must use the same pinned versions for a controlled and reproducible comparison.*

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