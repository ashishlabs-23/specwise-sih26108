# IndicTrans2 Render Validation Harness

## Prototype Validation

This is an isolated Render/Linux prototype test for loading and running the official AI4Bharat IndicTrans2 inference path. It downloads and loads `ai4bharat/indictrans2-indic-en-dist-200M`, then prints actual outputs, load/end-to-end timings, generation timings, and technical-identifier diagnostics. Identifier survival is diagnostic only; it does not establish semantic correctness.

The harness uses `AutoTokenizer`, `AutoModelForSeq2SeqLM`, and `IndicProcessor` directly. It reads `HF_TOKEN` only from the environment. It does not use a translation pipeline, fixtures, external translation services, or SpecWise imports.

## Current SpecWise

IndicTrans2 is **not yet integrated into production SpecWise**. No multilingual capability should be claimed until this isolated validation succeeds. A successful run verifies only this model-loading and inference test, not an application integration or safe procurement analysis.

This harness makes no claim of production readiness, BIS certification, nationwide BIS coverage, real-time BIS synchronization, or legal/regulatory completeness.

## Future Work

Any later production proposal requires separate engineering and policy review. Intended safeguards include:

- Controlled multilingual normalization.
- Retaining both the original and translated representation.
- Bilingual/back-translation verification.
- Fail-closed behavior when translation drifts or checks fail.

## Model and Inputs

Model ID: `ai4bharat/indictrans2-indic-en-dist-200M`

The exact baseline sentences are:

- Hindi (`src_lang="hin_Deva"`): `सिंचाई के लिए 5 HP ओपनवेल सबमर्सिबल पंपसेट की आपूर्ति करें।`
- Kannada (`src_lang="kan_Knda"`): `ನೀರಾವರಿಗಾಗಿ 5 HP ಓಪನ್‌ವೆಲ್ ಸಬ್‌ಮರ್ಸಿಬಲ್ ಪಂಪ್‌ಸೆಟ್ ಪೂರೈಸಬೇಕು.`

One additional short procurement sentence per language includes an IS reference, year, HP, mm, and product/application wording. The script compares extracted identifiers before and after translation, allowing case/spacing differences. This check does not evaluate meaning.

## Render Execution

1. Create a separate Render service from a test branch. Do not attach production environment groups or credentials.
2. Select Docker and set both the root directory and build context to `tests/indictrans2_render_test`. Set the Dockerfile path to `Dockerfile` relative to that root.
3. Add `HF_TOKEN` as a secret environment variable on the isolated service. Do not put it in source, a Blueprint value, Dockerfile, build argument, or command.
4. Build the image. The Dockerfile installs CPU-only PyTorch plus this harness's dependencies and copies only the test script and requirements file.
5. Manually execute `python test_indictrans2.py` once against the isolated service's built image. Render one-off jobs can execute a command against an existing service build.
6. Collect the run logs, then delete or suspend the temporary test service after validation.

Initial smoke-test resource target: **1 CPU / 2 GB RAM; actual suitability must be established by the Render build/run.**