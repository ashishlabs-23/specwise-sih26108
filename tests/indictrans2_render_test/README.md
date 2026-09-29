# IndicTrans2 ONNX INT8 Memory-Feasibility Test Harness

## Active Experiment Status

This directory contains an isolated, standalone prototype validation harness for evaluating the **third-party IndicTrans2 ONNX INT8 (`hari31416/indictrans2-indic-en-dist-200M-ONNX-int8`)** runtime in a resource-constrained container environment.

> [!IMPORTANT]
> **Independent Experimental Prototype — Not Production SpecWise**:
> - Current Runtime: **ONNX Runtime INT8 (`CPUExecutionProvider`)**
> - Candidate Model: `hari31416/indictrans2-indic-en-dist-200M-ONNX-int8` (Third-party dynamic INT8 ONNX conversion of `ai4bharat/indictrans2-indic-en-dist-200M`).
> - **Public Model — No `HF_TOKEN` Required**: Unlike gated PyTorch repositories, this ONNX model is public and requires no Hugging Face authentication tokens.
> - **Not Integrated in Production**: IndicTrans2 is **not** integrated into the SpecWise production search engine, API, or frontend. No multilingual claims or production deployments are active.
> - **Primary Objective**: Measure container RAM and runtime feasibility within the Render Free tier (512 MiB RAM limit).

---

## Memory Architecture & Strategy

To stay strictly below the **460 MiB target threshold** (leaving 52 MiB headroom on the Render Free 512 MiB container ceiling), the harness implements an aggressive memory-reduction strategy:

1. **Sequential Session Lifetime**:
   - **Phase 1**: Instantiate `encoder_model.onnx` session $\rightarrow$ run encoder on source tokens $\rightarrow$ capture `last_hidden_state` $\rightarrow$ explicitly delete session and invoke `gc.collect()`.
   - **Phase 2**: Instantiate `decoder_model.onnx` session $\rightarrow$ run initial step 0 $\rightarrow$ capture initial KV-cache $\rightarrow$ delete session and invoke `gc.collect()`.
   - **Phase 3**: Instantiate `decoder_with_past_model.onnx` session $\rightarrow$ run auto-regressive decoding loop $\rightarrow$ delete session and invoke `gc.collect()`.
   - *Encoder and Decoder sessions never reside in memory concurrently.*
2. **Execution Provider**: `CPUExecutionProvider` only.
3. **Execution Mode**: `ORT_SEQUENTIAL`.
4. **Threading**: `intra_op_num_threads = 1`, `inter_op_num_threads = 1`.
5. **Memory Allocator Settings**:
   - `enable_cpu_mem_arena = False` (memory freed immediately to OS).
   - `enable_mem_pattern = False`.
   - `enable_profiling = False`.
6. **Graph Optimization**: `ORT_DISABLE_ALL`.
7. **Inference Parameters**: Batch size 1, greedy decoding (`argmax`), bounded sequence length (`max_tokens = 64`).
8. **Minimal File Downloads**: Filtered download pulling only `.onnx`, `.onnx.data`, and tokenizer JSON files (~219 MiB total model weights).

---

## Test Execution

### Default Sanity Run (1 Representative Case)
For initial Render deployment validation, the harness evaluates one technical procurement case to confirm boot, loading, inference, and memory ceiling compliance:

- **Source (Hindi)**: `IS 14220:2018 के अनुसार सिंचाई के लिए 5 HP ओपनवेल पंपसेट और 25 mm पाइप दें।`
- **Prefix Format**: `hin_Deva eng_Latn <text>`
- **Expected Reference**: `Give 5 HP openwell pumpsets and 25 mm pipes for irrigation as per IS 14220:2018.`

```bash
python test_onnx_harness.py
```

### Full Suite Run (Optional Benchmark)
```bash
python test_onnx_harness.py --full-suite
```

---

## Pinned Runtime Dependencies

See [`requirements_onnx.txt`](requirements_onnx.txt):
```txt
onnxruntime==1.19.2
tokenizers==0.20.3
huggingface_hub==0.26.2
psutil==5.9.8
```

*Explicitly Excluded Heavy Frameworks*: `torch`, `transformers`, `ctranslate2`, `IndicTransToolkit`, `indic-nlp-library-itt`, `sacremoses`, `fairseq`.

---

## Historical Context: Prior CTranslate2 (CT2) Experiment

*(Archived — Superseded by ONNX INT8 experiment)*

The repository previously evaluated official and converted CTranslate2 INT8 weights:
1. `ai4bharat/indictrans2-indic-en-dist-200M` lacked official `ct2_int8_model/` files.
2. Third-party converted CT2 INT8 models packaged weights in 808–981 MiB `model.bin` files, immediately exceeding the Render Free 512 MiB ceiling.
3. Prior Render CT2 test deployment history:
   - `51596c3`: PyTorch / Transformers harness — build failed (exceeded resource limits).
   - `0cf00d7`: CTranslate2 4.5.0 — failed with container executable-stack denial (`libctranslate2.so: cannot enable executable stack`).
   - `39f711b`: CTranslate2 4.6.0 — resolved executable-stack; failed with `GatedRepoError: 401` on gated HF repo.
   - `df8a85b`: Fixed variable naming and added token preflight.