# FIXTURE-DAI-001 — Synthetic Stakeholder Interviews

All names, statements and events are fictional.

## CLIENT-SRC-001 — CEO interview

**Date:** 2026-07-02  
**Participants:** Daniel Lim, CEO; offdata engagement lead

**Q: What decision do you need to make?**  
We need to decide whether AI is worth a serious first investment and which area will show value quickly. I do not want another technology experiment that looks impressive but does not improve the business. I would like one visible pilot within six months.

**Q: Where do you see the largest opportunity?**  
Customer service feels obvious. Almost half the questions are repetitive. A customer-facing chatbot could answer order-status and product questions at any time. Our salespeople also complain about quotation administration. I suspect there is enough work across both areas to remove several positions eventually, though we have not made a workforce plan.

**Q: What constraints matter?**  
We can spend up to SGD 120,000 on the first stage. The ERP is not being replaced. We cannot put customer pricing, contracts or drawings into public AI systems. We also cannot reduce service availability while piloting. Any major workforce change comes back to me.

**Q: What would count as success?**  
A visible improvement in response speed, less administration and a credible financial return within twelve months. I would be disappointed if we only produce policies and training.

**Q: What concerns you?**  
Data leakage and incorrect technical advice. We sell components that must be compatible with a customer’s equipment. A wrong answer can cause delay, damage or a safety issue. At the same time, if every output requires five approvals, there is no point.

**Q: What evidence would change your current preference for a chatbot?**  
If the repeatable questions are not actually safe to answer automatically, or if our internal quotation process has a better measurable return and lower risk, I would reconsider.

**Interviewer observation:** The CEO has a strong preference for a visible AI initiative and speaks about future headcount reduction without an approved operating-model or workforce decision.

---

## CLIENT-SRC-002 — Sales and quotation workshop

**Date:** 2026-07-03  
**Participants:** Sales Director, two account managers, quotation coordinator, product specialist, finance business partner

### Sales Director

Our sellers spend at least half their time preparing quotes, finding old prices and chasing technical people. We should automate the entire quotation process. Competitors are replying faster.

### Account Manager A

Half is too high for me. I probably spend one day a week on quotes, but urgent or customised requests take over the day. The worst part is waiting for product compatibility confirmation. Drafting the email is not the bottleneck.

### Account Manager B

I reuse prior quotations. The problem is knowing whether the old price and discount are still valid. Customer-specific terms are in different folders. I would use an assistant if it showed the source and did not send anything automatically.

### Quotation Coordinator

The ERP creates a quote once we have the right item, quantity and price. We still re-key the enquiry from email or spreadsheet. About one in six quotes comes back because the item, quantity, unit, delivery term or discount authority was incomplete. Complex quotes wait for drawings or supplier confirmation.

### Product Specialist

Compatibility is not just text retrieval. Customers sometimes provide an incomplete part number or a photo. Similar-looking parts have different ratings. I could support an assistant that finds approved product documents and flags uncertainty. I would not approve automatic technical recommendations.

### Finance Business Partner

Discount authority is documented but not consistently embedded in the ERP. A model could suggest a price, but the final decision must remain with the delegated approver. We also need to separate time saved from actual cash savings.

### Workshop estimates

- Sales Director: 50 percent of seller time is quotation administration.
- Account Manager A: 20–25 percent on average, higher in project periods.
- Account Manager B: approximately 30 percent.
- Quotation Coordinator: 34 minutes median touch time, plus waiting.
- Product Specialist: 31 percent of quotations require specialist review, but complexity varies.

### Potential interventions raised

1. Extract enquiry details into a structured draft.
2. Retrieve current product and prior quotation evidence.
3. Flag missing information and approval needs.
4. Suggest compatible products.
5. Generate price and discount.
6. Send the quotation automatically.

### Workshop boundary agreed provisionally

Items 1–3 appear suitable for a bounded pilot. Items 4–6 require stronger data, control and delegated-authority design.

---

## CLIENT-SRC-003 — Customer service and technical support interviews

**Date:** 2026-07-04  
**Participants:** Customer Service Manager, two service agents, technical support engineer

### Customer Service Manager

We receive around 1,500 tickets each month. Order status, delivery dates, product documents and basic compatibility questions are common. First-contact resolution is 62 percent. A chatbot could reduce the queue, especially after hours.

### Service Agent A

Order status is repetitive when the ERP data is current. Delivery promises are more difficult because supplier dates change. Customers also ask us to explain why an order moved. A simple status answer can create more complaints if it lacks context.

