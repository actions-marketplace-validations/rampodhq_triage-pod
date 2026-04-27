# TriagePod — Full Product Specification

## 1. Document metadata

**Product name:** TriagePod
**Parent brand:** Rampod
**Category:** Developer workflow tool / GitHub-native issue triage assistant
**Primary deployment modes:** Open-source GitHub Action, self-hosted service, hosted SaaS
**Document type:** Golden product specification
**Document purpose:** Source of truth for product vision, scope, requirements, releases, and implementation guidance

---

# Part I — Product Information (Ideal State)

## 2. Product summary

### 2.1 One-line description

TriagePod is a GitHub-native issue triage assistant that helps maintainers and software teams keep their issue tracker clean, actionable, and high-signal.

### 2.2 Expanded description

TriagePod analyzes newly created and updated GitHub issues, detects likely duplicates, identifies missing issue information, suggests labels, recommends whether an issue belongs in GitHub Discussions instead of Issues, and helps maintainers route work faster with less manual effort.

The product is designed to reduce the hidden cost of issue triage:

* repeated duplicate reports
* incomplete bug reports
* support questions being posted as issues
* inconsistent labeling
* slow maintainer response
* poor prioritization
* rising issue backlog

### 2.3 Core value proposition

TriagePod saves maintainer time and improves issue quality by turning GitHub issue intake into a structured, semi-automated workflow.

### 2.4 Product philosophy

TriagePod is not an autonomous maintainer bot.
It is an **assistive workflow system**.

Its value must remain high even if AI is disabled.

AI can improve:

* duplicate matching
* summaries
* classification quality
* response drafting

But the product must still be useful with:

* rules
* templates
* similarity checks
* form-aware completeness checks
* deterministic routing logic

---

## 3. Problem statement

### 3.1 Primary problem

GitHub issue trackers often become noisy, inconsistent, and hard to manage as projects grow.

### 3.2 Common failure modes

Maintainers face recurring problems:

* duplicate issues for the same bug or request
* vague issues with missing reproduction details
* support and “how do I” questions being filed as bugs
* labels being applied inconsistently
* backlog growing faster than maintainers can triage
* valuable issues being buried in noise
* repeated manual review work

### 3.3 Why this matters

Poor issue hygiene causes:

* slower bug resolution
* frustrated users and contributors
* maintainer burnout
* lower project trust
* weaker roadmap visibility
* wasted engineering time

---

## 4. Product goals

## 4.1 Primary goals

* Reduce time spent on manual triage
* Improve issue quality at intake
* Reduce duplicate issue clutter
* Improve routing of support-style conversations
* Standardize labeling and initial classification
* Help maintainers act faster with better signal

## 4.2 Secondary goals

* Provide a professional first-touch experience for contributors
* Improve contributor education through guided follow-up
* Create a reusable triage layer across repos
* Support both open-source and private team workflows

## 4.3 Non-goals

TriagePod is not intended to be:

* a full project management platform
* a replacement for GitHub Issues or Projects
* a customer support CRM
* a fully autonomous bug resolution agent
* a code debugging tool
* a full analytics suite in v1

---

## 5. Target users

## 5.1 Primary personas

### Persona A — OSS Maintainer

* Maintains public repositories
* Has limited time
* Faces repeated support questions and duplicates
* Needs lightweight automation
* Values GitHub-native workflows

### Persona B — Small Devtools Team

* Works on SDKs, APIs, CLIs, libraries, starter kits
* Uses public or internal GitHub repos
* Wants consistent issue intake and faster triage
* Prefers low-friction setup

### Persona C — Indie SaaS Founder

* Manages public repo/community
* Wants issue tracker to stay clean
* Needs quick value from install
* Does not want enterprise-level tooling complexity

## 5.2 Secondary personas

### Persona D — Community / Developer Relations Lead

* Wants users guided to the right channels
* Wants repeated questions moved to docs or discussions

### Persona E — Engineering Manager

* Wants intake quality, signal, and prioritization consistency
* Interested in multi-repo governance later

---

## 6. User jobs to be done

When a new issue is opened, the user wants to:

* know if it is likely a duplicate
* know if it is missing important information
* know what kind of issue it is
* know what should happen next
* reduce unnecessary manual back-and-forth
* maintain a cleaner backlog

