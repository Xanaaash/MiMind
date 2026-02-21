# Professional Scale Library (T-806)

Updated: 2026-02-21

This registry adds six authority-backed scales with source references, use-case notes, scoring logic, and bilingual disclaimer text. The current implementation enables full submission/result flow for `WHO-5` and keeps the rest available as professional references pending full interactive rollout.

| Scale ID | Name | Item Count | Use Case | Scoring Logic | Interactive |
|---|---|---:|---|---|---|
| `who5` | WHO-5 Well-Being Index | 5 | Subjective well-being trend over past 2 weeks | 0-5 per item, total 0-25, multiply by 4 to get 0-100 | Yes |
| `isi7` | Insomnia Severity Index | 7 | Perceived insomnia severity and daytime impact | 0-4 per item, total 0-28 | No |
| `ucla3` | UCLA Loneliness Scale (3-item) | 3 | Rapid loneliness risk screening | 1-3 per item, total 3-9 | No |
| `swls5` | Satisfaction With Life Scale | 5 | Global life satisfaction tracking | 1-7 per item, total 5-35 | No |
| `rses10` | Rosenberg Self-Esteem Scale | 10 | Self-esteem baseline and trend check | 4-point items with reverse coding, total 10-40 | No |
| `auditc3` | AUDIT-C Alcohol Use Screen | 3 | Risky alcohol-use pattern screening | 0-4 per item, total 0-12 | No |

## Evidence Mapping

- WHO-5: Topp CW et al. (2015) systematic review.
- ISI-7: Bastien CH et al. (2001) validation study.
- UCLA-3: Hughes ME et al. (2004) short loneliness scale.
- SWLS: Diener E et al. original SWLS publication.
- RSES: Rosenberg M. (1965) foundational self-esteem scale text.
- AUDIT-C: Bush K et al. (1998) validation in primary care.

## Scope Boundary

- These scales support self-reflection and screening only.
- They do not provide medical diagnosis, medication guidance, or treatment plans.
- Risk-positive outputs still rely on existing safety triage rules.
