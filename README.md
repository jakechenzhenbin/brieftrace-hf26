# BriefTrace

Find the original wording behind a client's new request, using a small open-weight model on your own computer.

**Local contest prototype, created 2026-10-18. Not published, sold, customer-validated or submitted.**

BriefTrace retrieves relevant clauses from a labelled brief. It shows the exact original wording beside each request and flags exclusions, limits and uncertain matches for human review. It does not decide contractual scope, generate prices, send replies or process payments.

## Run locally

Python 3.11+ is required. On this Windows machine the environment and model are already prepared: double-click `launch.bat`, or open <http://127.0.0.1:8793> while the local server is running.

For a clean installation:

```sh
python -m venv .venv
# Windows: .venv\Scripts\python ; macOS/Linux: .venv/bin/python
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python setup_model.py
.venv\Scripts\python server.py
```

Setup downloads packages from PyPI and about 91 MB of model files from the public, pinned Hugging Face repository. **Setup needs the internet. Subsequent analysis uses local files and no inference service.** No API key, cloud account or model-service subscription is required. The local server listens only on 127.0.0.1 and does not save text or log request bodies.

## Model and evidence

- Model: [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2), Apache-2.0, revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`.
- Runtime: ONNX Runtime CPU and Hugging Face Tokenizers. No remote model code is loaded.
- Algorithm: attention-mask-aware mean pooling, normalized embeddings, cosine retrieval of three brief clauses per request. Category labels come from the user's `[IN]`, `[OUT]`, `[LIMIT]` markers; labels are not invented by the model.
- Similarity thresholds are conservative prototype heuristics. They are not calibrated probabilities, entailment detection or a guarantee that a clause covers a request.
- Lines over the 256-token model limit are rejected, rather than silently cut off.

This is an English prototype. It can miss negation, changed quantities, revision counts and legal context. In particular, the model can retrieve the right clause while the tool still asks for review. That uncertainty is shown openly. Use the source text and your judgment.

## Verify

```sh
.venv\Scripts\python -m unittest -v test_engine
```

The checks use real local weights, including paraphrases, exclusion retrieval, exact-quote integrity, unfamiliar requests, a negated request, overlong input and Python network-socket blocking. They cover a small synthetic set, **not production accuracy or legal reliability**. The prepared public repository uses `docs/verification.json` for the actual run and local HTTP checks; the local review copy is `artifacts/verification.json`. Demo media and verification records are separate from the small source-only ZIP.

## Small commercial hypothesis

The proposed user is a freelance designer or small agency reviewing confidential client changes. An offline evidence view may be useful when uploading a brief to a SaaS tool is unwelcome. There are existing scope-change products, including [ScopePaid](https://www.scopepaid.com/) and [Fenscope](https://fenscope.com/). Their existence is evidence of a product category, not evidence that anyone will buy BriefTrace. No pricing, sales, user interview or willingness-to-pay is claimed here. This bounded build is a competition entry preparation, not a launched business.

## Credits and creation disclosure

The code, interface, examples and initial write-up were created with OpenAI Codex assistance. No professional development experience is asserted for the human participant. Human review and authorization are still pending. Model authors and runtime libraries retain their respective rights; see `THIRD_PARTY_NOTICES.md`. Example clients and requests are fictional. There are no copied client documents, testimonials or revenue claims.

The model and `.venv` are excluded from the source archive. `setup_model.py` reproduces the download and records local hashes. Model files are data, not a fine-tuned model claimed as original work.