When a repo admin configures TriagePod, they want to:

* define project-specific triage rules
* enforce their preferred workflow
* avoid maintaining custom bots themselves
* keep behavior transparent and controllable

---

## 7. Product positioning

## 7.1 Positioning statement

TriagePod helps maintainers and small software teams reduce issue chaos by automating the first layer of GitHub issue triage: duplicates, missing information, labeling, and routing.

## 7.2 Category

GitHub issue workflow assistant

## 7.3 Product differentiation

TriagePod differs by being:

* GitHub-native
* installable with minimal effort
* useful without full AI dependence
* configurable per repo
* focused specifically on intake triage, not generic automation
* suited for OSS maintainers and small teams, not only large enterprises

---

## 8. Product principles

1. **GitHub-first**

   * The product should feel like a natural GitHub extension.

2. **Assist, don’t hijack**

   * TriagePod should recommend and guide before aggressively automating.

3. **Transparent logic**

   * Users should understand why a suggestion was made.

4. **Configurable**

   * Behavior must be adjustable by repo owners.

5. **Useful without AI**

   * Core value cannot depend entirely on LLM inference.

6. **Low-friction adoption**

   * Time to value should be under 15 minutes for basic setup.

7. **Professional contributor experience**

   * Comments and prompts should be helpful, not robotic or hostile.

---

## 9. Functional scope (ideal state)

By the ideal end-state, TriagePod supports the following capability areas.

## 9.1 Issue intake analysis

* Trigger on issue opened
* Trigger on issue edited
* Trigger on issue reopened
* Optional trigger on comment added
* Parse title, body, labels, metadata, templates, forms

## 9.2 Duplicate detection

* Compare new issue against recent open issues
* Compare against recently closed duplicate-marked issues
* Rank likely duplicates
* Provide confidence score
* Explain why issue is likely duplicate
* Suggest duplicate links in comment
* Optionally mark as duplicate after maintainer confirmation

## 9.3 Missing information detection

* Check required fields from config
* Check whether title quality is adequate
* Check whether reproduction steps are present
* Check whether expected vs actual result exists
* Check for version/environment details
* Check for logs/screenshots if relevant
* Detect placeholder or low-signal content
* Ask follow-up questions automatically

## 9.4 Issue classification

* Bug
* Feature request
* Documentation issue
* Support question
* Duplicate
* Enhancement
* Regression
* Needs-info
* Other custom repo-defined types

## 9.5 Label suggestion

* Suggest labels based on:

  * title/body
  * issue form fields
  * rules
  * file/package references if present
* Optional auto-apply labels
* Confidence threshold for auto-application
* Maintain audit trace of why labels were suggested

## 9.6 Discussions routing

* Detect support/question-style issues
* Recommend moving conversation to GitHub Discussions
* Suggest Discussion category where possible
* Post a polite routing comment
* Avoid routing if repo has Discussions disabled

GitHub Discussions is specifically designed for community questions and open-ended conversation, which makes this routing capability meaningful and aligned with existing platform behavior.

## 9.7 Triage summaries

* Summarize issue content
* Summarize long threads
* Generate maintainer-facing action summary
* Highlight next recommended action

## 9.8 Repo configuration

* Per-repo config via YAML
* Optional organization-level defaults
* Required fields configuration
* Label mappings
* Routing rules
* Duplicate similarity thresholds
* Comment templates
* Enabled/disabled feature flags

## 9.9 Maintainer controls

* Dry-run mode
* Suggest-only mode
* Auto-comment toggle
* Auto-label toggle
* Confidence thresholds
* Ignore lists for labels/users/repos/issues

## 9.10 Dashboard and history

* View triage actions by repo
* View duplicate suggestions made
* View needs-info rates
* View routing recommendations
* View issue quality trends
* View misclassification correction history

## 9.11 Multi-repo and org support

* Shared rules across repositories
* Repo-level overrides
* Org-wide issue quality reporting
* Central admin panel

## 9.12 Integration surface

* GitHub Action
* GitHub App / webhook-based service
* Hosted SaaS dashboard
* Self-hosted deployment
* Optional notifications to Slack/Discord/email later

## 9.13 AI-assisted features

* Better duplicate ranking
* Thread summarization
* Maintainer reply drafting
* Smart label suggestions
* Issue quality scoring
* Similar-issue explanation generation

