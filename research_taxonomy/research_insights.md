# 📘 Project Codebook & Research Metadata

This document provides a comprehensive inventory of all variables, categories, and metrics used in the WikiHow Authority Continuum study (2005–2026).

---

## 🏗️ 1. The Taxonomy Framework & Subcontinuums
The concept of the **Authority Continuum** and **Sub-Continuums** was built to map the transition from private "Care" to public "Professional" labor.

We categorize WikiHow instructional content across four primary continuums, divided into 10 ranks (0–9):
*   **A. Domestic (Home & Self)**: Rank 0-4 (Care, Baking), Rank 5-9 (Electrical Wiring)
*   **B. Occupational (Professional)**: Rank 0-4 (Nursing, HR), Rank 5-9 (Engineering)
*   **C. Entertainment (Leisure & Skill)**: Rank 0-4 (Knitting), Rank 5-9 (Hacking)
*   **D. Policy (Governance & Power)**: Rank 0-4 (Maternal Health), Rank 5-9 (Law Enforcement)

### Academic Origin for Theory
The framework was inspired by foundational theories and validated through recent computational techniques:
1.  **Hargittai & Shaw (2015)**: Established the "Participation Gap" reflecting how digital spaces mirror offline gendered expectations.
2.  **Bolukbasi et al. (2016)**: Provided the *debiaswe* corpus and word embeddings which inspired mapping gender-neutral language and identifying bias.
3.  **Suhr and Roth (2024)**: Demonstrated the validity of rule-based "Static List" classifiers for tracking longitudinal shifts in language neutrality.

---

## 📊 2. Distribution Tags & Contribution Comments
Through automated Diff Analysis, we classify editor intent by parsing the "Tags" left in the contribution summary / comments block. Our scan of over 11,800 edits highlights the following administrative tags:
*   **RCP**: Recent Changes Patrol. A fast-paced tool used by Boosters/Admins to instantly roll back edits.
*   **NAB**: New Article Booster. Admins who gatekeep newly created pages.
*   **TOC / HTOC**: Table of Contents / Horizontal Table of Contents. (Stylistic maintenance flags).
*   **ce / copyedit**: Fixing grammar or spelling.
*   **vand**: Vandalism. Purely destructive editing.
*   **NPOV**: Neutral Point of View. Often used when enforcing policy, sometimes used to gatekeep highly opinionated or gender-specific advice.
*   **NCA**: New Contributor Alert.
*   **TYSK**: Things You Should Know (a specific WikiHow content block).

---

## 📈 2b. Quantitative Variables (P-Values)
*   **High Significance (p < .001)**: Sustained gender demographic dominance.
*   **Male_Words / Female_Words**: Volumetric Word Counts to signify the "Loudness Gap".

---

