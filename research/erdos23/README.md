# Erdős Problem 23 verification

This isolated project checks the analytic core of a candidate result for Erdős Problem 23.

It proves these Lean declarations without `sorry`:

- `coverWeight_feasible`
- `coverWeight_cost`
- `reciprocal_constant_from_length_five`
- `cost_le_one_twenty_five`
- `odd_girth_cost_identity`
- `constructed_cover_cost_le_one_twenty_five`

The graph-specific cycle degree lemma and the published signed-graph integrality theorem remain separate proof dependencies. This project does not claim a full proof of Erdős Problem 23.