---

## 10. User flows

## 10.1 New issue flow

1. User opens a GitHub issue
2. TriagePod is triggered
3. It retrieves issue content and repo config
4. It runs:

   * completeness checks
   * duplicate checks
   * classification
   * routing checks
5. It produces a triage result
6. Depending on config, it:

   * comments
   * applies labels
   * marks needs-info
   * suggests discussions route
7. Maintainer reviews and acts

## 10.2 Issue edited flow

1. Reporter updates issue after TriagePod comment
2. TriagePod re-runs
3. Missing-info status is re-evaluated
4. If resolved:

   * remove needs-info label optionally
   * post acknowledgment optionally
5. Issue becomes ready for maintainer attention

## 10.3 Maintainer review flow

1. Maintainer reads TriagePod output
2. Maintainer:

   * accepts label suggestions
   * confirms duplicate
   * chooses to reroute
   * ignores suggestion
3. System records whether recommendation was accepted
4. Data improves analytics and future tuning

## 10.4 Configuration flow

1. Maintainer installs TriagePod
2. Adds `triagepod.yml`
3. Chooses enabled features
4. Tests with dry-run
5. Enables live comments and/or labels
6. Monitors early outputs

---

## 11. Feature definitions

## 11.1 Duplicate detector

### Purpose

Reduce repeated issue noise.

### Inputs

* issue title
* issue body
* issue metadata
* candidate issue set

### Outputs

* top N similar issues
* confidence score
* rationale
* recommendation comment

### Acceptance criteria

* returns up to configured N candidates
* ignores excluded labels/issues
* respects time window and open/closed filters
* provides explainable output

## 11.2 Missing-info checker

### Purpose

Improve intake quality before maintainers spend time.

### Checks may include

* minimum description length
* template completeness
* presence of repro steps
* environment/version mention
* expected vs actual fields
* attachment/log indicators

### Outputs

* missing fields list
* status: complete / incomplete / uncertain
* follow-up comment template

## 11.3 Issue classifier

### Purpose

Provide first-pass categorization.

### Classification outputs

* bug
* feature
* docs
* support
* enhancement
* duplicate
* other

### Modes

* rule-based only
* rule + AI hybrid

## 11.4 Label engine

### Purpose

Apply consistent triage metadata.

### Capabilities

* suggest labels
* auto-apply allowed labels
* respect existing labels
* avoid conflicting labels
* custom mapping from class → labels

## 11.5 Discussion router

### Purpose

Move support load away from Issues when appropriate.

### Rules

* only active if Discussions enabled
* only suggest if configured
* do not automatically transfer unless explicitly supported later
* use polite tone
* provide reason for recommendation

## 11.6 Triage summaries

### Purpose

Make issue review faster.

### Outputs

* issue summary
* suspected category
* suspected severity
* next-step suggestion

## 11.7 Analytics

### Purpose

Help teams understand issue hygiene.

### Metrics

* duplicate rate
* needs-info rate
* average completion improvement after comment
* support-vs-bug mix
* label consistency
* time-to-triage trends

---

## 12. Configuration specification

## 12.1 Example conceptual config

```yaml
version: 1

features:
  duplicate_detection: true
  missing_info_check: true
  label_suggestions: true
  discussion_routing: true
  summaries: true

required_fields:
  - reproduction_steps
  - expected_behavior
  - actual_behavior
  - version
  - environment

labels:
  bug: ["bug"]
  feature: ["enhancement"]
  docs: ["documentation"]
  support: ["support"]
  needs_info: ["needs-info"]
  duplicate: ["duplicate"]

duplicate_detection:
  max_candidates: 3
  similarity_threshold: 0.78
  search_open_issues: true
  search_recent_closed: true
  lookback_days: 180

discussion_routing:
  enabled: true
  question_patterns:
    - "how do i"
    - "can someone help"
    - "question"
  category: "Q&A"

comments:
  tone: "friendly"
  include_confidence: true
  include_explanations: true

automation:
  auto_apply_labels: false
  auto_comment: true
  dry_run: false
```

## 12.2 Config requirements

* human-readable
* repo-local
* validated on startup
* sensible defaults
* schema versioning supported

---

## 13. Output design

## 13.1 Comment style requirements

Comments must be:

* short
* helpful
* professional
* specific
* non-judgmental
* easy to skim

