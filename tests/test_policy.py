import unittest,importlib.util,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];P=ROOT/'.hermes/plugins/off-data-venture'
spec=importlib.util.spec_from_file_location('offdata_plugin',P/'__init__.py',submodule_search_locations=[str(P)]);pkg=importlib.util.module_from_spec(spec);sys.modules['offdata_plugin']=pkg;spec.loader.exec_module(pkg)
policy=sys.modules['offdata_plugin.policy']
class PolicyTests(unittest.TestCase):
 def valid(self):return {'purpose':'DIRECT_BUYER','admissibility':'ADMISSIBLE','environment':'LIVE','is_provisional':False,'account_identity':'a','actor_identity':'b','counterparty_role':'BUYER','interaction_type':'MEETING','occurred_at':'2026-08-25T00:00:00Z','channel':'meet','receipt_ref':'r'}
 def test_g3_positive(self):self.assertTrue(policy.direct_g3_admissible(self.valid())[0])
 def test_each_tuple_field_required(self):
  for f in policy.DIRECT_FIELDS:
   d=self.valid();d[f]=None;self.assertFalse(policy.direct_g3_admissible(d)[0],f)
 def test_nonlive_rejected(self):
  d=self.valid();d['environment']='TEST';self.assertFalse(policy.direct_g3_admissible(d)[0])
if __name__=='__main__':unittest.main()
