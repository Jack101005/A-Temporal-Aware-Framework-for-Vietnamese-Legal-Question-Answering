"""
runner.py
=========
Runs the whole experiment grid and produces the results tables.

THE GRID:
    for each model in [PhoGPT, ViGPT-Law, GPT-4, Claude, Gemini, ...]
        for each mode in [no_rag, standard_rag, temporal_rag]
            answer every benchmark question
            compute all metrics

This is what generates the comparison tables that go straight into the
thesis (e.g. "temporal_rag cuts hallucination rate from 41% to 9%").

WHAT IT WILL DO LATER:
- run(models, modes, questions): loop the grid, collect metrics
- save_results(): write a CSV / DataFrame for plotting
- statistical_tests(): paired t-test + bootstrap CI between modes
"""


class EvaluationRunner:
    """Runs models x modes x questions and aggregates metrics."""

    def run(self, models: list, modes: list, questions: list):
        """TODO: loop the experiment grid, return a results table."""
        ...

    def save_results(self, results, path: str):
        """TODO: persist results to CSV for analysis/plotting."""
        ...
