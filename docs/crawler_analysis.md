# WikiHow Complete Crawl - Size Estimation & Strategy

## 📊 Size Estimation

### WikiHow Statistics (Estimated)

Based on WikiHow's scale:
- **Total articles**: ~250,000 articles (as of 2024)
- **Languages**: 18+ languages (English is largest)
- **English articles**: ~180,000-200,000
- **Categories**: ~5,000+ categories

### Storage Size Breakdown

#### 1. Article Content Only

**Per Article:**
- Article HTML: ~50-150 KB average
- Images (if downloaded): ~500 KB - 2 MB average (3-10 images per article)
- Metadata: ~5 KB

**Conservative estimate (text only, no images):**
- 200,000 articles × 100 KB = **20 GB**

**With images:**
- 200,000 articles × 1 MB (avg) = **200 GB**

#### 2. Edit History (Revisions)

This is where it gets BIG!

**Per Article Revision:**
- Revision metadata: ~2 KB (user, timestamp, comment, size)
- Full revision content: ~50-150 KB (if storing full text)
- Diff only: ~5-20 KB (if storing diffs)

**Average revisions per article**: ~30-100 revisions (popular articles can have 1,000+)

**Conservative estimate (metadata + diffs only):**
- 200,000 articles × 50 revisions × 10 KB = **100 GB**

**Full revision content:**
- 200,000 articles × 50 revisions × 100 KB = **1 TB (1,000 GB)**

#### 3. User Information

**Users to track:**
- Active editors: ~50,000-100,000
- Historical editors: ~500,000+

**Per User:**
- Profile data: ~5-10 KB
- Gender inference results: ~1 KB

**Total:**
- 500,000 users × 10 KB = **5 GB**

---

## 💾 Total Storage Estimates

| Crawl Type | Storage Required |
|------------|------------------|
| **Minimal** (current articles only, no images) | ~20 GB |
| **Basic** (articles + revision metadata) | ~50 GB |
| **Standard** (articles + revision diffs + users) | ~150 GB |
| **Complete** (articles + full revisions + images) | **1.2 TB** |
| **Full Archive** (all versions, all images, all metadata) | **2-3 TB** |

---

## 🎯 Recommended Approach: Incremental Crawling

### Strategy 1: Category-Based Crawl (RECOMMENDED)

Instead of crawling ALL of WikiHow, focus on your research needs:

**For your 4 continuums (37 categories):**
- Articles per category: ~100-500
- Total articles: ~5,000-10,000
- Revisions: ~250,000-500,000

**Storage:**
- Articles: ~500 MB - 1 GB
- Revision metadata: ~5-10 GB
- Revision diffs: ~2-5 GB
- **Total: ~10-15 GB** (very manageable!)

### Strategy 2: Sampled Full Crawl

- Crawl all categories (metadata only)
- Sample articles from each category (e.g., 10 per category)
- Full revision history for sampled articles

**Storage: ~50-100 GB**

### Strategy 3: Complete Historical Archive

- All articles
- All revisions (full content)
- All images
- All user data

**Storage: ~2-3 TB**
**Time: Several weeks to months**
**Legal: May require WikiHow permission**

---

## ⚖️ Legal & Ethical Considerations

### WikiHow's Terms of Service

WikiHow content is licensed under **Creative Commons CC BY-NC-SA 3.0**:
- ✅ You CAN: Download for research/analysis
- ✅ You CAN: Use for academic purposes
- ❌ You CANNOT: Use commercially without permission
- ⚠️ You SHOULD: Respect rate limits
- ⚠️ You SHOULD: Not overload their servers

### Best Practices

1. **Use API, not web scraping** - More efficient, more ethical
2. **Respect rate limits** - 5 second delays (as we do now)
3. **Crawl during off-peak hours** - Less server load
4. **Cache everything** - Don't re-fetch
5. **Consider contacting WikiHow** - For large crawls, ask permission

---

## 🏗️ Crawler Architecture

### Option A: Incremental Crawler (Recommended)

```
Phase 1: Category Discovery
- Fetch all categories
- Store category tree
- ~1 hour, ~10 MB

Phase 2: Article Discovery
- Fetch articles per category
- Store article metadata
- ~2-5 hours, ~100 MB

Phase 3: Revision Crawling
- Fetch revisions for articles
- Store revision metadata + diffs
- ~24-48 hours, ~10-50 GB

Phase 4: Content Crawling
- Fetch full article content
- Optional: download images
- ~12-24 hours, ~5-20 GB
```

### Option B: Full Crawl

```
Phase 1: Complete Category Tree
Phase 2: All Article Metadata (~200K articles)
Phase 3: All Revisions (~10M revisions)
Phase 4: Full Content + Images
```

**Time: 2-4 weeks continuous**
**Storage: 1-3 TB**

---

## 🛠️ Crawler Design

### Database Schema

