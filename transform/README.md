# Hamann XML Transnormer

This `uv` project applies
[`textplus-bbaw/transnormer-19c-beta-v02`](https://huggingface.co/textplus-bbaw/transnormer-19c-beta-v02)
to historical German character data without sending XML markup to the model.

The input is validated and selected with `lxml`. Each complete physical line is
flattened across inline elements before inference, so a spelling such as
`wi<del>ß</del>en` is sent to the model as `wißen`. Character-level alignment
projects the result back into the original text slots. XML markup, attributes,
comments, indentation, and unchanged entity references retain their original
serialization.

Text inside `nr`, `gr`, and `hb` is preserved and acts as a normalization
barrier. All other inline text, including `aq`, is sent to the model.

## Setup

From this directory:

```sh
uv sync
```

The first model-backed run downloads roughly 1.2 GB of model weights into the
Hugging Face cache. This project locks the CPU-only PyTorch build. Using CUDA
requires replacing that dependency with a CUDA build compatible with the GPU.

## Test sample

```sh
uv run transnorm-xml \
  testdata/briefe-sample.xml \
  testdata/briefe-sample.normalized.xml \
  --alignment-report testdata/briefe-sample.alignment.jsonl
```

## Full file

Create a separate output first:

```sh
uv run transnorm-xml \
  ../briefe.xml \
  ../briefe.normalized.xml \
  --alignment-report ../briefe.normalized.alignment.jsonl \
  --batch-size 4
```

Use `--letters 1,600,552a` to process only selected `letterText` IDs. Unselected
letters remain byte-for-byte unchanged. Use `--device cpu` or `--device cuda`
to override automatic device selection after installing a matching PyTorch
build.

The JSONL report records source and normalized text, word-level edit groups,
and `ambiguous_markup_spans`. A nonzero ambiguity count means one model edit
crossed multiple XML text slots, so the exact placement of that edit should be
reviewed.

During inference, the command displays completed segments, percentage, elapsed
time, processing rate, and estimated remaining time. Pass `--no-progress` to
disable this display.
