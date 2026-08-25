#!/usr/bin/env python3
steps=['package_selftest','preflight','pin_hermes','plugin_skill_security_review','create_shadow_profiles','gate_policy_import','owner_policy','business_identity','model_primary_fallback_qualification','real_last30days','postgres_migrations','authority_and_audit','kanban_boards','telegram_AAR','backups_restore','codex_certification','no_seed_trial']
for i,s in enumerate(steps,1): print(f'{i:02d}. {s}')
