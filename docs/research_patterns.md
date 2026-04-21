# Profiling Intelligence: Research Patterns & Personas

This document provides a detailed breakdown of the contributor personas and visual patterns identified during the deep-dive research of 50+ veteran WikiHow accounts. These findings form the basis of our AI-driven demographic stratification.

## 👥 Contributor Personas

Our analysis identifies four primary classes of contributors, each with distinct visual 'signatures' on their profile pages.

### 1. The Institutional Staff/Employee
**Signature**:
- **Badge**: Orange "STAFF" or "STAFFCircle" icon.
- **Identity**: Often uses real names (e.g., *Jack Herrick*, *Tiago Roth*) or placeholders (e.g., *WikiHow Intern*).
- **Behavior**: High "Patrol" counts and bio mentions of "Engineering," "Product," or specific WikiHow headquarters (Palo Alto).
- **Impact**: These accounts represent institutional steering rather than volunteer community sentiment.

### 2. The Volunteer Power-Admin
**Signature**:
- **Badge Trio**: ADMIN, BOOSTER, and FEATURED badges.
- **Inference**: Usually veteran accounts (10-19+ years).
- **Behavior**: Bios emphasize "Welcoming," "Help Team," and "Mentoring." Their statistics show a balanced ratio of Articles Started to Edits.
- **Identity**: Often gender-disclosed (e.g., *Whimaway* / Sarah Eliza) and location-aware.

### 3. The Professional Specialist
**Signature**:
- **Authority Indicators**: Bios explicitly state real-world credentials (e.g., 'Ph.D in Biology', 'Ordained Minister', 'Legal Specialist').
- **Niche Focus**: Their "Articles Started" are tightly clustered around a single domain (e.g., Healthcare, Law, or Craftsmanship).
- **Research Value**: These are the highest-quality profiles for "Professional Stratification" analysis.

### 4. The 'WikiGnome' Hobbyist
**Signature**:
- **High Diversity**: "Articles Started" cover a massive, unrelated range (e.g., *How to Make Slime* vs. *How to Fix a Leaky Header*).
- **Identity**: Often anonymous or using aliases. Gender is usually inferred from bio pronouns (she/her) rather than professional titles.
- **Motivation**: Driven by "Cleaning up the wiki" and general knowledge sharing.

---

## 🤖 AI Inference Heuristics

To ensure consistent demographic data, our DeepSeek profiler uses the following heuristic logic:

| Observation | Inference | Confidence |
| :--- | :--- | :--- |
| Mentions 'wife', 'husband', or 'teen girl' | Self-ID Gender | **HIGH** |
| Lists professional credentials (MD, PhD, Chaplain) | Professional Archetype | **HIGH** |
| Username contains 'Bot' + Minimal Bio | Automated Account | **EXTREME** |
| 10+ year tenure + Admin Badge | Community Pillar | **MEDIUM** |
| Diverse articles + No niche | Hobbyist Generalist | **MEDIUM** |

## 📐 Layout Variation Analysis

| Layout Type | Affected Users | Scrape Strategy |
| :--- | :--- | :--- |
| **Standard** | 85% of users | Scripted CSS Selectors (Stable) |
| **Widget-Based** | Legacy Veterans | Table-Row Scanning for 'My Roles' |
| **Custom HTML** | Elite Veterans (Zack) | **Full-Page Vision Reasoning** (AI required to find stats embedded in custom <div> units) |
