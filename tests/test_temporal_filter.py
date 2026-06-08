"""
test_temporal_filter.py
=======================
Tests for the core temporal rule -- the most important thing to get right.

WHY TEST THIS FIRST:
If the temporal filter is wrong, the whole thesis claim collapses. These
tests pin down the exact behaviour: a document valid on the query date is
kept; a superseded one is dropped; a not-yet-effective one is dropped;
effective_to = None means "still valid".

WHAT TO WRITE LATER (examples):
- test_keeps_currently_effective_document()
- test_drops_superseded_document()
- test_drops_not_yet_effective_document()
- test_null_effective_to_means_still_valid()
"""

# from src.temporal.temporal_filter import filter_by_date
# from datetime import date

# def test_drops_superseded_document():
#     ...
