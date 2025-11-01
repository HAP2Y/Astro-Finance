# Testing Guide for Astro-Finance Notebook

This guide explains how to test the notebook changes, particularly the improved logging structure.

## Option 1: Testing in Google Colab (Recommended)

Google Colab is the primary execution environment for this notebook. This is the most direct way to test all functionality.

### Quick Test (5-10 minutes)

1. **Open the notebook in Colab**
   - Go to: https://colab.research.google.com/github/HAP2Y/Astro-Finance/blob/claude/improve-notebook-logging-011CUgfaDKN7wnTe2USKG74D/AstroFinanceProject.ipynb
   - Or click the "Open in Colab" badge at the top of the notebook

2. **Run Cell 1 (Financial Data Acquisition)**
   ```
   Runtime → Run the focused cell (Ctrl/Cmd + Enter)
   ```

3. **Verify the logging improvements:**

   ✅ **Check for timestamps:**
   ```
   2025-11-01 06:09:15 | INFO     | ======================================================================
   2025-11-01 06:09:15 | INFO     | ASTRO-FINANCE PROJECT - PHASE 1: FINANCIAL DATA ACQUISITION
   ```

   ✅ **Check for log levels:**
   - `INFO` for general messages
   - `WARNING` for skipped operations
   - `ERROR` for failures
   - `CRITICAL` for fatal errors

   ✅ **Check for preserved formatting:**
   - Progress indicators (✓, ⚠, ✗)
   - Table output with tabulate
   - Section separators (=== lines)

4. **Test error handling:**
   - If Google Drive mount fails, you should see:
   ```
   YYYY-MM-DD HH:MM:SS | CRITICAL | ✗ FATAL ERROR: Could not mount Google Drive
   YYYY-MM-DD HH:MM:SS | CRITICAL |   Error: <error message>
   ```

5. **Run additional cells (optional):**
   - Cell 2: Vedic Astrological Data Generation
   - Cell 3: Data Alignment & Merging
   - Any cells from Phase 2 (Feature Engineering)

### Full Test (30-60 minutes)

Run all cells sequentially to ensure:
- All cells execute without syntax errors
- Logging output is consistent across all cells
- Timestamps appear on all log entries
- Appropriate log levels are used throughout
- Tables still render properly with `print(tabulate(...))`

### What to Look For

**✅ Expected behavior:**
- Timestamps on every log line
- Log level indicators (INFO, WARNING, ERROR, CRITICAL)
- Preserved visual formatting (emojis, checkmarks, progress bars)
- Tabulated output still displays as formatted tables
- No duplicate logging configuration warnings

**❌ Issues to report:**
- Missing timestamps
- Incorrect log levels
- Broken table formatting
- Syntax errors
- Import errors

## Option 2: Automated Validation with GitHub Actions

A GitHub Actions workflow has been set up to automatically validate:
- Notebook structure integrity
- Python syntax in all code cells
- Logging configuration presence
- Required dependencies

### How it works:

1. **Automatic triggers:**
   - Runs on every push to `claude/**` branches
   - Runs on pull requests to `main` branch
   - Only runs when `.ipynb` files are modified

2. **What it validates:**
   - ✓ Notebook JSON structure is valid
   - ✓ All code cells have valid Python syntax
   - ✓ Logging module is properly configured
   - ✓ Logger instances are created
   - ✓ Appropriate log levels are used
   - ✓ Required dependencies are imported

3. **View results:**
   - Go to: https://github.com/HAP2Y/Astro-Finance/actions
   - Click on the latest workflow run
   - View the "Validate Notebook" job
   - Check the step summaries and logs

### Manual workflow trigger:

You can also manually run the workflow:
1. Go to Actions tab in GitHub
2. Select "Validate Notebook" workflow
3. Click "Run workflow"
4. Select your branch
5. Click "Run workflow" button

## Option 3: Local Testing (Advanced)

For developers who want to test locally without Colab:

### Prerequisites:
```bash
pip install nbformat nbconvert jupyter
pip install pandas numpy yfinance tabulate pyswisseph
```

### Validate syntax:
```bash
jupyter nbconvert --to python AstroFinanceProject.ipynb --stdout | python -m py_compile -
```

### Extract and check logging:
```bash
python3 << 'EOF'
import json

with open('AstroFinanceProject.ipynb', 'r') as f:
    nb = json.load(f)

code_cells = [c for c in nb['cells'] if c['cell_type'] == 'code']

for i, cell in enumerate(code_cells):
    source = cell['source'] if isinstance(cell['source'], str) else ''.join(cell['source'])

    if 'import logging' in source:
        print(f"✓ Cell {i+1}: Has logging configuration")

        # Count logger calls
        info_count = source.count('logger.info(')
        warn_count = source.count('logger.warning(')
        error_count = source.count('logger.error(')
        critical_count = source.count('logger.critical(')

        print(f"  INFO: {info_count}, WARNING: {warn_count}, ERROR: {error_count}, CRITICAL: {critical_count}")
EOF
```

## Comparison: Before vs After

### Before (using print):
```python
print("=" * 70)
print("ASTRO-FINANCE PROJECT - PHASE 1")
print("  ✓ Libraries imported")
```

**Output:**
```
======================================================================
ASTRO-FINANCE PROJECT - PHASE 1
  ✓ Libraries imported
```

### After (using logging):
```python
logger.info("=" * 70)
logger.info("ASTRO-FINANCE PROJECT - PHASE 1")
logger.info("  ✓ Libraries imported")
```

**Output:**
```
2025-11-01 06:09:15 | INFO     | ======================================================================
2025-11-01 06:09:15 | INFO     | ASTRO-FINANCE PROJECT - PHASE 1
2025-11-01 06:09:15 | INFO     |   ✓ Libraries imported
```

## Troubleshooting

### Issue: "Multiple logging handlers" warning
**Cause:** Running cells multiple times in Colab
**Solution:** Restart runtime (Runtime → Restart runtime)

### Issue: Timestamp format looks wrong
**Expected format:** `YYYY-MM-DD HH:MM:SS | LEVEL | message`
**If different:** Check logging.basicConfig in the cell

### Issue: Tables not displaying properly
**Check:** Ensure `print(tabulate(...))` is used, not `logger.info(tabulate(...))`

### Issue: Google Drive mount fails
**This is expected** for the logging test - we're primarily testing that the error is logged with CRITICAL level and proper formatting

## Reporting Issues

If you find any issues during testing:

1. **For Colab testing:**
   - Take a screenshot of the error
   - Note which cell failed
   - Copy the error message

2. **For GitHub Actions:**
   - Click on the failed workflow run
   - Copy the error from the failed step
   - Note the validation step that failed

3. **Report via:**
   - GitHub Issues: https://github.com/HAP2Y/Astro-Finance/issues
   - Or comment on the PR

## Success Criteria

The logging improvements are working correctly if:

- ✅ All cells execute without syntax errors
- ✅ Every log line has a timestamp
- ✅ Log levels are appropriate (INFO for normal, WARNING/ERROR/CRITICAL for issues)
- ✅ Visual formatting is preserved (✓, ⚠, ✗, emojis)
- ✅ Tables still render cleanly
- ✅ GitHub Actions workflow passes
- ✅ No regression in functionality
