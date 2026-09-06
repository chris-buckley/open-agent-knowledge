"""Positive and negative checks of the implemented pilot, not a simulated study."""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
from oak import parse,render,Instruction
from evaluation.task import initial,dataset,metrics,accept,assert_split_separation
from evaluation.export_check import check_artifact
from evaluation.study import text
from nodes.author import write,documents
from runtime.numeric import forward,parameters,inputs,load_model
from runtime.oak_adapter import load,source_revision,export,oak_forward
from training.optimise import gradients,fit_concept
from training.session import record,read_record,code_hashes,verify_frozen,propose,apply,observe

class ExperimentTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.w=initial(0); self.x,self.y=dataset(0,"pilot")
        self.nodes=self.root/"nodes";write(self.w,self.nodes)
    def tearDown(self):self.temp.cleanup()

    def test_roundtrip_and_resolve(self):
        w,g=load(self.nodes)
        self.assertEqual(len(g.documents),6)
        for n in g.documents.values():
            for grouping in ("xml","markdown"):
                self.assertEqual(render(parse(render(n,grouping=grouping),grouping=grouping),grouping=grouping),render(n,grouping=grouping))
        self.assertTrue(np.array_equal(w['left'],self.w['left']))

    def test_oak_executor_numerical_parity(self):
        np.testing.assert_allclose(oak_forward(self.nodes,self.x[:2]),forward(self.w,self.x[:2]),rtol=1e-12,atol=1e-12)

    def test_inference_does_not_mutate_parameters(self):
        before=source_revision(self.nodes); old=copy.deepcopy(self.w)
        forward(self.w,self.x)
        self.assertEqual(before,source_revision(self.nodes))
        for k in old:np.testing.assert_array_equal(old[k],self.w[k])

    def test_gradient_finite_difference(self):
        x,y=self.x[:3],self.y[:3];g=gradients(self.w,x,y)
        for key in g:
            for i in range(g[key].size):
                a,b=copy.deepcopy(self.w),copy.deepcopy(self.w)
                a[key].flat[i]+=1e-5;b[key].flat[i]-=1e-5
                finite=(metrics(a,x,y)['bce']-metrics(b,x,y)['bce'])/2e-5
                self.assertAlmostEqual(finite,g[key].flat[i],places=7)

    def test_invalid_tensors(self):
        for value in ([[True,0.,0.,0.]],[[float('nan'),0.,0.,0.]],[[float('inf'),0.,0.,0.]],[[1,2,3]],[["1",0,0,0]],[]):
            with self.subTest(value=value),self.assertRaises(ValueError):
                w=copy.deepcopy(self.w);w['left']=value;parameters(w)
        with self.assertRaises(ValueError):inputs(np.zeros((1,3,4,3)))
        with self.assertRaises(ValueError):inputs(np.full((1,4,4,3),2.))
        with self.assertRaises(ValueError):inputs(np.empty((0,4,4,3)))

    def test_frozen_composition(self):
        w=copy.deepcopy(self.w);w['compose']=[[2.]]
        with self.assertRaises(ValueError):parameters(w)

    def test_missing_document(self):
        (self.nodes/'right.oak.md').unlink()
        with self.assertRaises((ValueError,KeyError)):load(self.nodes)

    def test_agent_instruction_rejected(self):
        p=self.nodes/'left.oak.md'; n=parse(p.read_text())
        n.instructions.append(Instruction(id='agent-repair',body='Ask an agent to repair the output.'))
        p.write_text(render(n))
        with self.assertRaises(ValueError):load(self.nodes)

    def test_unsupported_tool_rejected(self):
        p=self.nodes/'left.oak.md';p.write_text(p.read_text().replace('tensor.left.v1','agent.left.v1'))
        with self.assertRaises(ValueError):load(self.nodes)

    def test_symlink_rejected(self):
        p=self.nodes/'left.oak.md';q=self.root/'outside.oak.md';p.rename(q);p.symlink_to(q)
        with self.assertRaises(ValueError):load(self.nodes)

    def test_record_types_and_study_freshness(self):
        from training.session import HERE
        self.assertEqual((HERE/'evaluation/study.oak.md').read_text(),text())
        values={'baseline':'a'*64,'observation':'b'*64,'owner':'left','method':'concept','rationale':'Measured selector confusion.','actor':'assistant'}
        p=self.root/'proposal.oak.md';record(p,values,proposal=True)
        self.assertEqual(values,read_record(p))
        with self.assertRaises(FileExistsError):record(p,values,proposal=True)

    def test_concept_fit_ownership(self):
        c,_=fit_concept(self.w,self.x,'left')
        for key in ('right','compose','readout'):np.testing.assert_array_equal(c[key],self.w[key])
        self.assertFalse(np.array_equal(c['left'],self.w['left']))

    def test_splits(self):
        for seed in (7,19,31):self.assertEqual(set(assert_split_separation(seed)),{'train','dev','test'})

    def test_acceptance_and_interference(self):
        self.assertFalse(accept({'bce':.5,'accuracy':.8},{'bce':.6,'accuracy':.9}))
        self.assertFalse(accept({'bce':.5,'accuracy':.8},{'bce':.4,'accuracy':.7}))
        initial_error=(.5*.5-1)**2
        self.assertEqual((2*.5-1)**2,0)
        self.assertEqual((.5*2-1)**2,0)
        self.assertGreater((2*2-1)**2,initial_error)

    def test_clean_export_and_parameter_identity(self):
        out=self.root/'export';model=export(self.nodes,out)
        self.assertEqual(model['source_revision'],source_revision(self.nodes))
        result=check_artifact(out,self.w,self.x[:4])
        self.assertTrue(result['decision_equivalence'])
        model['weights']['left'][0][0]+=1
        (out/'model.json').write_text(json.dumps(model))
        with self.assertRaises(ValueError):check_artifact(out,self.w,self.x[:4])

    def test_unknown_export_operation(self):
        out=self.root/'export';model=export(self.nodes,out)
        model['operations'][0]='llm.call';(out/'model.json').write_text(json.dumps(model))
        with self.assertRaises(ValueError):load_model(out/'model.json')

    def test_stale_proposal_and_closed_run(self):
        from training.session import HERE
        work=self.root/'run';base=work/'7';(base/'snapshots').mkdir(parents=True)
        write(self.w,base/'snapshots/warm');(base/'CURRENT').write_text('warm\n')
        for name in ('observations','proposals','decisions'):(base/name).mkdir()
        (work/'freeze.json').write_text(json.dumps({'code':code_hashes(),'study':hashlib.sha256((HERE/'evaluation/study.oak.md').read_bytes()).hexdigest()}))
        observe(work,7);p=propose(work,7,'left','concept','Inspect selector then request concept fitting.')
        changed=copy.deepcopy(self.w);changed['left'][0,0]+=.1;write(changed,base/'snapshots/changed')
        (base/'CURRENT').write_text('changed\n')
        with self.assertRaisesRegex(ValueError,'stale'):apply(work,7,p)
        (work/'SELECTION_CLOSED').write_text('closed')
        with self.assertRaisesRegex(ValueError,'closed'):propose(work,7,'left','concept','Cannot change after final selection.')