```sql
-- Articles
CREATE TABLE articles (
    article_id INTEGER PRIMARY KEY,
    title TEXT UNIQUE,
    category_id INTEGER,
    created_at TIMESTAMP,
    creator_user_id INTEGER,
    current_size INTEGER,
    total_revisions INTEGER,
    content_html TEXT,
    last_crawled TIMESTAMP
);

-- Revisions
CREATE TABLE revisions (
    revision_id INTEGER PRIMARY KEY,
    article_id INTEGER,
    user_id INTEGER,
    timestamp TIMESTAMP,
    size INTEGER,
    size_delta INTEGER,
    comment TEXT,
    is_minor BOOLEAN,
    content_diff TEXT,  -- Store diff, not full content
    FOREIGN KEY (article_id) REFERENCES articles(article_id)
);

-- Users
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    gender TEXT,  -- male/female/unknown
    gender_source TEXT,  -- profile/pronouns/genderize
    editcount INTEGER,
    registration TIMESTAMP,
    last_updated TIMESTAMP
);

-- Categories
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    parent_category_id INTEGER,
    article_count INTEGER
);
```

### Storage Format

**Recommended: SQLite Database**
- Advantages:
  - Single file (portable)
  - Fast queries
  - No server needed
  - Good compression

**Alternative: JSON Files**
- Advantages:
  - Human-readable
  - Easy to process
  - Language-agnostic

**Alternative: Parquet Files**
- Advantages:
  - Columnar storage
  - Best compression
  - Fast for analytics

---

## ⚡ Optimization Strategies

### 1. Compression

- **gzip**: 60-70% reduction
- **bzip2**: 70-80% reduction
- **xz**: 75-85% reduction

**Example:**
- 100 GB uncompressed → 20-30 GB compressed

### 2. Diff Storage

Instead of storing full revision content, store diffs:
- First revision: Full content
- Subsequent revisions: Only changes (diff)

**Savings: 80-90%**

### 3. Deduplication

Many revisions have identical content (reverts, vandalism fixes):
- Store unique content once
- Reference by hash

**Savings: 30-50%**

### 4. Selective Fields

Don't store everything:
- ✅ Keep: user, timestamp, size_delta, comment
- ❌ Skip: IP addresses, detailed flags

**Savings: 20-30%**

---

## 📈 Realistic Crawl Plans

### Plan A: Research-Focused (RECOMMENDED)

**Target:**
- 4 continuums (37 categories)
- ~5,000-10,000 articles
- Full revision history
- User metadata

**Storage: ~10-20 GB**
**Time: ~24-48 hours**
**Cost: Free (using WikiHow API)**

**Implementation:**
```bash
python crawler.py --mode research --categories data/mapped_spaces.json
```

### Plan B: Category Sampling

**Target:**
- All categories (5,000+)
- 10 sample articles per category
- Last 50 revisions per article

**Storage: ~50-100 GB**
**Time: ~1 week**
**Cost: Free (with rate limiting)**

### Plan C: Complete Archive

**Target:**
- All articles (200,000)
- All revisions (~10M)
- Full content

**Storage: ~1-2 TB**
**Time: ~2-4 weeks**
**Cost: May need dedicated server, WikiHow permission**

---

## 🚦 Crawl Rate Limits

### Current Rate (Conservative)
- 5 seconds per request
- ~720 requests/hour
- ~17,000 requests/day
- ~500,000 requests/month

### Aggressive (with permission)
- 1 second per request
- ~3,600 requests/hour
- ~85,000 requests/day

### To Crawl 200,000 Articles

**Articles only (1 request each):**
- Conservative: ~12 days
- Aggressive: ~2.5 days

**With revisions (50 revisions per article = 10M requests):**
- Conservative: **~600 days (1.6 years!)**
- Aggressive: **~120 days (4 months)**

**This is why selective crawling is recommended!**

---

## 💡 Recommendations

### For Your Research Project

**Best Approach:**
1. ✅ **Crawl your 4 continuums** (~10-20 GB, 1-2 days)
2. ✅ **Store in SQLite database** (portable, efficient)
3. ✅ **Use compression** (gzip or xz)
4. ✅ **Cache everything** (never re-fetch)
5. ✅ **Respect rate limits** (5 sec delays)

**You'll get:**
- Complete data for your research
- Manageable storage
- Reasonable crawl time
- Ethical/legal compliance

### If You Need More Data

1. **Contact WikiHow** - Ask for data dump or increased rate limits
2. **Use sampling** - Representative sample instead of full crawl
3. **Collaborate** - Share crawl costs with other researchers
4. **Use existing datasets** - Check if Wikipedia/WikiHow datasets exist

---

## 📝 Next Steps

Would you like me to build:

1. **Option A**: Focused crawler for your 4 continuums (~10-20 GB)
2. **Option B**: Category sampling crawler (~50-100 GB)
3. **Option C**: Full archive crawler (~1-2 TB)

**I recommend Option A** - gives you everything you need for your research without overwhelming storage/time requirements.

---

## 📊 Summary Table

| Aspect | Research Crawl | Sample Crawl | Full Archive |
|--------|---------------|--------------|--------------|
| **Articles** | ~10,000 | ~50,000 | ~200,000 |
| **Revisions** | ~500,000 | ~2,500,000 | ~10,000,000 |
| **Storage** | 10-20 GB | 50-100 GB | 1-2 TB |
| **Time** | 1-2 days | 1 week | 2-4 weeks |
| **Feasibility** | ✅ Easy | ⚠️ Moderate | ❌ Challenging |
| **Legal** | ✅ Clear | ✅ Clear | ⚠️ Need permission |
| **Cost** | Free | Free | $$$ Server costs |

**Recommendation: Start with Research Crawl, expand if needed!**