## 13.2 Example tone

Bad:

* “Your issue is low quality.”

Good:

* “Thanks for opening this. A few details seem to be missing before maintainers can investigate effectively.”

## 13.3 Comment content sections

* greeting
* issue assessment
* missing info or duplicate candidates
* suggested next step
* optional note about Discussions

---

## 14. Deployment model

## 14.1 Open-source Action

* easiest adoption path
* best for public repos
* minimal setup
* free entry point

## 14.2 Self-hosted

* containerized service
* webhook/App mode
* useful for private repos and controlled environments

## 14.3 Hosted SaaS

* easiest premium experience
* org-level reporting
* richer configuration UI
* multi-repo support
* billing and authentication

---

## 15. Technical architecture (high-level)

## 15.1 Core components

* Event receiver
* GitHub API client
* Config loader/validator
* Triage engine
* Rule engine
* Similarity engine
* AI provider abstraction
* Comment/label action executor
* Persistence layer
* Admin/dashboard service

## 15.2 Triage engine stages

1. Ingest event
2. Load repo config
3. Fetch issue context
4. Run heuristics
5. Run duplicate retrieval
6. Run classification
7. Run routing analysis
8. Merge results
9. Execute configured actions
10. Persist history

## 15.3 Data persistence

Needed for:

* historical duplicate analysis
* accepted/rejected suggestion logging
* analytics
* dashboard insights
* cached embeddings or similarity features

## 15.4 AI abstraction

AI provider must be pluggable:

* OpenAI-compatible
* local model option later
* provider optional
* graceful fallback to rules-only mode

---

## 16. Security and privacy

## 16.1 Security goals

* minimum GitHub permissions
* secure secret handling
* auditability of actions taken
* no unsafe code execution from issue content

## 16.2 Privacy requirements

* users must know what issue content is processed
* hosted mode must disclose whether content is sent to third-party AI APIs
* self-hosted mode should support no-external-AI operation
* data retention should be configurable

## 16.3 Permission model

Principle of least privilege:

* read issues
* write issue comments
* optionally write labels
* no unnecessary repo/admin permissions

---

## 17. Success metrics

## 17.1 Product success metrics

* installs
* active repos
* weekly triage events processed
* repeat repo usage
* conversion from free to paid

## 17.2 Workflow impact metrics

* reduction in duplicate issue clutter
* reduction in maintainer triage time
* increase in complete first-time issue submissions
* better label consistency
* reduction in support questions filed as issues

## 17.3 Qualitative success signals

* “Saved us time”
* “Reduced back-and-forth”
* “Cleaner issue tracker”
* “Made contributors provide better reports”

---

## 18. Risks and mitigations

## 18.1 False duplicate suggestions

Risk:

* users lose trust

Mitigation:

* confidence thresholds
* suggest-only mode
* explainability
* easy ignore controls

## 18.2 Over-commenting / bot annoyance

Risk:

* contributors dislike experience

Mitigation:

* concise tone
* configurable verbosity
* dry-run
* rate limits

## 18.3 Misclassification of support vs bug

Risk:

* valid bugs routed away incorrectly

Mitigation:

* suggest rather than force
* conservative thresholds
* maintainer override

## 18.4 AI inconsistency

Risk:

* inconsistent outputs

Mitigation:

* rules-first architecture
* deterministic fallbacks
* provider abstraction
* confidence gating

---

# Part II — Versioned Release Plan

The versions below are intentionally cumulative.

* **v1** = strong installable MVP
* **v1.5** = production-ready expansion for serious users
* **v2** = full ideal-state product

By **v2**, all major features described in this spec are represented.

---

# v1 — MVP

## 19. v1 objective

Deliver a GitHub-native tool that creates immediate value on new issues with minimal setup.

## 19.1 v1 product definition

TriagePod v1 is a **GitHub Action** that runs on issue creation and provides:

* duplicate suggestions
* missing-info checks
* basic label suggestions
* Discussion-routing suggestions
* repo-level YAML configuration

## 19.2 v1 target users

* OSS maintainers
* indie developers
* small public repos
* teams wanting lightweight intake assistance

## 19.3 v1 included features

### A. GitHub Action runtime

* trigger on `issues.opened`
* configurable through workflow + YAML
* runs on public repositories first

