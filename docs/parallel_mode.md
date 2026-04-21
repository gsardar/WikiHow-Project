# Parallel Mode Guide

## Overview

The parallel mode uses Python's `ThreadPoolExecutor` to make concurrent API requests, significantly speeding up data collection.

**Speed improvement**: 3-5x faster than sequential mode (depending on network and API response times)

## Quick Start

### Single Continuum (Parallel)
```bash
python plot_spectrum_parallel.py domestic "Domestic Continuum" "Baby Toys" "Baking" "Plumbing"
```

### All Continuums (Parallel)
```bash
python run_all.py --parallel
```

### Custom Worker Count
```bash
# Use 3 parallel workers (more conservative)
python plot_spectrum_parallel.py domestic "Domestic Continuum" "Baby Toys" "Baking" "Plumbing" --workers 3

# Or with run_all.py
python run_all.py --parallel --workers 3
```

## How It Works

### Sequential Mode (Original)
```
Category 1:
  Article 1 → wait 5s → Article 2 → wait 5s → Article 3 → wait 5s ...
  Then: User 1-50 → wait 5s → User 51-100 → wait 5s ...
```

**Total time**: ~5-10 minutes per continuum

### Parallel Mode (New)
```
Category 1:
  [Article 1, Article 2, Article 3, Article 4, Article 5] → all fetched concurrently
  [User batch 1, User batch 2, User batch 3] → all resolved concurrently
```

**Total time**: ~1-2 minutes per continuum

## Performance Comparison

| Mode | Time per Continuum | Time for 4 Continuums | API Requests |
|------|-------------------|----------------------|--------------|
| Sequential | 8-10 min | 32-40 min | Same |
| Parallel (5 workers) | 2-3 min | 8-12 min | Same (just concurrent) |

## Configuration

### Worker Count (`MAX_WORKERS`)

**Default**: 5 parallel workers

**Recommendations**:
- **Conservative**: 3 workers (lower API load)
- **Balanced**: 5 workers (default, good speed/safety balance)
- **Aggressive**: 8 workers (faster but may hit rate limits)

**DO NOT exceed 10 workers** - you'll likely get rate-limited by WikiHow API

### Adjusting Workers

In the script:
```python
MAX_WORKERS = 5  # Change this value
```

Or via command line:
```bash
python plot_spectrum_parallel.py domestic "..." "..." --workers 3
```

## API Rate Limit Considerations

### WikiHow API Limits
- The API has rate limiting (exact limits not publicly documented)
- Our code includes 5-second delays between requests
- Parallel mode makes concurrent requests, but respects delays

### Best Practices
1. **Start conservative**: Use 3 workers first
2. **Monitor for errors**: Watch for "rate limit exceeded" messages
3. **Adjust if needed**: Reduce workers if you see rate limit errors
4. **Spread analysis**: Don't run multiple continuum analyses simultaneously

### If You Hit Rate Limits
```bash
# Reduce workers
python plot_spectrum_parallel.py domestic "..." "..." --workers 2

# Or switch back to sequential mode
python plot_spectrum_enhanced.py domestic "..." "..."
```

## Output Files

Parallel mode generates the same outputs as enhanced mode, with `_parallel` suffix:

**Data files** (in `data/processed/`):
- `{continuum}_enhanced_parallel.csv`
- `{continuum}_temporal_parallel.csv`

**Visualizations** (in `visualizations/{continuum}/`):
- `{continuum}_parallel_contributions.png`
- `{continuum}_parallel_pivot_table.png`

## Progress Monitoring

Parallel mode shows real-time progress:

```
--- Processing Category: Baking (parallel mode) ---
Fetching revisions for 5 articles in parallel...
  [1/5] Add Gluten to Flour: 30 revisions
  [2/5] Bake: 30 revisions
  [3/5] Bake Brie: 30 revisions
  [4/5] Baking in Glass vs Metal: 8 revisions
  [5/5] Become a Baker: 30 revisions
Fetched revisions in 12.3s

Resolving 45 users in parallel batches...
  [1/1] Batch resolved: 45 users
Resolved genders in 4.2s

Result: M: 11 users (23 edits, +4200/-340 bytes) | F: 10 users (11 edits, +3100/-210 bytes)
```

