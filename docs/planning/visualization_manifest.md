# Master Visualizations Manifest

This is the comprehensive, master list of every single graph conceptualized and mapped out for the research pipeline. They are organized logically into the four major sections of the thesis, detailing exactly what type of graph each is and what sociological phenomenon it proves.

### **Section A: Demographics & User Lifecycles**
*Focus: Who the contributors are, when they joined, and when they quit.*

1. **Demographics by Cohort & Time (Multi-Line / Area Graph)**
   * **What it is:** Tracks the raw volume of Female, Male, and Unknown contributors over the years (2005–2024), broken down by the year they joined (their Cohort). 
   * **Purpose:** Proves the macro-trend of platform demographics and whether wikiHow relies on aging "super-users" or fresh influxes of new members.
2. **Active Time and Dormancy Decay (Stacked Bar Chart)**
   * **What it is:** The X-axis shows "Tenure Before Dormancy" (<1 Year, 1-3 Years, etc.), and the Y-axis shows the number of users dropping out, stacked by gender.
   * **Purpose:** Visualizes the "Churn Rate." Shows if female users abandon the platform significantly faster than male users.
3. **Regional Concentration Map (Geographic / Fuzzy Search Map)**
   * **What it is:** A spatial map plotting the self-reported or fuzzy-matched locations of users.
   * **Purpose:** Adds a layer of intersectionality, showing if "Male-Coded Occupational" contributors are clustered in specific global regions (like North America or South Asia).

### **Section B: The Task Continuums**
*Focus: The digital division of labor across the 40 task categories.*

4. **The Categorical Breakdown / Demographic Gradient (Faceted Grouped Bar Graph)**
   * **What it is:** Four separate graphs (Domestic, Occupational, Entertainment, Policy) showing the Male/Female ratio across the specific categories (e.g., from *Baby Care* [0] to *Electrical Wiring* [9]).
   * **Purpose:** The core proof of your thesis. Visually demonstrates whether online instructional labor perfectly mirrors offline gender roles.
5. **Longitudinal Continuum Trends (Multi-Line Facet Grid)**
   * **What it is:** Tracks the Male vs. Female contribution score within the four macro-continuums over the last 20 years.
   * **Purpose:** Answers the question: *Are the continuums becoming more equal over time, or are traditional gender lines hardening?*
6. **The "Reversal" Articles / Gender Flips (Timeline / Gantt Chart)**
   * **What it is:** A timeline tracking specific, highly contested articles (like *How to Wire a Plug*) that started with Male-dominated authorship but eventually flipped to Female-dominated authorship (or vice versa).
   * **Purpose:** Highlights the micro-level battlegrounds of the platform.

### **Section C: Gatekeeping, Vandalism & Toxicity**
*Focus: How structural power and harassment operate across gendered lines.*

7. **The Perpetrator-Target Matrix (Seaborn Heatmap)**
   * **What it is:** A color-coded matrix crossing the *Gender of the Vandal* against the *Orientation of the Target Article*.
   * **Purpose:** The "Who is attacking What" graph. Proves if toxicity is strictly intra-gender (M in M) or if it crosses boundaries (M in F).
8. **Vandalism Typology (100% Stacked Bar Chart)**
   * **What it is:** Breaks down the *type* of ML-flagged toxicity (Generic Spam vs. Tone Policing vs. Sexist Slurs) by the gender of the perpetrator.
   * **Purpose:** Proves that harassment isn't homogenous. For example, it might show that Male perpetrators disproportionately use "Tone Policing/Condescension" in female-coded spaces.
9. **Gatekeeping vs. Gatekept (Scatter Plot with Quadrants)**
   * **What it is:** Plots users by their *Total Edit Attempts* (X-axis, Log Scale) against their *Acceptance Rate* (Y-axis). 
   * **Purpose:** Mathematically isolates the "Aggressive Gatekeepers" (High volume, 99% acceptance) from the "Marginalized/Gatekept Users" (Low volume, high rejection).
10. **Cross-Gender Gatekeeping Dyads (Network Graph / Chord Diagram)**
    * **What it is:** Visualizes the flow of Reverts using thick directional arrows (e.g., M→M, F→F, M→F, F→M). 
    * **Purpose:** Maps ideological structural power to see who polices whom the most.
11. **Genuine Contributions vs. Reversions (Stacked Bar Chart)**
    * **What it is:** For each continuum, shows the ratio of edits that were accepted versus edits that were rolled back.
    * **Purpose:** Establishes the baseline "hostility" of different instructional spaces (e.g., Software articles might be heavily reverted, while Knitting articles are rarely touched).

### **Section D: Advanced Behavioral & Ideological Shifts**
*Focus: The long-term sociological consequences of platform dynamics.*

12. **Ideological Domain Shifting (Sankey Diagram / Flow Chart)**
    * **What it is:** A beautiful flow visualization showing users' early-career focus flowing into their late-career focus.
    * **Purpose:** Shows human evolution. Tracks users who shifted from writing highly gendered content to adopting strict gender-neutral language over their tenure.
13. **The "Chilling Effect" / Contributor Retention (Grouped Bar Chart)**
    * **What it is:** Compares the platform abandonment rate of users whose edits were accepted, users who got a normal revert, and users who got a toxic/condescending revert.
    * **Purpose:** Directly links platform toxicity to the gender participation gap, proving that condescending gatekeeping drives people away.
14. **Edit Survival Analysis (Kaplan-Meier Survival Curve)**
    * **What it is:** A curve plotting Time (Hours/Days) against the "Probability of Survival" for a gender-neutralizing edit.
    * **Purpose:** Measures the *intensity* of gatekeeping. Shows how quickly traditionalists hunt down and revert changes like "businessman" to "executive".
