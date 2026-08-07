# WS6.12 — Deliverable quality implementation specification

> [!CAUTION]
> **SPECIFIED, NOT IMPLEMENTED OR AUTHORISED.** This defines future renderer acceptance gates only.
> It does not render or issue a client artefact, activate runtime, authorize Codex, or satisfy implementation evidence.

## Purpose

WS6.12 extends the existing Phase 4 semantic model with implementation-ready renderer gates for PPTX, DOCX, XLSX, PDF, SVG and HTML.
The semantic model remains the source of truth; renderers may not change material semantics.

- Renderer surfaces: `6`.
- Mandatory dimensions per renderer: `5`.
- PCR-10 renderer requirements: `26`.
- Explicit surface bindings: `37`.
- Renderer acceptance cases: `30`.
- Cross-format OQ cases: `8`.
- Total planned cases: `38`.
- Registered/executable renderer tests: `0`.
- Satisfied implementation evidence: `0`.
- `codex_start_authorized=false`.

## Canonical path

The defect register suggested `docs/55-DELIVERABLE-QUALITY-IMPLEMENTATION-SPEC.md`, but `docs/55-WS6-3-CURRENT-STATUS-DOCUMENT-REPAIR.md` is immutable retained WS6.3 evidence.
This file is the canonical WS6.12 specification.

## Release-wide hard gates

- Automatic repair is forbidden; repaired or parser-recovered output blocks release.
- PPTX, DOCX and XLSX must open in an independent office consumer without repair/recovery warnings.
- PDF, SVG and HTML must parse/render without recovery or fatal resource/console errors.
- Material-region visual diffs have zero tolerance; global normalized raster difference is at most `0.005` with anti-alias channel delta at most `12`.
- Visual masks cannot cover text, material numbers, citations, decision labels or semantic visual labels.
- Clipped material text, off-canvas material objects, protected overlaps, missing fonts and missing assets each have zero tolerance.
- Material number agreement, citation resolution, semantic labels, contradiction retention and independent recalculation are 100%; unsupported material claims and unexplained hardcoded material numbers are zero.
- Baseline changes require review.

## PCR-10 requirement expansion

| Group | Requirement | Surfaces | Dimension |
|---|---|---|---|
| `pptx` | `opens_without_repair_warning` | `pptx` | `package_integrity` |
| `pptx` | `editable_shapes_and_charts` | `pptx` | `editability_structure` |
| `pptx` | `no_clipping_overlap_or_off_slide_content` | `pptx` | `visual_regression` |
| `pptx` | `readable_typography` | `pptx` | `accessibility` |
| `pptx` | `template_and_brand_compliance` | `pptx` | `visual_regression` |
| `pptx` | `citations_and_notes_preserved` | `pptx` | `semantic_reconciliation` |
| `pptx` | `visual_regression_passed` | `pptx` | `visual_regression` |
| `docx` | `opens_without_repair_warning` | `docx` | `package_integrity` |
| `docx` | `correct_heading_navigation` | `docx` | `accessibility` |
| `docx` | `controlled_pagination` | `docx` | `visual_regression` |
| `docx` | `no_orphaned_headings_or_broken_tables` | `docx` | `visual_regression` |
| `docx` | `accessible_structure_and_alt_text` | `docx` | `accessibility` |
| `docx` | `citation_consistency` | `docx` | `semantic_reconciliation` |
| `xlsx` | `formulas_remain_formulas` | `xlsx` | `editability_structure` |
| `xlsx` | `formula_and_reference_validation` | `xlsx` | `semantic_reconciliation` |
| `xlsx` | `input_assumption_output_separation` | `xlsx` | `editability_structure` |
| `xlsx` | `independent_recalculation` | `xlsx` | `semantic_reconciliation` |
| `xlsx` | `print_areas_and_named_ranges` | `xlsx` | `visual_regression` |
| `xlsx` | `reconciles_to_approved_deliverables` | `xlsx` | `semantic_reconciliation` |
| `pdf_svg_html` | `correct_rendering` | `pdf, svg, html` | `visual_regression` |
| `pdf_svg_html` | `selectable_text_where_appropriate` | `pdf, svg, html` | `editability_structure` |
| `pdf_svg_html` | `accessibility` | `pdf, svg, html` | `accessibility` |
| `pdf_svg_html` | `responsive_html` | `html` | `visual_regression` |
| `pdf_svg_html` | `print_safe_views` | `pdf, html` | `visual_regression` |
| `pdf_svg_html` | `no_missing_fonts_or_assets` | `pdf, svg, html` | `package_integrity` |
| `pdf_svg_html` | `material_consistency_with_office_outputs` | `pdf, svg, html` | `semantic_reconciliation` |

## Renderer contracts

### `PPTX`

