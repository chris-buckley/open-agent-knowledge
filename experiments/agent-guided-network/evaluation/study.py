"""Generate the pre-registered, existing-OAK study record for the first small run."""
from pathlib import Path
from oak import Node, Constant, render


def text():
    return render(Node(constants=[
        Constant(id="study",value="sequential-assistant-feasibility-001"),
        Constant(id="status",value="Frozen before scored seed-7 observations. Pilot seed 0 is excluded."),
        Constant(id="roles",value={"proposers":1,"scheduling":"sequential, shared context", "numeric_modules":4,"trainable_modules":3,"oak_documents":6,"trainable_scalars":11}),
        Constant(id="task",value="Input X[batch,4,4,3]. Target ((X[...,0] @ X[...,1]) > 0) AND NOT X[...,2]. The rule and local concept targets are disclosed to the assistant and solver-only control."),
        Constant(id="equations",value=["LEFT = sigmoid(X @ W_left[:3] + W_left[3])", "RIGHT = sigmoid(X @ W_right[:3] + W_right[3])", "COUNT = LEFT @ RIGHT with frozen gain 1", "PROB = sigmoid(W_readout[0]*COUNT + W_readout[1]*X[...,2] + W_readout[2])"]),
        Constant(id="sampling",value={"channels":[.35,.35,.15],"train_worlds":128,"dev_worlds":64,"test_worlds":256,"seeds":[7,19,31],"seed_offsets":{"train":10000,"dev":20000,"test":30000},"duplicate_world_check":True}),
        Constant(id="selection",value={"primary":"development BCE","minimum_improvement":1e-6,"maximum_accuracy_drop":.02,"threshold":.5,"all_candidates_scored_without_agents":True}),
        Constant(id="budgets",value={"warm_adam_steps":50,"warm_rate":.03,"numerical_rates":[.01,.03,.1],"numerical_steps_per_rate":400,"numerical_check_interval":25,"assistant_proposals":6,"head_steps_per_proposal":400,"head_rate":.05,"concept_ridge":.001,"concept_target_probabilities":[.01,.99],"preservation_error_threshold":.05,"parameter_absolute_limit":64,"random_proposals":6,"random_scale":.3}),
        Constant(id="controls",value=["initial", "common warm start", "numerical Adam selected on dev", "automatic concept fitting plus readout Adam", "six random proposals", "one actual assistant session on seed 7", "numerical replay of that decision sequence on seeds 19 and 31"]),
        Constant(id="test-policy",value="No test metrics or examples are printed until the assistant sequence and every automatically selected comparison network are frozen. This is procedural separation, not an adversarial security boundary against the implementer."),
        Constant(id="export",value={"format":"generated model.json and inference.py", "dependency":"numpy==2.3.5 plus Python standard library", "dtype":"float64", "atol":1e-12,"rtol":1e-12,"decisions":"exact", "network":"blocked", "oak_imports":"absent"}),
        Constant(id="verdicts",value={"engineering":"mean test BCE improves over initial and all export checks pass", "scientific":"no superiority verdict from three seeds or unmatched conversation cost", "reporting":"means and seed ranges, including rejected updates"}),
        Constant(id="limits",value=["not 100 launched agents", "not independent agent populations", "not a general tensor compiler", "not a policy-enforcement proof", "no semantic ablation claim", "conversation token/cost telemetry is unavailable", "solver control has access to the same declared task concepts", "no automatic architecture search"]),
        Constant(id="pilot",value="Separate seed-0 pilot: initial BCE 0.664986; after 50 warm steps 0.515744; selector fitting can temporarily reduce accuracy. This motivated retaining rejection and joint-candidate handling, not changing the 0.02 regression cap after scored feedback."),
    ]))


if __name__=="__main__":
    Path(__file__).with_suffix('.oak.md').write_text(text())
