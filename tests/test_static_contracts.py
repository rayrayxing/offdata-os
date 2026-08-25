import unittest,json
from pathlib import Path
R=Path(__file__).resolve().parents[1]
class StaticContracts(unittest.TestCase):
 def test_dashboard(self):
  m=json.loads((R/'.hermes/plugins/off-data-venture/dashboard/manifest.json').read_text());self.assertEqual(m['api'],'plugin_api.py');self.assertTrue((R/'.hermes/plugins/off-data-venture/dashboard/dist/index.js').exists())
 def test_cron(self):
  j=json.loads((R/'config/cron_jobs.final.json').read_text())['jobs'];names={x['name'] for x in j};self.assertIn('OFFDATA Frontier Scan',names);self.assertIn('OFFDATA Approval Chaser',names);self.assertEqual(len([x for x in j if x['name'].startswith('OFFDATA Brief')]),4)
 def test_external_guards(self):
  s=(R/'.hermes/plugins/off-data-venture/__init__.py').read_text();e=(R/'.hermes/plugins/off-data-venture/external_tools.py').read_text();self.assertIn('offdata_terminal_external_effect',s);self.assertIn('CONTACT_OPTED_OUT',e);self.assertIn('Idempotency-Key',e)
 def test_profiles_and_skills(self):
  p=json.loads((R/'manifests/profiles.final.json').read_text())['profiles'];s=json.loads((R/'manifests/skills.final.json').read_text())['skills'];self.assertGreaterEqual(len(p),46);self.assertGreaterEqual(len(s),40)
if __name__=='__main__':unittest.main()