- Implementation: `P7.2` / `COMP-DELIVERY`.
- Visual QA: `P7.5`.
- Integrity: `no_repair_warning`.
- Editability/structure: `native_editable`.
- Independent consumer: `independent_office_consumer`.

**Native structures**
- `text_boxes`
- `native_shapes`
- `editable_charts`
- `speaker_notes`
- `slide_titles`

**Accessibility**
- `slide_titles_present`
- `reading_order_defined`
- `informative_visuals_have_alt_text`
- `normal_text_contrast_at_least_4_5`
- `large_text_contrast_at_least_3_0`
- `no_color_only_meaning`

**Semantic reconciliation**
- `semantic_object_ids_preserved`
- `material_numbers_match_approved_model`
- `citations_and_notes_resolve`
- `recommendation_and_roadmap_ids_match`

**Visual regression**
- `zero_clipped_text`
- `zero_off_slide_material_objects`
- `zero_protected_overlap`
- `template_brand_tokens_match`
- `raster_baseline_within_tolerance`

| Planned case | Dimension | PCR-10 requirements | Evidence |
|---|---|---|---|
| `DQ-PPTX-PACKAGE-INTEGRITY-001` | `package_integrity` | opens_without_repair_warning | `pptx_package_integrity_report` |
| `DQ-PPTX-EDITABILITY-STRUCTURE-001` | `editability_structure` | editable_shapes_and_charts | `pptx_editability_structure_report` |
| `DQ-PPTX-ACCESSIBILITY-001` | `accessibility` | readable_typography | `pptx_accessibility_report` |
| `DQ-PPTX-SEMANTIC-RECONCILIATION-001` | `semantic_reconciliation` | citations_and_notes_preserved | `pptx_semantic_reconciliation_report` |
| `DQ-PPTX-VISUAL-REGRESSION-001` | `visual_regression` | no_clipping_overlap_or_off_slide_content, template_and_brand_compliance, visual_regression_passed | `pptx_visual_regression_report` |

### `DOCX`

- Implementation: `P7.3` / `COMP-DELIVERY`.
- Visual QA: `P7.5`.
- Integrity: `no_repair_warning`.
- Editability/structure: `native_editable`.
- Independent consumer: `independent_office_consumer`.

**Native structures**
- `paragraphs`
- `headings`
- `tables`
- `links`
- `editable_text`
- `vector_or_editable_visual_objects`

**Accessibility**
- `document_language_present`
- `heading_hierarchy_navigable`
- `table_headers_identified`
- `informative_visuals_have_alt_text`
- `normal_text_contrast_at_least_4_5`
- `no_color_only_meaning`

**Semantic reconciliation**
- `semantic_object_ids_preserved`
- `material_numbers_match_approved_model`
- `citation_consistency`
- `appendix_provenance_complete`

**Visual regression**
- `controlled_pagination`
- `zero_orphaned_headings`
- `zero_broken_tables`
- `zero_clipped_content`
- `raster_baseline_within_tolerance`

| Planned case | Dimension | PCR-10 requirements | Evidence |
|---|---|---|---|
| `DQ-DOCX-PACKAGE-INTEGRITY-001` | `package_integrity` | opens_without_repair_warning | `docx_package_integrity_report` |
| `DQ-DOCX-EDITABILITY-STRUCTURE-001` | `editability_structure` | WS6.12 cross-cutting requirement | `docx_editability_structure_report` |
| `DQ-DOCX-ACCESSIBILITY-001` | `accessibility` | correct_heading_navigation, accessible_structure_and_alt_text | `docx_accessibility_report` |
| `DQ-DOCX-SEMANTIC-RECONCILIATION-001` | `semantic_reconciliation` | citation_consistency | `docx_semantic_reconciliation_report` |
| `DQ-DOCX-VISUAL-REGRESSION-001` | `visual_regression` | controlled_pagination, no_orphaned_headings_or_broken_tables | `docx_visual_regression_report` |

### `XLSX`

- Implementation: `P7.3` / `COMP-DELIVERY`.
- Visual QA: `P7.5`.
- Integrity: `no_repair_warning`.
- Editability/structure: `formula_native_editable`.
- Independent consumer: `independent_spreadsheet_consumer`.

**Native structures**
- `formulas`
- `named_ranges`
- `tables`
- `charts`
- `print_areas`
- `source_assumption_calculation_output_check_separation`

**Accessibility**
- `meaningful_sheet_names`
- `table_headers_identified`
- `charts_have_alt_text_or_equivalent_summary`
- `inputs_not_color_only`
- `errors_have_text_equivalent`

**Semantic reconciliation**
- `formulas_remain_formulas`
- `formula_references_valid`
- `independent_recalculation_passes`
- `material_numbers_match_other_approved_surfaces`
- `source_register_complete`

