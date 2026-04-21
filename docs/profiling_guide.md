# WikiHow Deep Profiling Guide

This document defines the methodology for extracting demographic and professional intelligence from WikiHow contributor profiles.

## Methodology

We use a hybrid approach combining **Structured Scripting** and **Generative AI Vision**.

### 1. Scriptable Data (Stable)
The following elements are extracted via direct CSS/XPath selectors due to their stability in the WikiHow DOM:
- **Username**: `.firstHeading`
- **Badges**: `a.pb-badge` list (Admin, Booster, Specialist, etc.).
- **Header Metadata**: Pronouns and Location (when present in the standard header card).

### 2. Deep Extraction (Generative AI)
We use DeepSeek Vision to reason over unstructured areas of the profile:
- **Tenure (Age)**: Extracted from varied header and bio strings (e.g., "over 19 years!").
- **Profession/Industry**: Inferred from bio text, user roles, and "Articles Started" themes (e.g., a user starting 50 articles on "Legal Advice" is tagged with 'Legal Industry').
- **Account Type**: Distinguishing between Human contributors, automated Bots, and organizational accounts.

## Schema Definition

| Field | Description | Type |
| :--- | :--- | :--- |
| `inferred_gender` | Male, Female, Non-Binary, or Unknown. | Categorical |
| `tenure` | Years active on WikiHow. | Integer/String |
| `location` | City, State, Country (derived from header/bio). | String |
| `profession_industry`| Primary field of expertise or employment. | Categorical |
| `badges` | List of community roles. | List |
| `layout_variation` | Standard, Widget-Based, or Custom-HTML. | Categorical |

## Layout Variations Identified

### Standard Layout
The default WikiHow profile structure. Single column bio with a header card.

### Widget-Based Layout (Legacy)
Uses multiple legacy "boxes" (UIBs) for stats. Common among 2005-2010 era veterans (e.g., **Flickety**).

### Custom-HTML Layout
Highly customized profiles using internal WikiHow CSS/HTML overrides (e.g., **Zack**). These require full-page visual context as stat locations are non-standard.