### B. Repo config file

* `triagepod.yml`
* schema validation
* default config fallback

### C. Duplicate detection (basic)

* compare against open issues
* simple similarity ranking
* configurable candidate count
* suggest top candidates in comment

### D. Missing-info checker

* configurable required fields
* simple field/pattern presence checks
* comment on missing details

### E. Basic issue classification

* bug / feature / docs / support / other
* rules-first
* optional lightweight AI enhancement

### F. Label suggestions

* suggest labels in output
* optional auto-apply for safe labels
* respect config mapping

### G. Discussions routing suggestion

* detect question/support phrasing
* suggest using Discussions where enabled
* comment only, no hard transfer

### H. Friendly triage comment

* short and readable
* includes:

  * classification
  * duplicate candidates
  * missing info
  * next steps

### I. Dry-run mode

* log results without taking actions

### J. Basic docs and examples

* README
* setup guide
* sample configs
* screenshots / demo GIF

## 19.4 v1 excluded features

* dashboard
* org-wide support
* issue edited re-check
* historical analytics
* hosted SaaS
* Slack/Discord notifications
* advanced AI summarization
* multi-repo views
* maintainer feedback learning loop

## 19.5 v1 success criteria

* installs in real repos
* users can configure it in under 15 minutes
* duplicate suggestions are useful often enough to save time
* missing-info comments improve issue quality

---

# v1.5 — Production Expansion

## 20. v1.5 objective

Move from “useful experiment” to “serious daily tool” for maintainers and small teams.

## 20.1 v1.5 product definition

TriagePod v1.5 expands the Action into a more reliable workflow assistant with improved event coverage, better precision, historical context, and a basic service layer.

## 20.2 v1.5 included features

### A. Additional event support

* trigger on `issues.edited`
* trigger on `issues.reopened`
* optional trigger on relevant comments

### B. Improved duplicate detection

* include recently closed issues
* configurable lookback window
* better ranking logic
* confidence score display
* reason snippets for duplicate suggestions

### C. Improved completeness analysis

* detect weak placeholders like:

  * “not working”
  * “help pls”
* check quality of title
* deeper template completeness checks

### D. Better label engine

* conflict prevention
* label priority rules
* optional auto-label thresholding
* custom project-specific mappings

### E. AI-assisted summaries

* short maintainer summary
* action-oriented issue synopsis
* optional thread summary on updates

### F. Issue quality scoring

* basic score such as:

  * complete
  * incomplete
  * low-signal
  * high-confidence bug
* exposed in comment or metadata

### G. Maintainer feedback controls

* mark suggestion useful / not useful
* internal logging of accepted/rejected actions
* groundwork for model/rule tuning

### H. Basic persistence layer

* store triage results
* store event history
* store duplicate candidate outcomes

### I. Self-hosted mode (basic)

* containerized service option
* webhook/App mode for private repos
* external AI optional

### J. Enhanced docs and onboarding

* troubleshooting docs
* best practices by repo type
* templates for:

  * libraries
  * SDKs
  * apps
  * CLIs

## 20.3 v1.5 excluded features

* polished hosted SaaS
* org-level dashboards
* cross-repo analytics
* multi-tenant admin UI
* enterprise security controls
* team collaboration dashboard

## 20.4 v1.5 success criteria

* teams can use TriagePod continuously without frequent tuning
* duplicate and needs-info accuracy improves over v1
* self-hosted adopters can run it with private repos
* maintainers trust output more due to better explanations

---

# v2 — Full Product

## 21. v2 objective

Deliver the full ideal-state TriagePod platform: GitHub-native triage automation plus visibility, governance, analytics, and premium deployment options.

## 21.1 v2 product definition

TriagePod v2 is a full issue-triage platform available as:

* open-source Action
* self-hosted service
* hosted SaaS

It supports individual repos, teams, and organizations with advanced triage intelligence and control.

## 21.2 v2 included features

### A. Full event coverage

* issue opened
* issue edited
* issue reopened
* selected comment-driven re-evaluation
* optional periodic re-triage jobs

### B. Advanced duplicate intelligence

* open + closed issue candidate search
* cross-repo candidate search in org mode
* explainable similarity reasons
* configurable confidence bands
* optional maintainer-confirmed duplicate workflow

### C. Full issue completeness framework

