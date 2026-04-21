# 🎭 WikiHow Research: The "Hall of Rejects" & Presentation Highlights

This document summarizes the qualitative and quantitative insights for the sociological research presentation on WikiHow's demographic and moderation dynamics.

---

## 🏷️ 1. Administrative Tags (The "Enforcement" Language)
In our analysis of over 11,800 edits, these tags define how contributors are policed:
- **`vand` (Vandalism)**: Purely destructive or nonsense edits (Keyboard mashing, blanking).
- **`RCP` (Recent Changes Patrol)**: High-velocity rollback by power-users.
- **`NAB` (New Article Booster)**: Gatekeeping for newly created instructional content.
- **`ce` / `copyedit`**: Fixing surface-level grammar/spelling.
- **`NPOV` (Neutral Point of View)**: Often used to "scrub" gendered nuance or subjective advice in favor of a "Systemic Neutral" tone.

---

## 🏅 2. User Authority Badges (The Hierarchy)
The social stratification of WikiHow is visually indicated by badges that denote gatekeeping power:
- ![Admin](https://www.wikihow.com/skins/WikiHow/images/admin.png) **ADMIN**: Final word on reverts; extreme gatekeeping authority.
- ![Staff](https://www.wikihow.com/skins/WikiHow/images/staff.png) **STAFF**: Corporate oversight of sitewide policy.
- ![Specialist](https://www.wikihow.com/skins/WikiHow/images/expert-badge.png) **SPECIALIST**: Content experts validating "Professional" (Rank 9) continuums.
- ![Featured](https://www.wikihow.com/skins/WikiHow/images/featured.png) **FEATURED**: Veteran contributors with high "Loudness" scores.
- ![Booster](https://www.wikihow.com/skins/WikiHow/images/booster.png) **BOOSTER**: Community supporters policed by Admins but polling the public.

---

## 😂 3. The Rejection List: Hilarious & Notable Failures
These actual article titles were rejected by the system for being "Noise" (Mischief, Gimmick, or Dangerous):

| Article Title | Rejection Category | Research Punchline |
| :--- | :--- | :--- |
| **How to Bake Cookies on Your Car Dashboard** | Mischief / Gimmick | "Skill transition from kitchen to global warming." |
| **How to Get Rid of Ghosts in Your House** | Paranormal Noise | Interfered with domestic wiring / technical safety. |
| **What Emojis Mean Sex?** | Social Noise | Subjective lexicon vs. functional home management. |
| **How to Make an Electromagnetic Pulse** | Dangerous / Weapon | High-risk doomsday prep vs. electrical hobbyist. |
| **How to Run Away From Home** | Mischief Noise | The ultimate "Anti-Domestic" article. |
| **Which Camp Half-Blood Cabin Am I In?** | Fandom Noise | Fantasy home-building vs. actual carpentry. |

**Full List available in:** [hilarious_rejections.csv](file:///f:/Users/Admin/Documents/WikiHow%20Project/research_taxonomy/hilarious_rejections.csv)

---

## 🧬 4. Name Guessing Difficulty: Why GenAI is Smarter
We initially used `Genderize.io` + `regex` for identity attribution, but hit a biological/technical wall:
- **Easy Cases**: `Mary`, `David`, `Sarah` (Straightforward API hits).
- **Hard Cases (Technical Noise)**: `AndrejG_22`, `MichaelAbrams_01`, `User_⭐`. The API fails on underscores and special characters.
- **Hard Cases (Ambiguous)**: `User:CelesteTu` or `User:Ciccioblues`.
- **The GenAI Solution**: Our pipeline (DeepSeek Vision) doesn't just look at the word. It reads the **Profile Bio** ("Mother of three", "Avid woodworker", "Trans rights advocate"). It understands the *cultural* context of the name "Ciccio" (Italian masculine) and uses image metadata to resolve identities that the API rejects as "Unknown".

---

## ⚔️ 5. Reversion Dynamics: "The Gatekeeping Wall"
- **How we know it was reverted**: We scan the historical log for a "Revert Signature": `(revert|undo|rollback|undid|RCP)`.
- **Identifying "Genuine" Reversions**: We pipe the deleted content through the **Detoxify (RoBERTa)** model. If a helpful, non-toxic edit (e.g., neutralizing "He" to "They") was rolled back, we classify it as **Ideological Gatekeeping**.
- **The Theoretical Foundation**: Our study is grounded in the **"Authority Continuum"**.
    - **Hargittai & Shaw (2015)**: The digital mirror of offline gender roles.
    - **Bolukbasi et al. (2016)**: Gender-neutrality mapping through word embeddings.

---

## 🔄 6. Contribution Shifts: "Drifting Across Domains"
We track how users move from traditionally "Feminine" clusters to "Masculine" ones (or vice-versa).

| Username | Shift History | Key Article Migration |
| :--- | :--- | :--- |
| **WRM** | Feminine → Masculine → Feminine | Drifted from `electrical_wiring` to `baby_care`. |
| **Eric** | Masculine → Feminine | From `electrical_wiring` (Tech) to `clothing/health`. |
| **Intern** | High-Tech → Domestic Core | Heavy migration from `Interior Decorating` to `Baking`. |

---

## 📊 7. Non-Genuine Categories (Categorical Filters)
- **`VANDALISM`**: Pure destruction / nonsense.
- **`SPAM_PROMOTIONAL`**: Sales/Ad noise.
- **`NON_GENUINE_SARCASM`**: Cynical or parody advice.
- **`MAINTENANCE_GATEKEEPING`**: Reverting good content over minor "Styles" rules.
- **`GENDER_GATEKEEPING`**: Erasure of gendered nuance or non-binary markers.