### Service Agent B

Many tickets are duplicates because customers email the salesperson and service inbox. The ticket categories are not reliable. We often close a ticket under “general enquiry” because the right code is missing. The knowledge folder also contains old product sheets.

### Technical Support Engineer

Compatibility questions range from exact part-number confirmation to application engineering. The first type could be supported by approved product data. The second needs technical judgement and sometimes a site visit. The current ticket field does not distinguish them.

### Control concerns

- An external assistant must not expose another customer’s order or price.
- Product documents require version control.
- Technical uncertainty must route to a specialist.
- The company should not promise a delivery date solely from a probabilistic output.
- Human agents need to see sources and be able to correct the knowledge base.

### Interview conclusion

An internal knowledge assistant for human service agents may be viable earlier than a fully autonomous customer-facing chatbot. The ticket dataset requires recoding or sampling before estimating addressable volume.

---

## CLIENT-SRC-004 — Operations, IT and information security interviews

**Date:** 2026-07-05  
**Participants:** Operations Director, Warehouse Manager, IT Manager, outsourced security adviser

### Operations Director

Inventory is our largest balance-sheet concern. We hold SGD 8.4 million, including more than SGD 1 million of slow-moving items, yet still miss lines. The ERP vendor demonstrated an AI forecast module and said it can be activated quickly. I think this should be the first pilot because the value is tangible.

### Warehouse Manager

The history is messy. Project orders distort demand. Customers substitute items. Some lost sales are not recorded because a salesperson offers an alternative. Lead times change by supplier. A forecast can look accurate overall and still miss critical items.

### IT Manager

The ERP has limited APIs. We can export reports and use a controlled integration account, but real-time write-back would require vendor work. Product data has duplicates and incomplete attributes. Customer-specific prices are partly in ERP tables and partly in spreadsheets. We have Microsoft 365 but no approved enterprise generative-AI environment.

### Outsourced Security Adviser

The information-security policy predates generative AI. Access control is basic and shared mailboxes are common. We have no inventory of prompts or data sent to public AI tools. A recent informal check found employees using free AI services for email drafting and document summarisation.

### Security boundaries proposed

- Enterprise identity and named accounts.
- No public-model use with customer, pricing, contract, employee or drawing data.
- Approved data sources and retrieval boundaries.
- Logging of user, source and generated output.
- Human approval before external transmission.
- Vendor data-use and retention review.
- Incident and kill-switch process.

### Interview conclusion

The inventory opportunity may be valuable but is not pilot-ready without data remediation and a controlled back-test. Current unapproved AI use is a present risk requiring an immediate governance baseline regardless of selected pilot.

---

## CLIENT-SRC-005 — Finance, HR and workforce interviews

**Date:** 2026-07-06  
**Participants:** CFO, HR Manager, Sales Operations Manager, employee representative

### CFO

A pilot must have a credible twelve-month return. The initial business case assumes four full-time-equivalent positions of capacity at roughly SGD 210,000 annually, plus a possible gross-margin improvement from faster quotation response. If we spend SGD 88,000 and capture SGD 355,000 of value, the case is attractive.

### Interviewer challenge

Are the four positions expected to be removed or avoided?

### CFO

Not currently. Demand is growing and the teams say they are overloaded. We might avoid future hiring or redeploy capacity. I accept that this is not the same as immediate cash saving, but the board will expect a financial number.

### HR Manager

The workforce survey shows strong interest in training but low confidence in reviewing AI output. Twenty-two percent report using public AI tools for work. Managers have started talking about headcount reduction without a defined plan, which is creating concern. We need transparent role and training design.

### Sales Operations Manager

If quotation time is reduced, sellers might spend more time with customers. That only creates financial value if activity and conversion actually improve. We should measure capacity use, not assume it.

### Employee Representative

People are willing to learn, but they want clarity on monitoring, performance assessment and job impact. Some staff believe AI mistakes will become their responsibility even when they do not understand the system.

### Workforce conditions proposed

- State the pilot as augmentation and learning, not a predetermined reduction programme.
- Define which decisions remain human.
- Train users to verify sources and escalate uncertainty.
- Measure correction effort and workload transfer.
- Do not use pilot telemetry for individual performance action without a separate policy and consultation.

### Interview conclusion

The financial case must separate cash, cost avoidance, released capacity and incremental margin. Workforce communication and capability are material conditions of pilot success.