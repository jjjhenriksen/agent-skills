# Hosting and gifts — review release 0.1.0

## What was authored
Six standalone AgentSkills with task-specific references/templates, four read-only Python 3.11+ helpers and fictional runnable examples. Each folder has its own SKILL.md and MIT license. No cross-skill file dependency, personal records, hardcoded account, credentials, paid API, background task or UI-theme coupling.

- Google Sheets is the default shared potluck tool; explicit ranges, literal text writes, separate private file, re-read before/after write. It is NOT an exclusive-reservation database.
- SignUpGenius stays an optional manual packet/export adapter. Its current terms prohibit automated site use. Browser automation is conditional on provider permission, not shipped as tested functionality.
- Menu arithmetic keeps mass/volume and preparations separate, subtracts reservations, surfaces unknown quantities and reports exclusive-resource conflicts. It does not optimize schedules, validate cooking or certify allergy safety.
- Gift accounting distinguishes paid, remaining commitment, uncommitted estimate and RECEIVED refunds. Neither a gift idea nor a price link is checkout authority.
- Reminder gate suppresses stale/inactive/completed/already-sent/early/expired tasks. It is not a scheduler, delivery guarantee or distributed lock.
- Ordinary hosting language; no assumed disability, stamina assessment, mandatory rest plan or 'capacity management' service. Practical requirements are handled when relevant to the request.

## Research checked 2026-11-10
Each skill carries the relevant source subset in references/sources.md.

| Source | Decision it informs |
|---|---|
| https://www.signupgenius.com/how-to-use/potluck | Free contribution slots, quantities, email reminders; plan-specific extras |
| https://www.signupgenius.com/terms-of-service | Gate automated browser use; no claimed exception |
| https://developers.google.com/workspace/sheets/api/guides/values | Explicit ranges and values; no formulas from untrusted guest text |
| https://developers.google.com/workspace/sheets/api/guides/batchupdate | Atomic batches aren't concurrent claim locking |
| https://www.foodsafety.gov/blog/food-safety-tips-holidays | Holding/refrigeration and thermometer checks |
| https://www.foodsafety.gov/food-safety-charts/cold-food-storage-charts | Food-specific storage windows |
| https://www.fsis.usda.gov/food-safety/safe-food-handling-and-preparation/food-safety-basics/leftovers-and-food-safety | Rapid cooling and leftovers |
| https://www.foodallergy.org/resources/avoiding-cross-contact | Tiny transferred allergen quantities matter |
| https://consumer.ftc.gov/articles/online-shopping | Full costs, seller policies and purchase records |
| https://www.access-board.gov/ada/guides/chapter-4-accessible-routes/ | Verify actual arrival/venue routes when relevant; not private-home compliance certification |
| https://docs.openclaw.ai/automation/cron-jobs/schedules.md | One-shot/timezone/quiet-hour behavior |
| https://docs.openclaw.ai/clawhub/skill-format.md | Independently published folder format |
| https://docs.openclaw.ai/tools/clawhub.md | Folder-based skill publication after review |

W3C presentation guide returned 403, two stale FTC paths and an Apps Script lock-guide path returned 404; not relied upon. No contact form, gated resource, mailing-list signup or provider integration was enabled.

## Checks and honest limits
Reproduce from this repository:

```sh
python3 scripts/check_bundles.py
python3 -m unittest discover -s tests -v
```

The repository's existing checker/tests need PyYAML==6.0.3 and markdown-it-py==3.0.0; runtime helpers have no third-party Python dependencies. The focused helper suite is tests/test_hosting_helpers.py.

Independent offline scenario review exercised dinner shopping/equipment, competing potluck claims, formula-like guest text, partial snapshots, gift cancellation/refunds and stale reminders. It found a partial-snapshot vacancy ambiguity; fixed by emitting open_units:null and a separately named upper bound, with regression coverage.

No real guest email, Google Sheet, SignUpGenius page, account, scheduler, checkout or ClawHub publication was created or mutated. Model behavior, host isolation, actual sharing permissions and authenticated provider integrations still need separate pilots. No automatic live scheduling or background processing ships in these skills.

## Release preparation, not publication
Each of the six folders is the ClawHub source unit. Review its files and tests, select the authenticated publisher and confirm slug availability. Current documented command (do NOT run before approval):

```sh
clawhub skill publish ./hosting-run-of-show --slug hosting-run-of-show --name "Hosting Run of Show" --version 0.1.0
```

Repeat with the corresponding folder/name only after owner approval. The installed CLI has no skill-publish dry-run flag; never call the publish command just to validate. Local .skill ZIP validation is not a registry/security-scan pass. Do not publish the repository root, private event records or local test environments. Registry ownership, final slugs and scan status remain unverified.

The celebration template may bundle exact reviewed copies now; after separate skill releases exist, an explicitly reviewed template release can pin their actual registry references. Don't invent unpublished package names or duplicate a bundled and external copy. Christmas themes may accompany the template as a separate appearance plugin with no behavior coupling.

## Executed verification receipt (2026-11-10)
- Six skills passed the installed skill-creator frontmatter validator and local packager.
- Six independent archives inspected: exact source bytes/file sets, no cache files, all local references confined to their own bundle.
- Full agent-skills test suite: 56 passed (48 new hosting-helper tests, 8 existing checks).
- Existing skill bundle identity/reference checker passed.
- Public-source path/token-marker checks and git diff whitespace checks passed.
- Independent offline forward-test review completed; identified vacancy ambiguity fixed and regression-tested.
- Authenticated provider workflows, installed agent discovery and registry scans remain unrun.