**Visual regression**
- `print_areas_valid`
- `no_truncated_material_cells`
- `chart_labels_visible`
- `raster_baseline_within_tolerance`

| Planned case | Dimension | PCR-10 requirements | Evidence |
|---|---|---|---|
| `DQ-XLSX-PACKAGE-INTEGRITY-001` | `package_integrity` | WS6.12 cross-cutting requirement | `xlsx_package_integrity_report` |
| `DQ-XLSX-EDITABILITY-STRUCTURE-001` | `editability_structure` | formulas_remain_formulas, input_assumption_output_separation | `xlsx_editability_structure_report` |
| `DQ-XLSX-ACCESSIBILITY-001` | `accessibility` | WS6.12 cross-cutting requirement | `xlsx_accessibility_report` |
| `DQ-XLSX-SEMANTIC-RECONCILIATION-001` | `semantic_reconciliation` | formula_and_reference_validation, independent_recalculation, reconciles_to_approved_deliverables | `xlsx_semantic_reconciliation_report` |
| `DQ-XLSX-VISUAL-REGRESSION-001` | `visual_regression` | print_areas_and_named_ranges | `xlsx_visual_regression_report` |

### `PDF`

- Implementation: `P7.3` / `COMP-DELIVERY`.
- Visual QA: `P7.5`.
- Integrity: `no_parser_recovery`.
- Editability/structure: `fixed_derived_from_editable_source`.
- Independent consumer: `independent_pdf_parser`.

**Native structures**
- `selectable_text_where_semantically_text`
- `embedded_or_declared_fonts`
- `tagged_structure`
- `source_artifact_link`

**Accessibility**
- `document_language_present`
- `tagged_reading_order`
- `informative_visuals_have_alt_text`
- `normal_text_contrast_at_least_4_5`
- `no_color_only_meaning`

**Semantic reconciliation**
- `material_consistency_with_office_outputs`
- `material_numbers_match_approved_model`
- `citations_resolve`
- `semantic_story_version_matches`

**Visual regression**
- `correct_rendering`
- `print_safe`
- `zero_missing_fonts`
- `zero_missing_assets`
- `raster_baseline_within_tolerance`

| Planned case | Dimension | PCR-10 requirements | Evidence |
|---|---|---|---|
| `DQ-PDF-PACKAGE-INTEGRITY-001` | `package_integrity` | no_missing_fonts_or_assets | `pdf_package_integrity_report` |
| `DQ-PDF-EDITABILITY-STRUCTURE-001` | `editability_structure` | selectable_text_where_appropriate | `pdf_editability_structure_report` |
| `DQ-PDF-ACCESSIBILITY-001` | `accessibility` | accessibility | `pdf_accessibility_report` |
| `DQ-PDF-SEMANTIC-RECONCILIATION-001` | `semantic_reconciliation` | material_consistency_with_office_outputs | `pdf_semantic_reconciliation_report` |
| `DQ-PDF-VISUAL-REGRESSION-001` | `visual_regression` | correct_rendering, print_safe_views | `pdf_visual_regression_report` |

### `SVG`

- Implementation: `P7.4` / `COMP-DELIVERY`.
- Visual QA: `P7.5`.
- Integrity: `no_parser_recovery`.
- Editability/structure: `structured_vector_editable`.
- Independent consumer: `independent_xml_svg_parser`.

**Native structures**
- `vector_geometry`
- `text_elements_where_semantically_text`
- `viewbox`
- `title`
- `desc`

**Accessibility**
- `title_and_description_present`
- `meaningful_groups_identifiable`
- `text_not_unnecessarily_outlined`
- `contrast_rules_met`
- `no_color_only_meaning`

**Semantic reconciliation**
- `material_consistency_with_office_outputs`
- `semantic_visual_ids_preserved`
- `labels_and_numbers_match_approved_model`
- `source_version_matches`

**Visual regression**
- `correct_rendering`
- `zero_missing_fonts`
- `zero_missing_assets`
- `viewbox_contains_material_geometry`
- `raster_baseline_within_tolerance`

| Planned case | Dimension | PCR-10 requirements | Evidence |
|---|---|---|---|
| `DQ-SVG-PACKAGE-INTEGRITY-001` | `package_integrity` | no_missing_fonts_or_assets | `svg_package_integrity_report` |
| `DQ-SVG-EDITABILITY-STRUCTURE-001` | `editability_structure` | selectable_text_where_appropriate | `svg_editability_structure_report` |
| `DQ-SVG-ACCESSIBILITY-001` | `accessibility` | accessibility | `svg_accessibility_report` |
| `DQ-SVG-SEMANTIC-RECONCILIATION-001` | `semantic_reconciliation` | material_consistency_with_office_outputs | `svg_semantic_reconciliation_report` |
| `DQ-SVG-VISUAL-REGRESSION-001` | `visual_regression` | correct_rendering | `svg_visual_regression_report` |

