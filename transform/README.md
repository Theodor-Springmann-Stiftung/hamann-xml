# Hamann XML Transnormer

This `uv` project applies
[`textplus-bbaw/transnormer-19c-beta-v02`](https://huggingface.co/textplus-bbaw/transnormer-19c-beta-v02)
to historical German character data without sending XML markup to the model.

The input and output are validated with `lxml`. Character-level alignment
projects normalized text back into its original XML text slots. XML markup,
attributes, comments, indentation, punctuation, and unchanged entity
references retain their original serialization.

Text inside `nr`, `gr`, and `hb` is preserved and acts as a normalization
barrier. All other inline text, including `aq`, is processed. Words split by
inline markup are reconstructed before inference, so `<aq>disponir</aq>en` is
sent as `disponiren` and can be written back as `<aq>disponier</aq>en`.

## Modes

| Mode | Behavior | Typical use |
|---|---|---|
| `lines` | Sends each physical XML line with sentence context | Better normalization quality |
| `words` | Sends each unique word once and caches it in JSON | Much faster, reusable dictionary |

Line mode is the default. Word mode is faster but can make worse decisions
because the model was trained with sentence context. Review its dictionary and
alignment report before replacing production data.

## Setup

Run all following commands from the `transform` directory:

```sh
cd transform
uv sync
```

The first model-backed run downloads roughly 1.2 GB of model weights into the
Hugging Face user cache. The cache, `.venv`, and Python cache files are not
tracked by Git.

This project locks the CPU-only PyTorch build. Using CUDA requires replacing
that dependency with a CUDA-enabled PyTorch build compatible with the GPU.

## Line Mode

### Preserved sample

```sh
uv run transnorm-xml \
  testdata/briefe-sample.xml \
  testdata/briefe-sample.normalized.xml \
  --alignment-report testdata/briefe-sample.alignment.jsonl
```

### Selected letters

This processes only letters `1`, `600`, and `552a`. Every unselected letter is
copied byte-for-byte without inference.

```sh
uv run transnorm-xml \
  ../briefe.xml \
  ../briefe.selected.normalized.xml \
  --letters 1,600,552a \
  --alignment-report ../briefe.selected.alignment.jsonl \
  --batch-size 4
```

### Complete `briefe.xml`

```sh
uv run transnorm-xml \
  ../briefe.xml \
  ../briefe.normalized.xml \
  --alignment-report ../briefe.normalized.alignment.jsonl \
  --batch-size 4
```

On the tested i9-13900K CPU, four-beam line mode processed approximately
2.5-4 segments per second. The complete file took an estimated 12 hours.

## Cached Word Mode

Word mode ignores punctuation for inference, reconstructs words across inline
tags, sends each unique case-sensitive word once, and stores the result in a
JSON dictionary. Initial capitalization is retained. Punctuation and
whitespace are copied unchanged.

`briefe.xml` currently contains 73,365 unique words. The preserved sample ran
at approximately 39 words per second with batch size 64. Full-file performance
will vary.

### Preserved sample

```sh
uv run transnorm-xml \
  testdata/briefe-sample.xml \
  testdata/briefe-sample.words.normalized.xml \
  --mode words \
  --dictionary testdata/briefe-sample.words.dictionary.json \
  --alignment-report testdata/briefe-sample.words.alignment.jsonl \
  --batch-size 64
```

### Selected letters

```sh
uv run transnorm-xml \
  ../briefe.xml \
  ../briefe.selected.words.normalized.xml \
  --mode words \
  --dictionary ../briefe.words.dictionary.json \
  --letters 1,600,552a \
  --alignment-report ../briefe.selected.words.alignment.jsonl \
  --batch-size 64
```

### Complete `briefe.xml`

```sh
uv run transnorm-xml \
  ../briefe.xml \
  ../briefe.words.normalized.xml \
  --mode words \
  --dictionary ../briefe.words.dictionary.json \
  --alignment-report ../briefe.words.alignment.jsonl \
  --batch-size 64
```

### Reuse the dictionary

Run the same complete-file command again. Words already in the dictionary are
not sent to the model. The final summary reports them as `cached_words` and
reports `normalized_words: 0` when every input word was cached.

The dictionary is ordinary JSON and can be corrected manually. For example:

```json
{
  "ward": "wurde",
  "hätt": "hätte"
}
```

Keep these entries inside the dictionary's existing `words` object, then rerun
the same command. The corrected mappings are applied without new inference.

### Rebuild the dictionary

Move the previous dictionary aside, then run the complete word-mode command
again:

```sh
mv ../briefe.words.dictionary.json ../briefe.words.dictionary.previous.json
```

The next word-mode run creates a new dictionary using the configured model.
A dictionary is tied to its model ID; the command rejects one created for a
different model.

## Common Options

Disable the progress bar:

```sh
uv run transnorm-xml \
  ../briefe.xml \
  ../briefe.normalized.xml \
  --alignment-report ../briefe.normalized.alignment.jsonl \
  --no-progress
```

Use greedy decoding instead of the default four beams:

```sh
uv run transnorm-xml \
  ../briefe.xml \
  ../briefe.normalized.xml \
  --alignment-report ../briefe.normalized.alignment.jsonl \
  --num-beams 1
```

Greedy decoding is faster but can reduce normalization quality. Batch size
changes throughput and memory use but does not otherwise change the decoding
algorithm.

After installing a compatible CUDA-enabled PyTorch build, select the GPU with
`--device cuda`. Force CPU execution with `--device cpu`.

## Review Outputs

The XML output is validated before it is written. The JSONL alignment report
records source and normalized text, word-level edit groups, and
`ambiguous_markup_spans`. A nonzero ambiguity count means one model edit
crossed multiple XML text slots and should be reviewed.

Compare an output with the source:

```sh
git diff --no-index ../briefe.xml ../briefe.words.normalized.xml
```

`git diff --no-index` returns exit status 1 when it finds differences; that is
expected here.

After reviewing the XML and dictionary, replace the tracked source if desired:

```sh
mv ../briefe.words.normalized.xml ../briefe.xml
```

The original file is never overwritten automatically.
