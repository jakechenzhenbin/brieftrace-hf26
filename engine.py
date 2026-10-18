"""Local evidence retrieval. Similarity is never a contractual verdict."""
from pathlib import Path
import hashlib
import json
import re
import threading
import time

import numpy as np
import onnxruntime as ort
from tokenizers import Tokenizer

ROOT = Path(__file__).resolve().parent
MODEL_DIR = ROOT / "models"
LABELS = {"IN": "included", "OUT": "excluded", "LIMIT": "limit", "NOTE": "unspecified"}

class InputError(ValueError):
    pass

class LocalEncoder:
    def __init__(self):
        ort.disable_telemetry_events()
        manifest = json.loads((MODEL_DIR / "manifest.json").read_text(encoding="utf-8"))
        for item in manifest["files"]:
            path = MODEL_DIR / item["file"]
            if hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]:
                raise RuntimeError("Local model integrity mismatch. Re-run the explicit setup.")
        self.revision = manifest["revision"]
        self.tokenizer = Tokenizer.from_file(str(MODEL_DIR / "tokenizer.json"))
        self.tokenizer.enable_padding(pad_id=0, pad_token="[PAD]")
        opts = ort.SessionOptions()
        opts.intra_op_num_threads = 2
        self.session = ort.InferenceSession(str(MODEL_DIR / "model.onnx"), sess_options=opts, providers=["CPUExecutionProvider"])
        self.lock = threading.Lock()

    def encode(self, texts):
        with self.lock:
            encoded = self.tokenizer.encode_batch(texts)
            if any(len(item.ids) > 256 for item in encoded):
                raise InputError("A line exceeds the model's 256-token limit. Split it into shorter lines; no text was silently truncated.")
            values = {
                "input_ids": np.asarray([item.ids for item in encoded], dtype=np.int64),
                "attention_mask": np.asarray([item.attention_mask for item in encoded], dtype=np.int64),
                "token_type_ids": np.asarray([item.type_ids for item in encoded], dtype=np.int64),
            }
            feeds = {item.name: values[item.name] for item in self.session.get_inputs()}
            hidden = self.session.run(None, feeds)[0]
            mask = values["attention_mask"][..., None].astype(np.float32)
            pooled = (hidden * mask).sum(axis=1) / np.maximum(mask.sum(axis=1), 1e-9)
            return pooled / np.maximum(np.linalg.norm(pooled, axis=1, keepdims=True), 1e-9)

def parse_scope(text):
    if not isinstance(text, str) or not text.strip() or len(text) > 14000:
        raise InputError("Add a brief of up to 14,000 characters.")
    clauses = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        match = re.match(r"^\[(IN|OUT|LIMIT|NOTE)\]\s*(.+)$", line, re.IGNORECASE)
        tag, content = (match.group(1).upper(), match.group(2)) if match else ("NOTE", line)
        if len(content) > 1800:
            raise InputError("Keep each brief line below 1,800 characters.")
        clauses.append({"id": f"B{len(clauses)+1:02}", "kind": LABELS[tag], "text": content, "source": line})
    if len(clauses) > 24:
        raise InputError("Use at most 24 brief lines.")
    return clauses

def parse_requests(text):
    if not isinstance(text, str) or not text.strip() or len(text) > 6000:
        raise InputError("Add requests of up to 6,000 characters, one per line.")
    items = [line.strip() for line in text.splitlines() if line.strip()]
    if len(items) > 12 or any(len(x) > 1000 for x in items):
        raise InputError("Use at most 12 requests, each below 1,000 characters.")
    return items

def analyze(encoder, brief, requests):
    started = time.perf_counter()
    clauses = parse_scope(brief)
    queries = parse_requests(requests)
    vectors = encoder.encode([c["text"] for c in clauses] + queries)
    similarities = vectors[len(clauses):] @ vectors[:len(clauses)].T
    findings = []
    for index, request in enumerate(queries):
        order = np.argsort(-similarities[index])[:min(3, len(clauses))]
        matches = [{**clauses[int(i)], "similarity": round(float(similarities[index, i]), 4)} for i in order]
        top = matches[0]
        close_exclusion = next((m for m in matches if m["kind"] in ("excluded", "limit") and m["similarity"] >= 0.30 and top["similarity"]-m["similarity"] <= 0.08), None)
        if top["similarity"] < 0.30:
            status, note = "review", "No close wording found. Ask for clarification before agreeing."
        elif close_exclusion:
            status, note = "boundary", "An exclusion or limit appears among the close matches. Check the quoted evidence."
        elif top["kind"] == "included" and top["similarity"] >= 0.48:
            status, note = "related", "Related to included wording. Check quantity, revision counts and context before agreeing."
        else:
            status, note = "review", "Related wording found, but its scope is unclear. Human review is needed."
        findings.append({"id": f"R{index+1:02}", "request": request, "status": status, "note": note, "matches": matches})
    return {
        "findings": findings,
        "clauses": clauses,
        "model": "all-MiniLM-L6-v2 / local CPU",
        "model_revision": encoder.revision,
        "elapsed_ms": round((time.perf_counter()-started)*1000, 1),
        "network_requests_during_analysis": 0,
        "limitations": "English prototype. Semantic retrieval can miss negation, amounts and obligations. Scores are similarity, not confidence or a scope verdict. No price, contract or client message is generated automatically.",
    }
