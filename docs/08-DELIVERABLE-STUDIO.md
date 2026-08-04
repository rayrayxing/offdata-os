# 08 — Storyline, Infographics and Deliverable Studio

## 1. Objective

Create client-ready outputs with the analytical integrity of the canonical engagement record and the visual quality expected of a strong consulting team.

The system must not independently rewrite the story for each format. It must render approved content from one semantic source.

## 2. Canonical Engagement Semantic Model

The story model should contain:

- Engagement and deliverable purpose
- Audience and decision
- Governing thought
- Proposition hierarchy
- Section contracts
- Claim and evidence references
- Key numbers and model references
- Recommendations and implications
- Visual-archetype specifications
- Citation presentation mode
- Brand, accessibility and confidentiality rules

Released artefacts must reference immutable versions of the story model and underlying analyses.

## 3. Supported output formats

- PowerPoint (`.pptx`)
- Word (`.docx`)
- Excel (`.xlsx`)
- PDF
- SVG
- Interactive HTML
- Web dashboards
- Image exports for previews and approved reuse

## 4. PowerPoint requirements

- Native editable text and shapes where practical
- Assertion-led titles where appropriate
- Consistent grid, typography, spacing and hierarchy
- Speaker notes with fuller sources and caveats where useful
- Appendix source register when required
- Charts linked to approved data or models
- No clipped or overlapping objects
- No rasterised labelled diagrams when editability is required
- Correct reading order and contrast
- Documented template and renderer version

## 5. Word requirements

- Stable heading hierarchy
- Page and section control
- Tables that fit and repeat headers correctly
- Cross-references and contents where appropriate
- Citation and appendix modes
- Accessible document structure
- Consistency with the approved story and numbers

## 6. Excel requirements

Workbook design should separate:

- Read-me and model purpose
- Source data
- Assumptions
- Transformations and calculations
- Scenarios and sensitivities
- Outputs
- Checks and reconciliations

Requirements:

- Formulas rather than unexplained hard-coded values
- Units and currencies declared
- Input, formula and output conventions documented
- No broken links or repair warnings
- Calculation checks visible
- Material results reconcilable to reports and slides
- Missing data represented honestly

## 7. Interactive HTML requirements

- Responsive layout
- Progressive disclosure
- Accessible navigation and keyboard support
- Data and claim provenance available on demand
- Export or print views where useful
- No decorative motion that obscures decisions
- Visual pacing that supports the storyline

“Cinematic” means purposeful sequencing, contrast, progressive disclosure and focus—not gratuitous animation.

## 8. Infographic grammar

The initial visual library must support:

### Journey and progression

- Commitment curves
- Maturity curves
- Adoption journeys
- Stage-gate roadmaps
- Transformation waves
- Failure and exit paths

### Systems and architecture

- Layered stacks
- Icebergs
- Reference architectures
- Capability maps
- Data and technology flows
- Ecosystem maps

### Strategy and decision

- Value-driver trees
- Option trees
- Portfolio matrices
- Scenario cones
- Decision funnels
- Strategic choice cascades

### Operating and implementation

- Operating-model wheels
- Radial frameworks
- Process maps
- Customer journeys
- Governance models
- Organisation and network maps
- Initiative roadmaps
- Benefits maps

### Risk and causality

- Causal chains
- Bow ties
- Fault and event trees
- Control maps
- Risk pathways
- Theory-of-change and logic models

### Quantitative communication

- Waterfalls
- Bridges
- Cohort curves
- Sensitivity charts
- Distribution and uncertainty charts
- Sankey-style flows
- Unit-economics diagrams

## 9. Visual specification schema

```yaml
visual:
  id:
  archetype:
  decision_message:
  audience:
  entities:
  relationships:
  labels:
  data_references:
  emphasis:
  layout_constraints:
  editable_required:
  accessibility:
  source_note_mode:
  output_formats:
```

The semantic specification should be reviewed before rendering complex visuals.

## 10. Rendering approach

### Use native shapes or SVG for

- Labelled consulting frameworks
- Process diagrams
- Architecture diagrams
- Data-driven visuals
- Editable client artefacts

### Use generated raster imagery for

- Hero illustrations
- Conceptual metaphors
- Decorative backgrounds
- Non-labelled visual assets

Generated imagery must not introduce false facts, fake logos, misleading interfaces or unlicensed imitations of distinctive protected designs.

## 11. Citation presentation

Maintain two layers:

### Internal provenance

- Full source
- Exact location
- Retrieval date
- Claim relationship
- Limitations
- Reviewer state

### Client presentation

Use proportionate treatment:

- Discreet footnote on material external facts
- Fuller detail in notes or appendix
- Model source and assumption tabs
- General labels such as “Company data; regulator publications; offdata analysis” where sufficient

Do not turn every slide into an academic reference page. Do not remove traceability from the internal record.

## 12. Quality tests

### Content

- Governing thought is clear
- Every page has a decision purpose
- Assertions match evidence
- Alternatives and uncertainty are represented appropriately
- Recommendations connect to implementation

### Reconciliation

- Numbers match approved models
- Terms and dates are consistent
- Charts and tables use the same definitions
- PPTX, DOCX, XLSX and HTML do not diverge materially

### Visual

- No clipping or overlap
- Minimum readable font sizes
- Correct contrast
- Consistent alignment and whitespace
- Labels and legends are complete
- Reading order is logical
- Visual complexity is proportionate

### Technical

- Files open without repair
- Formulas calculate
- Links and references resolve
- SVG and images render
- PDF export matches source layout
- HTML works on target browsers and screen sizes

## 13. Founder review packet

Before release, present:

- Deliverable preview
- Executive summary
- Key recommendations
- Material assumptions and uncertainties
- Quality score and open defects
- Model reconciliation status
- Client-facing citation approach
- Exact release action requested