### `HTML`

- Implementation: `P7.3` / `COMP-DELIVERY`.
- Visual QA: `P7.5`.
- Integrity: `no_parser_recovery`.
- Editability/structure: `semantic_dom_structured`.
- Independent consumer: `headless_browser_and_html_parser`.

**Native structures**
- `semantic_dom`
- `headings`
- `landmarks`
- `text_nodes`
- `accessible_svg_or_chart_components`
- `print_styles`

**Accessibility**
- `wcag_2_2_aa`
- `keyboard_navigation`
- `visible_focus`
- `semantic_landmarks`
- `informative_visuals_have_alt_text`
- `normal_text_contrast_at_least_4_5`
- `no_color_only_meaning`

**Semantic reconciliation**
- `material_consistency_with_office_outputs`
- `semantic_object_ids_preserved`
- `material_numbers_match_approved_model`
- `citations_resolve`
- `story_version_matches`

**Visual regression**
- `responsive_320px`
- `responsive_768px`
- `responsive_1440px`
- `print_safe`
- `zero_missing_fonts`
- `zero_missing_assets`
- `raster_baseline_within_tolerance`

| Planned case | Dimension | PCR-10 requirements | Evidence |
|---|---|---|---|
| `DQ-HTML-PACKAGE-INTEGRITY-001` | `package_integrity` | no_missing_fonts_or_assets | `html_package_integrity_report` |
| `DQ-HTML-EDITABILITY-STRUCTURE-001` | `editability_structure` | selectable_text_where_appropriate | `html_editability_structure_report` |
| `DQ-HTML-ACCESSIBILITY-001` | `accessibility` | accessibility | `html_accessibility_report` |
| `DQ-HTML-SEMANTIC-RECONCILIATION-001` | `semantic_reconciliation` | material_consistency_with_office_outputs | `html_semantic_reconciliation_report` |
| `DQ-HTML-VISUAL-REGRESSION-001` | `visual_regression` | correct_rendering, responsive_html, print_safe_views | `html_visual_regression_report` |

## Cross-format output-quality obligations

| Criterion | Owner | Evidence | Planned case |
|---|---|---|---|
| `OQ-CITE` | `IMP-P5` / `P5.4` / `COMP-KNOWLEDGE` | `citation_resolution_report` | `DQ-XFMT-OQ-CITE-001` |
| `OQ-CLAIM` | `IMP-P5` / `P5.4` / `COMP-QA` | `unsupported_claims_report` | `DQ-XFMT-OQ-CLAIM-001` |
| `OQ-LABEL` | `IMP-P7` / `P7.1` / `COMP-DELIVERY` | `semantic_label_coverage_report` | `DQ-XFMT-OQ-LABEL-001` |
| `OQ-CONTRA` | `IMP-P5` / `P5.3` / `COMP-KNOWLEDGE` | `contradicting_evidence_retention_report` | `DQ-XFMT-OQ-CONTRA-001` |
| `OQ-NUM` | `IMP-P6` / `P6.4` / `COMP-ANALYTICS` | `number_reconciliation_report` | `DQ-XFMT-OQ-NUM-001` |
| `OQ-HARD` | `IMP-P6` / `P6.4` / `COMP-ANALYTICS` | `hardcoded_number_scan_report` | `DQ-XFMT-OQ-HARD-001` |
| `OQ-RECALC` | `IMP-P6` / `P6.4` / `COMP-ANALYTICS` | `independent_recalculation_report` | `DQ-XFMT-OQ-RECALC-001` |
| `OQ-XFMT` | `IMP-P7` / `P7.5` / `COMP-QA` | `cross_format_reconciliation_report` | `DQ-XFMT-OQ-XFMT-001` |

## Evidence contract

Each future gate must retain the exact implementation commit, semantic-model digest, renderer/profile version, produced-artifact digest, independent consumer/parser result, accessibility report, reconciliation report and visual-regression report.
On failure, retain the original unmodified artifact and diagnostics; a repaired copy cannot replace the failing artifact as evidence.

## Completion boundary

WS6.12 closes only `WS6-QUALITY-004`. `WS6-QUALITY-005`, `WS6-CODEXPREP-002` and `WS6-BLOCK-006` remain open.
No renderer, visual-QA implementation or external deliverable release is claimed.

The next permitted chat-first work package is `WS6.13` after the governed predecessor sequence and exact hosted acceptance requirements are satisfied.

## Rollback

Close the WS6.12 pull request and delete only governance/ws612-deliverable-quality-implementation-specification.

Revert the WS6.12 specification package as one unit; preserve canonical semantic requirements and keep every authorization boundary false.