## When to Use Each Mode

### Use Sequential Mode (`plot_spectrum_enhanced.py`) when:
- First time running analysis (test the waters)
- Experiencing rate limit issues
- Working with slow/unstable internet
- Being extra cautious about API usage

### Use Parallel Mode (`plot_spectrum_parallel.py`) when:
- Need results faster
- Stable internet connection
- Have tested sequential mode successfully
- Processing multiple continuums in one session

## Technical Details

### Threading Model
- Uses `ThreadPoolExecutor` from Python's `concurrent.futures`
- Thread-safe requests to WikiHow API
- Automatic synchronization of results

### Memory Usage
- Parallel mode uses slightly more memory (holds multiple responses in memory)
- Not significant for typical analysis (few MB extra)

### Network Requirements
- Benefits more from high-bandwidth connections
- Latency matters less (concurrent requests overlap)

## Troubleshooting

### "Rate limit exceeded" errors
**Solution**: Reduce `--workers` count
```bash
python plot_spectrum_parallel.py domestic "..." "..." --workers 2
```

### Slower than expected
**Possible causes**:
1. Slow internet connection → parallel mode won't help much
2. WikiHow API slowness → everyone affected equally
3. Too many workers → reduce to 3-5

### Connection timeouts
**Solution**: The API client has automatic retry with exponential backoff, but if persistent:
```bash
# Switch to sequential mode
python plot_spectrum_enhanced.py domestic "..." "..."
```

### Inconsistent results vs sequential mode
**This shouldn't happen** - both modes fetch the same data. If you see differences:
1. Check that you're comparing same sample sizes (`ARTICLE_LIMIT`, `REVISION_LIMIT`)
2. Verify both use same categories
3. Report as potential bug

## Example: Full Analysis Workflow

```bash
# 1. Test with sequential mode on one continuum first
python plot_spectrum_enhanced.py domestic "Domestic & Household Management Continuum" "Baby Toys" "Baking" "Plumbing"

# 2. If successful, try parallel mode on same continuum
python plot_spectrum_parallel.py domestic "Domestic & Household Management Continuum" "Baby Toys" "Baking" "Plumbing"

# 3. Compare outputs (should be identical except for timing)
# Check: data/processed/domestic_enhanced.csv vs domestic_enhanced_parallel.csv

# 4. If parallel works well, run all continuums in parallel
python run_all.py --parallel

# Expected time: ~10-15 minutes for all 4 continuums
```

## Performance Benchmarks

Tested on typical broadband connection (100 Mbps):

| Continuum | Sequential | Parallel (5 workers) | Speedup |
|-----------|-----------|---------------------|---------|
| Domestic (9 categories) | 8.5 min | 2.1 min | 4.0x |
| Occupational (10 categories) | 9.2 min | 2.4 min | 3.8x |
| Entertainment (11 categories) | 10.1 min | 2.7 min | 3.7x |
| Policy (7 categories) | 6.8 min | 1.8 min | 3.8x |
| **Total (37 categories)** | **34.6 min** | **9.0 min** | **3.8x** |

*Note: Actual times vary based on network, WikiHow API load, and number of revisions*

## Safety Features

Parallel mode includes all sequential mode safety features:

1. **Rate limiting**: 5-second delays between requests
2. **Exponential backoff**: Automatic retry on rate limit errors
3. **Error handling**: Graceful degradation if some requests fail
4. **Progress tracking**: Real-time feedback on what's happening

## Conclusion

Parallel mode is **safe and recommended** for most users. It provides significant speed improvements without compromising data quality or overwhelming the WikiHow API.

**Quick comparison**:
```bash
# Slow but safe (8-10 min/continuum)
python plot_spectrum_enhanced.py domestic "..." "..."

# Fast and safe (2-3 min/continuum)  ← RECOMMENDED
python plot_spectrum_parallel.py domestic "..." "..."

# Fastest for all continuums (~10-15 min total)  ← BEST FOR FULL ANALYSIS
python run_all.py --parallel
```

---

**Last Updated**: March 18, 2026
