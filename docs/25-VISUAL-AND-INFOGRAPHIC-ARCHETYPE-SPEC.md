# 25 — Visual and Infographic Archetype Specification

## Purpose

Define reusable consulting visual grammars that can be generated as editable PowerPoint shapes, SVG and interactive HTML from one semantic specification.

## Common visual contract

Every visual must define:

- `visual_id`
- governing assertion
- intended audience and decision
- archetype
- nodes, relationships and hierarchy
- labels and source references
- data bindings, if any
- emphasis and reading order
- accessibility text
- format-specific rendering rules
- editability requirement
- visual QA checks

A visual is not approved merely because it is attractive. It must make the intended relationship easier to understand and must not imply unsupported precision or causality.

## 1. Maturity or commitment curve

Use for staged progression, confidence, adoption or capability development.

Required elements:

- explicit horizontal and vertical meanings
- named stages with observable criteria
- transition conditions
- failure, plateau or regression paths where material
- current and target states only when supported

Avoid generic upward curves with undefined stages.

## 2. Radial framework

Use for an integrated system with a central proposition and related dimensions.

Required elements:

- central outcome or operating proposition
- non-overlapping dimensions
- optional nested layers with distinct semantics
- relationship indicators only where meaningful
- balanced label density

Do not use a wheel merely to decorate a list.

## 3. Layered stack or iceberg

Use for visible outcomes supported by deeper enabling layers.

Required elements:

- clear dependency direction
- layer names and boundary logic
- indication of which layers are visible or hidden
- risks created by weak lower layers

Do not imply that every item in a lower layer causes every upper-layer result.

## 4. Causal narrative

Use to explain a sequence from trigger through mechanism to outcome.

Required elements:

- trigger or changed condition
- intervening mechanisms
- affected actors or systems
- outcomes and consequences
- feedback loops, uncertainties and alternative pathways where material

Causal arrows require evidence or explicit hypothesis status.

## 5. Value-driver tree

Use to connect financial or operational outcomes to controllable drivers.

Required elements:

- named outcome and formula or relationship
- mutually interpretable branches
- units and periods
- controllable versus external drivers
- initiative bindings
- reconciliation to model outputs

## 6. Journey and service blueprint

Use for customer, employee or process experience across time.

Required elements:

- stages or episodes
- actor actions and needs
- touchpoints
- frontstage and backstage activity
- evidence, pain points and moments that matter
- operational ownership and metrics

## 7. Process and value-stream flow

Use for work, information, decision or material flow.

Required elements:

- start and terminal conditions
- actors or systems
- decisions and handoffs
- cycle and wait time where available
- control points, failure modes and rework
- demand and volume assumptions

## 8. Operating-model map

Use to show how strategy and demand are converted into outcomes.

Required elements may include:

- capabilities
- products and services
- value streams
- organisation and decision rights
- governance and controls
- workforce
- sourcing and footprint
- technology and data
- performance management

The selected elements must reflect the supported decision rather than a universal template.

## 9. Governance and decision-rights model

Use for accountability, forums, authorities and escalation.

Required elements:

- decision or decision class
- accountable owner
- contributors and consultees
- threshold or delegated authority
- information required
- forum or mechanism
- escalation and exception route

## 10. Roadmap and transformation waves

Use for sequencing commitments and releases.

Required elements:

- outcomes, not only activities
- workstreams and owners
- dependencies
- decision gates
- acceptance evidence
- critical milestones
- benefits and adoption points
- contingency or stop conditions

## 11. Portfolio matrix

Use to compare opportunities or initiatives on two or more explicit dimensions.

Required elements:

- defined axes and scales
- source and calculation for placement
- uncertainty where material
- decision rules for quadrants or bands
- no arbitrary precision

## 12. System architecture

Use for applications, services, data and external interfaces.

Required elements:

- trust and data boundaries
- authoritative systems
- flow direction
- protocols or interface types where relevant
- residency and security zones
- failure and approval points

## Render hierarchy

1. Generate a structured visual specification.
2. Validate semantic completeness.
3. Render SVG as the canonical visual representation.
4. Convert to editable PowerPoint shapes where practical.
5. Bind interactive behaviours in HTML without changing semantics.
6. Render to image for visual inspection.
7. Run overlap, clipping, contrast and text-size checks.

## Quality requirements

- concise assertion-led title
- one dominant reading order
- no illegible labels
- no unexplained icons
- consistent meaning for colour, line and shape
- accessible text alternative
- source note proportionate to the surface
- editable labels and data where practical
- visual version linked to story-map version
- no contradiction with narrative or model

## Initial visual test set

Create golden examples for:

1. AI adoption maturity curve
2. Enterprise AI operating-model wheel
3. AI technology and data layered stack
4. AI disruption causal narrative
5. Benefits driver tree
6. Customer journey and service blueprint
7. Target operating-model map
8. Transformation roadmap
9. Governance and decision-rights model
10. Opportunity portfolio matrix

Each golden example must render consistently to SVG, PPTX and HTML and pass screenshot comparison within approved tolerances.