* template-aware analysis
* repo-type-specific completeness rules
* quality scoring
* dynamic follow-up suggestions

### D. Advanced classification and routing

* fine-grained issue types
* custom classes
* support vs bug vs docs vs feature confidence
* Discussions routing with category suggestion
* optional routing workflows depending on repo config

### E. Full label orchestration

* rules + AI hybrid
* auto-label based on confidence
* repo defaults + org defaults
* conflict and precedence engine

### F. Full summarization layer

* issue summary
* thread summary
* maintainer handoff summary
* “recommended next action” summary

### G. Dashboard and analytics

* per-repo dashboard
* org-level dashboard
* issue quality trends
* duplicate trends
* routing trends
* label application stats
* suggestion acceptance rates

### H. Multi-repo / org mode

* centralized configuration policies
* repo inheritance
* repo-level overrides
* org health overview

### I. Hosted SaaS

* authentication
* billing
* repo connection flow
* analytics UI
* settings UI
* event history
* premium AI features

### J. Self-hosted enterprise-ready mode

* no-external-AI mode
* configurable retention
* audit logs
* secure secrets handling
* container deployment docs

### K. Team workflows

* triage queue
* maintainer review panel
* feedback on suggestion quality
* saved views for:

  * duplicates
  * needs-info
  * support-like issues
  * regressions

### L. Monetization-ready premium layers

* private repo support
* advanced duplicate search
* org-level dashboards
* premium templates
* hosted automation
* support SLAs for paying users

## 21.3 v2 success criteria

* TriagePod is useful for both OSS maintainers and private team workflows
* it reduces triage overhead measurably
* hosted and self-hosted modes are production-credible
* the product has a clear free-to-paid upgrade path

---

# 22. Release mapping summary

| Capability               | v1                    | v1.5     | v2                 |
| ------------------------ | --------------------- | -------- | ------------------ |
| GitHub Action            | Yes                   | Yes      | Yes                |
| Repo YAML config         | Yes                   | Yes      | Yes                |
| New issue triage         | Yes                   | Yes      | Yes                |
| Duplicate detection      | Basic                 | Improved | Advanced           |
| Missing-info checks      | Basic                 | Improved | Full               |
| Label suggestions        | Basic                 | Improved | Advanced           |
| Discussions routing      | Basic suggestion      | Improved | Full routing logic |
| AI summaries             | No / minimal optional | Yes      | Advanced           |
| Issue quality scoring    | No                    | Yes      | Yes                |
| Edited/reopened support  | No                    | Yes      | Yes                |
| Persistence/history      | No                    | Basic    | Full               |
| Self-hosted mode         | No                    | Basic    | Full               |
| Dashboard                | No                    | No       | Yes                |
| Multi-repo/org support   | No                    | No       | Yes                |
| Hosted SaaS              | No                    | No       | Yes                |
| Maintainer feedback loop | No                    | Basic    | Full               |

---

# 23. Packaging and commercialization strategy

## 23.1 Free tier

* open-source GitHub Action
* public repo support
* basic triage

## 23.2 Gumroad / downloadable Pro

* advanced templates
* premium config packs
* self-hosted install bundle
* setup guides
* private-repo oriented deployment examples

## 23.3 Hosted SaaS

* easiest premium experience
* dashboards
* private repos
* org analytics
* premium AI features

GitHub’s Marketplace and Actions ecosystem give TriagePod a natural installation and discovery path, while Gumroad and software license tooling can support downloadable or self-hosted paid tiers.

---

# 24. Open questions for implementation phase

These are not product uncertainties; they are implementation decisions to finalize.

* Action only first, or Action plus minimal backend from day one?
* TypeScript vs Python for core engine?
* GitHub App support in v1.5 or v2?
* Hosted AI provider in early versions, or rules-only first?
* Free tier for public repos only, or public + low-volume private?
* When to introduce org-level pricing?
* Whether to support Discussions write-actions or keep it suggestion-only initially

---

# 25. Final product definition

TriagePod is a GitHub-native issue triage assistant that starts as a fast-install GitHub Action and grows into a configurable triage platform for maintainers and software teams. Its core promise is simple:

**less issue chaos, better issue quality, faster triage.**

And its release progression is equally clear:

* **v1** proves utility
* **v1.5** proves reliability
* **v2** delivers the full platform