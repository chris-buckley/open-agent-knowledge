"""Revision-pinned manual assistant sessions with explicitly labelled numerical replay."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import time
import numpy as np
from oak import Node, Constant, Schema, Type, NonEmpty, where, parse, render
from evaluation.task import SEEDS, dataset, initial, metrics, accept, assert_split_separation
from nodes.author import write
from runtime.numeric import parameters, forward
from runtime.oak_adapter import load, source_revision, export, oak_forward
from training.optimise import adam, fit_concept

HERE = Path(__file__).resolve().parents[1]
FIELDS = {"baseline": "string", "observation": "string", "owner": "string", "method": "string",
          "rationale": "string", "actor": "string"}
METHODS = ("concept", "head", "concept-head")


def save_json(path: Path, obj):
    path.write_text(json.dumps(obj, sort_keys=True, indent=2, allow_nan=False)+"\n")


def record(path: Path, values: dict, *, proposal=False):
    schema = []
    if proposal:
        schema = [Schema(id="proposal", template="\n".join(f"{k}: <{k.upper()}>" for k in FIELDS),
            where=[where(k.upper(), Type(of=v), NonEmpty()) for k,v in FIELDS.items()])]
    constants = [Constant(id=k, value=v, **({"schema": "schema.proposal", "placeholder": k.upper()} if proposal else {})) for k,v in values.items()]
    text = render(Node(constants=constants, schemas=schema))
    if render(parse(text)) != text:
        raise ValueError("record does not round trip")
    with path.open("x", encoding="utf-8") as f:
        f.write(text)


def read_record(path):
    return {c.id:c.value for c in parse(path.read_text()).constants}


def code_hashes():
    return {p.relative_to(HERE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(HERE.rglob("*.py")) if "results" not in p.relative_to(HERE).parts}


def verify_frozen(work: Path):
    frozen = json.loads((work/"freeze.json").read_text())
    if code_hashes() != frozen["code"]:
        raise ValueError("experiment implementation changed after freeze")
    if hashlib.sha256((HERE/"evaluation/study.oak.md").read_bytes()).hexdigest() != frozen["study"]:
        raise ValueError("study changed after freeze")
    return frozen


def current(work: Path, seed: int):
    base = work/str(seed)
    name = (base/"CURRENT").read_text().strip()
    directory = base/"snapshots"/name
    return base, directory, load(directory)[0]


def prepare(work: Path):
    work.mkdir(parents=True, exist_ok=False)
    freeze = {"code":code_hashes(), "study":hashlib.sha256((HERE/"evaluation/study.oak.md").read_bytes()).hexdigest(),
              "python":sys.version, "numpy":np.__version__, "platform":platform.platform(),
              "upstream_baseline":"a825c588b699b453bb24703c68bb724b033b0797",
              "agent_count":1, "numerical_module_count":4, "trainable_module_count":3,
              "trainable_parameters":11, "scheduling":"sequential shared-context assistant", "model_identity":"GPT-6 Pro (session identity, not an independently attested API model id)",
              "provider_tokens":None, "provider_cost":None, "token_cost_reason":"not exposed by this conversation runtime"}
    save_json(work/"freeze.json",freeze)
    t0 = time.perf_counter()
    for seed in SEEDS:
        base = work/str(seed); (base/"snapshots").mkdir(parents=True)
        x,y=dataset(seed,"train"); dev=dataset(seed,"dev")
        w=initial(seed); write(w,base/"snapshots/initial")
        warm=adam(w,x,y,steps=50,rate=.03)
        write(warm,base/"snapshots/warm")
        # Stronger tuning budget than the assistant treatment, explicitly accounted.
        trials=[adam(warm,x,y,steps=400,rate=r,dev=dev) for r in (.01,.03,.1)]
        best=min(trials,key=lambda a:metrics(a,*dev)["bce"])
        write(best,base/"snapshots/numerical")
        (base/"CURRENT").write_text("warm\n")
        (base/"proposals").mkdir(); (base/"decisions").mkdir(); (base/"observations").mkdir()
        save_json(base/"split-identities.json",assert_split_separation(seed))
        save_json(base/"baseline.json",{"dev": {"initial":metrics(w,*dev),"warm":metrics(warm,*dev),"numerical":metrics(best,*dev)},
                  "gradient_steps":1250,"numerical_selection_evaluations":54,"preparation_development_metric_calls":57})
    save_json(work/"preparation.json",{"seconds":time.perf_counter()-t0, "test_metrics_observed":False})


def observe(work: Path, seed: int):
    verify_frozen(work)
    base,directory,w=current(work,seed)
    x,y=dataset(seed,"train"); p,t=forward(w,x,trace=True)
    values={"revision":source_revision(directory), "dev":metrics(w,*dataset(seed,"dev")),
            "weights":{k:v.tolist() for k,v in w.items()},
            "concept-mse":{k:float(np.mean((t[k]-x[...,i])**2)) for k,i in (("left",0),("right",1))},
            "training-errors":int(np.sum((p>=.5)!=y))}
    name=f"{len(list((base/'observations').glob('*.oak.md')))+1:03}.oak.md"
    path=base/"observations"/name; record(path,values)
    return path,values


def propose(work: Path, seed: int, owner: str, method: str, rationale: str, *, actor: str = "assistant"):
    verify_frozen(work)
    if (work/"final.json").exists() or (work/"SELECTION_CLOSED").exists():
        raise ValueError("candidate selection is closed")
    base,directory,w=current(work,seed)
    observations=sorted((base/"observations").glob("*.oak.md"))
    if not observations or read_record(observations[-1])["revision"] != source_revision(directory):
        raise ValueError("a fresh observation is required")
    if len(list((base/"proposals").glob("*.oak.md"))) >= 6:
        raise ValueError("six-proposal budget exhausted")
    if owner not in ("left","right","readout") or method not in METHODS:
        raise ValueError("unsupported proposal")
    if (method=="head") != (owner=="readout"):
        raise ValueError("head fitting must target readout; concept methods target selectors")
    if not rationale.strip():
        raise ValueError("proposal needs a rationale")
    path=base/"proposals"/f"{len(list((base/'proposals').glob('*.oak.md')))+1:03}.oak.md"
    record(path,{"baseline":source_revision(directory),"observation":hashlib.sha256(observations[-1].read_bytes()).hexdigest(),
                 "owner":owner,"method":method,"rationale":rationale,"actor":actor},proposal=True)
    return path


def candidate(w: dict, seed: int, owner: str, method: str):
    x,y=dataset(seed,"train"); c=parameters(w); cost={"gradient_steps":0,"least_squares_calls":0}
    if method in ("concept","concept-head"):
        c,fit=fit_concept(c,x,owner)
        cost.update(fit); cost["least_squares_calls"]=1
    if method in ("head","concept-head"):
        c=adam(c,x,y,steps=400,rate=.05,owners=("readout",))
        cost["gradient_steps"]=400
    return c,cost


def apply(work: Path, seed: int, proposal: Path):
    verify_frozen(work)
    if (work/"SELECTION_CLOSED").exists():
        raise ValueError("candidate selection is closed")
    base,directory,w=current(work,seed); record_values=read_record(proposal)
    if set(record_values)!=set(FIELDS) or record_values["baseline"]!=source_revision(directory):
        raise ValueError("stale or malformed proposal")
    if proposal.parent.resolve()!=(base/"proposals").resolve():
        raise ValueError("proposal is not owned by this run")
    output=base/"decisions"/proposal.name
    if output.exists():
        raise ValueError("proposal was already evaluated")
    observed={hashlib.sha256(p.read_bytes()).hexdigest():read_record(p)["revision"] for p in (base/"observations").glob("*.oak.md")}
    if observed.get(record_values["observation"])!=record_values["baseline"]:
        raise ValueError("proposal has no matching observed evidence")
    if not all(isinstance(v,str) and v for v in record_values.values()) or record_values["actor"] not in ("assistant","replay"):
        raise ValueError("malformed proposal fields or actor")
    owner,method=record_values["owner"],record_values["method"]
    if owner not in ("left","right","readout") or method not in METHODS or (method=="head")!=(owner=="readout"):
        raise ValueError("invalid operation or owner")
    t0=time.perf_counter(); c,cost=candidate(w,seed,owner,method)
    name="candidate-"+proposal.name.split('.')[0]
    path=base/"snapshots"/name; write(c,path)
    c=load(path)[0]; dev=dataset(seed,"dev")
    before,after=metrics(w,*dev),metrics(c,*dev)
    accepted=accept(before,after)
    if source_revision(current(work,seed)[1])!=record_values["baseline"]:
        raise ValueError("baseline drift before acceptance")
    if accepted:
        tmp=base/"CURRENT.next";tmp.write_text(name+"\n");os.replace(tmp,base/"CURRENT")
    result={"proposal":hashlib.sha256(proposal.read_bytes()).hexdigest(),"baseline":record_values["baseline"],
            "candidate":source_revision(path),"accepted":accepted,"before":before,"after":after,
            "cost":cost,"seconds":time.perf_counter()-t0,"actor":record_values["actor"]+" proposal; numerical evaluation"}
    record(output,result)
    return result


def finish(work: Path):
    from evaluation.export_check import check_artifact
    verify_frozen(work)
    if (work/"SELECTION_CLOSED").exists():
        raise ValueError("selection already closed; do not overwrite a finished or partial run")
    proposals=sorted((work/"7/proposals").glob("*.oak.md"))
    if not proposals or any(not (work/"7/decisions"/p.name).exists() for p in proposals):
        raise ValueError("every assistant proposal must be evaluated before final testing")
    sequence=[read_record(p) for p in proposals]
    (work/"SELECTION_CLOSED").write_text("No further assistant decisions. Transfer runs are numerical replay.\n")
    selected={}; replay_costs={}
    # Finish all automatic selection before any final-test metrics are computed.
    for seed in SEEDS:
        base=work/str(seed); w=load(base/"snapshots/warm")[0]; dev=dataset(seed,"dev")
        replay=[]
        if seed==7:
            agent_path=current(work,seed)[1]
        else:
            for proposal in sequence:
                c,cost=candidate(w,seed,proposal["owner"],proposal["method"])
                before,after=metrics(w,*dev),metrics(c,*dev)
                ok=accept(before,after)
                replay.append({"method":proposal["method"],"owner":proposal["owner"],"accepted":ok,
                               "before":before,"after":after,"cost":cost,"actor":"numerical replay, not a new assistant decision"})
                if ok:w=c
            agent_path=base/"snapshots/agent-replay";write(w,agent_path)
            save_json(base/"replay.json",replay)
        replay_costs[str(seed)]=replay
        w=load(base/"snapshots/warm")[0]; x,y=dataset(seed,"train")
        # Non-agent semantic control: both known concept targets, then readout.
        solver,_=fit_concept(w,x,"left");solver,_=fit_concept(solver,x,"right")
        solver=adam(solver,x,y,steps=400,rate=.05,owners=("readout",))
        if not accept(metrics(w,*dev),metrics(solver,*dev)):solver=w
        write(solver,base/"snapshots/solver")
        rng=np.random.default_rng(seed+50000); random=parameters(w)
        for _ in range(6):
            c=parameters(random)
            owner=("left","right","readout")[int(rng.integers(3))]
            c[owner]+=rng.normal(0,.3,c[owner].shape)
            if accept(metrics(random,*dev),metrics(c,*dev)):random=c
        write(random,base/"snapshots/random")
        selected[str(seed)]={k:str((base/"snapshots"/k).relative_to(work)) for k in ("initial","warm","numerical","solver","random")}
        selected[str(seed)]["agent"]=str(agent_path.relative_to(work))
    save_json(work/"selected.json", {seed:{k:{"path":v,"revision":source_revision(work/v)} for k,v in entries.items()} for seed,entries in selected.items()})
    results={}; exports={}
    for seed in SEEDS:
        x,y=dataset(seed,"test"); results[str(seed)]={}
        for treatment,path in selected[str(seed)].items():
            w,_=load(work/path)
            results[str(seed)][treatment]=metrics(w,x,y)
        path=work/selected[str(seed)]["agent"];w,_=load(path)
        artifact=work/str(seed)/"export";model=export(path,artifact)
        checked=check_artifact(artifact,w,x)
        oak_error=float(np.max(np.abs(oak_forward(path,x[:2])-forward(w,x[:2]))))
        if oak_error>1e-12:raise ValueError("OAK executor differs from lowered graph")
        checked["oak_executor_max_error"]=oak_error
        exports[str(seed)]=checked
    summary={t:{m:{"mean":float(np.mean([results[str(s)][t][m] for s in SEEDS])),
                        "min":float(min(results[str(s)][t][m] for s in SEEDS)),
                        "max":float(max(results[str(s)][t][m] for s in SEEDS))}
                    for m in ("bce","accuracy","balanced_accuracy")} for t in selected["7"]}
    final={"results":results,"summary":summary,"exports":exports,
           "actual_assistant_seed":7,"transfer_seeds":[19,31],"actual_assistant_proposals":sum(p["actor"]=="assistant" for p in sequence),"replayed_proposals":sum(p["actor"]=="replay" for p in sequence),
           "independent_agent_population":False,"independent_test_rows":False,
           "uncertainty":"three-seed descriptive range only, not a confidence interval",
           "budgets":{"common_warm_steps":50,"numerical_steps_after_warm":1200,
                       "numerical_rates":[.01,.03,.1],"solver_steps_after_warm":400,"solver_fits":2,
                       "random_candidate_evaluations":6,"assistant_max_proposals":6},
           "scope":"small feasibility study; no claim of semantic or distributed-agent superiority"}
    save_json(work/"final.json",final)
    return final


def replay(work: Path, recorded: Path):
    """Replay published proposals; never label this as new language-model reasoning."""
    prepare(work)
    for original in sorted((recorded/"7/proposals").glob("*.oak.md")):
        r=read_record(original)
        observe(work,7)
        p=propose(work,7,r["owner"],r["method"],r["rationale"],actor="replay")
        apply(work,7,p)
    result=finish(work)
    expected=json.loads((recorded/"final.json").read_text())
    for seed in result["results"]:
        for treatment in result["results"][seed]:
            for metric in ("bce","accuracy","balanced_accuracy"):
                if not np.isclose(result["results"][seed][treatment][metric],expected["results"][seed][treatment][metric],rtol=1e-10,atol=1e-12):
                    raise ValueError("recorded result does not reproduce")
    return result
