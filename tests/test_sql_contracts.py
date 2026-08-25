import unittest,re
from pathlib import Path
R=Path(__file__).resolve().parents[1];SQL='\n'.join(p.read_text() for p in sorted((R/'database/migrations').glob('*.sql')))
class SQLContracts(unittest.TestCase):
 def test_authoritative_entities(self):
  for t in ['od_operations','evidence_artifacts','gate_snapshots','action_authorizations','external_effects','journal_entries','journal_lines','payments','research_queries']:self.assertIn(t,SQL)
 def test_effect_uniqueness(self):self.assertRegex(SQL,r'external_effects\([\s\S]*?operation_id text NOT NULL UNIQUE')
 def test_migrations_versioned(self):self.assertIn("003_external_effects_and_guard_policies",SQL)
if __name__=='__main__':unittest.main()
