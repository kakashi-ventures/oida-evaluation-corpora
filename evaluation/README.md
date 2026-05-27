# Evaluation Scripts

Scripts to reproduce the evaluation results reported in the paper.

For the benchmark format (corpus / queries / qrels / epistemic) see
[`../docs/format.md`](../docs/format.md); for how relevance grades were assigned
see [`../docs/relevance-guidelines.md`](../docs/relevance-guidelines.md). Standard
retrieval metrics (nDCG@k, Recall@k, MAP) can be computed directly from each
corpus's `qrels/test.tsv` with any BEIR-compatible evaluator; the scripts below
compute the paper's epistemic-quality metrics on top of system responses.

## Prerequisites

```bash
pip install -r requirements.txt
```

Requires an API key for the LLM judge (Claude Sonnet 4.6 used in the paper):

```bash
export ANTHROPIC_API_KEY=your_key_here
```

## Scripts

### `eqs_scorer.py`

Computes the Epistemic Quality Score (EQS) for a set of response pairs. Implements the five sub-scores (ECA, CP, CR, EC, DE) with calibrated 4-point anchors and the composite weighting from Section 4.1.

```bash
python eqs_scorer.py --responses responses.json --output results.csv
```

### `question_analysis.py`

Runs the QUESTION declaration rate analysis (Section 4.2, Table 4). Computes Fisher's exact test, Haldane-Anscombe odds ratio, and McNemar test for paired binary outcomes.

```bash
python question_analysis.py --brook brook_responses.json --baseline baseline_responses.json
```

## Response Format

Input JSON files should contain an array of response objects:

```json
[
  {
    "id": 1,
    "query": "What are the main bottlenecks...",
    "response": "Based on the organizational knowledge...",
    "input_tokens": 3868,
    "has_ignorance_declaration": true
  }
]
```
