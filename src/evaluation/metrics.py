"""
metrics.py
==========
All the numbers we report in the thesis.

TWO GROUPS:
1. Standard metrics (borrowed, well-understood):
   - retrieval: recall_at_k, mrr, ndcg
   - QA:        exact_match, f1, rouge

2. Novel temporal metrics (OUR contribution -- these answer the RQs):
   - temporal_accuracy_rate (TAR): % of answers citing only laws valid at
     the query date.
   - hallucination_rate (HR): % of answers citing non-existent or superseded
     laws.  <- directly answers RQ2 / RQ3
   - temporal_consistency (TC): ask the same question at different dates;
     does the answer change correctly?  <- directly answers RQ4

WHAT IT WILL DO LATER:
Each function takes predictions + gold data and returns a float, so the
runner can build a results table across all models and modes.
"""


# ---- standard retrieval metrics ----
def recall_at_k(retrieved, relevant, k): ...
def mrr(retrieved, relevant): ...
def ndcg(retrieved, relevant, k): ...

# ---- standard QA metrics ----
def exact_match(pred, gold): ...
def f1(pred, gold): ...
def rouge(pred, gold): ...

# ---- NOVEL temporal metrics (our contribution) ----
def temporal_accuracy_rate(answers, gold): ...   # TAR
def hallucination_rate(answers, valid_doc_ids): ...  # HR
def temporal_consistency(answers_by_date): ...   # TC