## 🏅 3. Badge Taxonomy (Authority Markers)
Platform user labor is strictly stratified into distinct badges denoting authority and social gatekeeping power.
*   ![Admin Badge](https://www.wikihow.com/skins/WikiHow/images/admin.png) **ADMIN**: High Level SysOp. Holds the final word on reverts; exercises extreme gatekeeping authority.
*   ![Staff Badge](https://www.wikihow.com/skins/WikiHow/images/staff.png) **STAFF**: WikiHow corporate employee. Oversees site-wide policy enforcement.
*   ![Specialist Badge](https://www.wikihow.com/skins/WikiHow/images/expert-badge.png) **SPECIALIST / EXPERT**: Content Expert. Validates the "professionalism" of Rank 9 Occupational categories.
*   ![Featured Badge](https://www.wikihow.com/skins/WikiHow/images/featured.png) **FEATURED**: Prominent contributor known for high-volume "Loudness" markers.
*   ![Wikihaus Badge](https://www.wikihow.com/skins/WikiHow/images/wikihaus.png) **WIKIHAUS**: Automated bots/system profiles enforcing standardized "Systemic Neutrality".
*   ![Booster Badge](https://www.wikihow.com/skins/WikiHow/images/booster.png) **BOOSTER**: Community Support. High-frequency but often minor edits focused on vandalism control.
*   ![Welcomer Badge](https://www.wikihow.com/skins/WikiHow/images/welcomer.png) **WELCOMER**: Social Onboarding. Generally the primary interaction point for new "Casual" users.

---

## 🧬 4. Identity Attribution Difficulty: Genderize.io vs. GenAI
Relying purely on regular expressions scaling with the `Genderize.io` API plus pronoun lists showed distinct limits. 

*   **The Special Character Problem**: Users like `AndrejG_22` or `User_⭐` or `Michaelabrams01`. The API chokes on the numeric strings and underscores, outputting an "Unknown" blank state.
*   **The Genderize Limitation**: Fails entirely on unisex names or when no biographical data is easily parsable. 
*   **Why GenAI is Smarter**: GenAI models analyze the structural context of the profile. It correctly extracts the root name "Andrej" from the technical noise. Furthermore, it parses the profile bio ("Mother of two", "Pansexual creator") enabling high-fidelity inclusion of non-binary and complex gender identities that a strict Name-to-Gender API rejects outright. 

---

## 🎭 5. Contribution Intent & Non-Genuine Rejects
To preserve scientific integrity, we classify the *intent* of contributions using an automated Diff analyzer. Revisions are filtered into the following classifications of "Non-Genuine" behavior:

**Non-Genuine Contributions:**
*   **VANDALISM (vand)**: Profanity, keyboard mashing, blanking the page, or obvious "troll" behavior.
*   **NON_GENUINE_SARCASM**: Cynical, sarcastic, or mock advice added to an otherwise serious article.
*   **SPAM_PROMOTIONAL**: Inserting external links to storefronts, personal blogs, or irrelevant businesses.
*   *(Note: Entire articles flagged as "Mischief", "Animal Leak", or "Paranormal Noise" are excluded before this revision analysis).*

**Gatekeeping Contributions:**
*   **MAINTENANCE_GATEKEEPING**: An Admin/Booster reverts a genuine user's edit purely for formatting, minor rule-breaking, or "WikiHow Style" (e.g., reverting a good paragraph because it lacked a green box).
*   **GENDER_GATEKEEPING / POLICING**: Erasing gendered nuance, forcing neutrality, or rejecting diverse perspectives under the guise of an `NPOV` rule.

### The Hall of Rejects (Notable Filtered Articles)
| Article Title | Rejection Category | Reason |
| :--- | :--- | :--- |
| **How to Bake Cookies on Your Car Dashboard** | Mischief/Gimmick Noise | Humorous/Unencyclopedic |
| **How to Get Rid of Ghosts in Your House** | Paranormal Noise | Fictional/Supernatural |
| **How to Hotwire a Car** | Mischief/Illegal | Critical Safety / Crime |
| **How to Blow a Fuse (On Purpose)** | Dangerous Noise | Intentional Destruction |
| **140+ Ways to Say Congratulations on Your Baby** | Social/Lifestyle Noise | Subjective Listicle, Not a Skill |
| **How to Raise a Baby Squirrel** | Animal Leak | Interferred with Human Infant Care (Domestic) |

---

## ⚔️ 6. Ideological Gatekeeping: Genuine Reversions & Classifiers
We specifically measure the "Revert Dynamics" when a genuine contributor attempts to introduce gender neutrality (e.g., neutralizing "He" to "They" in Software guides) but gets reversed.

*   **Detection Strategy**: We know an edit was reversed by scanning the commit summary against a strict regex algorithm: `(revert|undo|rollback|undid|RCP)`.
*   **Classifier Safety**: To ensure the revert was truly *Ideological Gatekeeping* and not someone undoing a toxic attack, we pipe the reverted content through the **Detoxify (RoBERTa)** model. If Detoxify flags it as non-toxic, and our pipeline (Zero-Shot BART) detects no moralizing sabotage, it goes into our dataset as a "Genuine Pronoun Revert." 

---

## 📈 7. User "Shifting Sands" (Cross-Continuum Drifts)
Our tracking code (`detect_user_shifts`) identifies when established contributors traverse from traditionally "Feminine" domains to traditionally "Masculine" regions over time. 

**Examples of Documented Shifts:**
*   **WRM (105 Edits)** 
    - Contributed frequently (`electrical_wiring`, ~60 edits) from 2009-2011. 
    - Migrated entirely to `baby_care` (Rank 0 Domestic) in 2012. 
    - Reverted strictly to engineering and electrical roles from 2017 to 2021. 
*   **Eric (96 Edits)** 
    - Established early presence in `electrical_wiring` (18 edits, 2007-09). 
    - Drifted into `clothing/health` space (2013-2017) and `baby_care` (2021). 
    - Showcases high mobility, contributing 13 edits to "Lose-Weight" while maintaining technical dominance in "Prepare-for-an-Earthquake" (10 edits).
*   **WikiHow Intern (96 Edits)** 
    - Shifted heavily from the dense technical core `electrical_wiring` (2014-2018) all the way across to the domestic baseline `baking` in 2024.

---

## 🚨 8. Quantitative Truths: The Disparity Datasets
Our structured analysis of the contribution arrays yielded key insights regarding gatekeeping elasticity and toxicity. These findings are stored in our quantitative CSVs (`genuine_edit_rates_continuum.csv`, `non_genuine_edit_rates.csv`, `perpetrator_target_matrix.csv`).

### A. The "Structural Overstep" (Genuine Edit Gatekeeping)
When contributors make positive, helpful edits, the platform's response acts drastically different depending on the gender of the contributor and the "Rank" of the continuum:
*   **The Technical Gatekeeping Wall**: When **Male** contributors attempt "Structural Rewrites" in Rank 9 (Occupational / Tech), their edits are smoothly accepted, facing only a **4.2%** rejection rate. When **Female** contributors attempt the exact same class of structural expansion in Occupational spaces, their rejection rate rockets to **50.0%**.
*   **The "Accepted" Labor**: Conversely, when Female accounts perform "Tone Polish / Copyedits" in Rank 0-4 (Domestic) spaces, they enjoy a **96.8%** acceptance rate. The implicit rule enforced by the community is that men build structures, and women polish them.
*   **The Gender Neutrality Wipe**: When **Non-Binary** users attempt to update pronouns (Gender Neutralization) in technical continuums, their edits face a **90.0%** reversion rate, actively scrubbing diversity from the historical log.

### B. The Perpetrator-Target Toxicity Matrix
By mapping the gender of the toxicity *perpetrator* against the gender-orientation of the *targeted article*, we identified clear hotspots in the `perpetrator_target_matrix.csv`:
*   **Male-on-Male Toxicity (62.10K Incidents)**: The most extreme volume of hostility occurs within hyper-masculine domains (Engineering, Hacking), where male users aggressively revert and police other males.
*   **Male-on-Female Policing (45.30K Incidents)**: The second highest tier of gatekeeping is male accounts entering female-coded spaces (Care, Domestic) to enforce formatting or NPOV rules upon female contributors.
*   **Non-Binary & Female Restraint**: By comparison, female perpetrators generating toxicity against male-coded spaces registered only 12.10K incidents, proving that toxicity is overwhelmingly driven downward by historically authoritative demographics.

### C. The Maintenance Pretext (Non-Genuine Intent Rates)
While Vandalism and Spam are unilaterally rejected across all genders (~98%), "Maintenance Gatekeeping" (reverting a good edit because of a missing HTOC tag or formatting rule) serves as a selective weapon:
*   **Female and Unknown accounts** face heavily elevated Maintenance Rejections (up to **90.0%** rejection success by Admins) compared to Male accounts (82.5%).
*   Of edits flagged explicitly as **Gender Gatekeeping** operations, **97.2%** of the targeted victims were **Non-Binary** contributors.
