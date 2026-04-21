# WikiHow Contributor Data Schema

This document defines the structure of the contributor database for the WikiHow Analysis project. The data is organized into **yearly folders** (e.g., `Data/2008/contributors.csv`) based on the contributor's join year (tenure).

## Database Structure (CSV)

| Variable | Type | Description |
| :--- | :--- | :--- |
| `username` | String | The wikiHow username. Primary Key. |
| `profile_url` | String | Full URL to the user page. |
| `real_name` | String | Extracted real name (e.g., from header box). |
| `location` | String | Extracted location (e.g., "Dubai"). |
| `year` | Integer | The year the user joined wikiHow (derived from Tenure). |
| `tenure` | String | Raw tenure string from profile (e.g., "over 18 years!"). |
| `edit_count` | Integer | Total number of article edits. |
| `pronoun` | String | Extracted pronouns (she/her, he/him, they/them). |
| `gender` | String | Final inferred gender (male, female, non-binary, unknown). |
| `identity_tags` | String | comma-separated list of identities (e.g., "lesbian, pansexual"). |
| `gender_source` | String | The logic layer that made the decision (Pronoun, Name, Image, GenAI). |
| `gender_confidence`| Float | Confidence score (0.0 to 1.0). Target > 0.95. |
| `badges` | List | JSON/List of badges (ADMIN, BOOSTER, FEATURED, etc.). |
| `image_ai_guess` | String | Gender guess from local vision library. |
| `genai_raw_json` | JSON | Full response from GenAI for auditing. |

---

## Visualization Requirements

To achieve the proposed research goals, the following variables are mapped to visualizations:

### 1. Gatekeeping & Privilege Analysis
*   **Goal**: Analyze if tenure or gender correlates with administrative privileges.
*   **Variables**: `year`, `gender`, `badges` (check for ADMIN/WELCOMER).
*   **Metric**: Ratio of Admins by Year/Gender.

### 2. Gender Parity & Trends
*   **Goal**: Visualize the evolution of gender diversity over time.
*   **Variables**: `year`, `gender`, `identity_tags`.
*   **Metric**: Stacked bar chart of Gender/Identity per Join Year.

### 3. Contributor Impact
*   **Goal**: Compare activity levels across different demographics.
*   **Variables**: `edit_count`, `gender`, `tenure`.
*   **Metric**: Scatter plot of Edits vs. Years Active.

### 4. Identity Diversity
*   **Goal**: Document the presence of non-binary and specific identity markers.
*   **Variables**: `identity_tags`.
*   **Metric**: Word cloud or distribution of specific identity mentions.
