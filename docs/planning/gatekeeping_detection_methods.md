# Detection Methods: Gatekeeping & Non-Genuine Content

This document outlines the heuristic and AI-driven rules for detecting administrative gatekeeping and non-genuine contributions (Vandalism, Spam, Sarcasm) on WikiHow.

## 🛡️ Administrative Gatekeeping Detection

| Rule | Detection Signal | Analysis |
| :--- | :--- | :--- |
| **Nuclear Revert** | Admin/Booster reverts a structured edit (templates/images) to a Bot version without a manual summary. | Indicates "Trust-based" rejection of valid content. |
| **Scope Policing** | Summary contains: `not the place`, `not wikiHow style`, `unneeded`, `unnecessary`. | Subjective removal of genuine information based on stylistic preference. |
| **Edit Looping** | 3+ alternating reverts between an Admin and a User on the same article. | A "Wall of Authority" preventing a user's perspective from persisting. |
| **Tone Rejection** | Talk page mentions `sarcastic` or `immature` preceding a `delete` or `revert` action. | Suppression of diverse or informal voices (the "Professionalization" of WikiHow). |

---

## 🚫 Non-Genuine Contribution Detection

| Rule | Detection Signal | AI Judgment Prompt |
| :--- | :--- | :--- |
| **Obvious Vandalism** | High-density profanity or "Nonsense" strings in the diff. | "Is this edit designed solely to degrade the article's utility?" |
| **Commercial Spam** | Usernames with sales-oriented keywords (e.g., `deals`, `camiseta`). | "Does this edit introduce external promotional links?" |
| **Mockery/Sarcasm** | Edits that add cynical or "joke" advice to serious articles (e.g. Breakup advice). | "Is this advice medically sound/procedural, or is it cynical humor?" |

---

## 🔬 "Nuclear Gatekeeping" Case Study
**Example**: *How to Install Ubuntu Linux Without CD*
- **Action**: User `TechThatWorks` added a valid Video Template.
- **Gatekeep**: Booster `EpcotMagic` rolled it back to a version by `MiscBot` with ZERO explanation.
- **Classification**: **Nuclear Gatekeeping** (Rejected legitimate improvement).
