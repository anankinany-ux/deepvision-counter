# Testing & Quality Assurance Guide
## Customer Counter Pro - Comprehensive Testing Plan

Complete testing strategy for ensuring software quality across all platforms.

---

## Table of Contents

1. [Testing Strategy](#testing-strategy)
2. [Unit Testing](#unit-testing)
3. [Integration Testing](#integration-testing)
4. [System Testing](#system-testing)
5. [Platform-Specific Testing](#platform-specific-testing)
6. [Performance Testing](#performance-testing)
7. [Beta Testing](#beta-testing)
8. [Bug Reporting](#bug-reporting)

---

## Testing Strategy

### Testing Pyramid

```
        /\
       /  \
      / UI \         10% - End-to-End Tests
     /______\
    /        \
   / Integr. \      30% - Integration Tests
  /___________\
 /             \
/   Unit Tests  \   60% - Unit Tests
/_________________\
```

### Test Environments

1. **Development**: Local machine, frequent testing
2. **Staging**: Clean VM, pre-release testing
3. **Production**: Real-world scenarios, beta testers

---

## Unit Testing

### Test Framework Setup

```bash
# Install pytest
pip install pytest pytest-cov

# Run tests
pytest test_counter.py -v

# With coverage
pytest --cov=counter_modern test_counter.py
```

### Test Cases

#### test_counter.py

```python
import unittest
import sqlite3
from datetime import datetime
from counter_modern import CustomerTracker, AlertManager

class TestCustomerTracker(unittest.TestCase):
    def setUp(self):
        """Setup test database"""
        self.tracker = CustomerTracker()
        # Use in-memory database for tests
        self.tracker.db = sqlite3.connect(':memory:')
        self.tracker.create_tables()
    
    def tearDown(self):
        """Cleanup"""
        self.tracker.close()
    
    def test_customer_entry(self):
        """Test customer entry recording"""
        entry_time = self.tracker.customer_entered(1, 1)
        self.assertIsNotNone(entry_time)
        self.assertEqual(self.tracker.get_current_occupancy(), 1)
    
    def test_customer_exit(self):
        """Test customer exit recording"""
        self.tracker.customer_entered(1, 1)
        exit_data = self.tracker.customer_exited(1)
        
        self.assertIsNotNone(exit_data)
        self.assertIn('duration', exit_data)
        self.assertEqual(self.tracker.get_current_occupancy(), 0)
    
    def test_multiple_customers(self):
        """Test multiple simultaneous customers"""
        self.tracker.customer_entered(1, 1)
        self.tracker.customer_entered(2, 1)
        self.tracker.customer_entered(3, 1)
        
        self.assertEqual(self.tracker.get_current_occupancy(), 3)
        
        self.tracker.customer_exited(2)
        self.assertEqual(self.tracker.get_current_occupancy(), 2)
    
    def test_duration_calculation(self):
        """Test visit duration calculation"""
        import time
        
        self.tracker.customer_entered(1, 1)
        time.sleep(2)  # Wait 2 seconds
        exit_data = self.tracker.customer_exited(1)
        
        self.assertGreaterEqual(exit_data['duration'], 2)
        self.assertLess(exit_data['duration'], 3)
    
    def test_analytics_empty(self):
        """Test analytics with no data"""
        analytics = self.tracker.get_today_analytics()
        
        self.assertEqual(analytics['total'], 0)
        self.assertEqual(analytics['avg_duration'], 0)
        self.assertEqual(analytics['max_duration'], 0)

class TestAlertManager(unittest.TestCase):
    def setUp(self):
        """Setup alert manager"""
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()  # Hide window
        
        colors = {'warning': '#f59e0b'}
        self.alert_mgr = AlertManager(root, colors)
    
    def test_occupancy_threshold(self):
        """Test occupancy alert configuration"""
        self.alert_mgr.config['occupancy_threshold'] = 10
        self.assertEqual(self.alert_mgr.config['occupancy_threshold'], 10)
    
    def test_alert_cooldown(self):
        """Test alert cooldown mechanism"""
        import time
        
        # First alert should show
        self.assertTrue(self.alert_mgr.should_show_alert('test'))
        
        # Immediate second alert should not show
        self.assertFalse(self.alert_mgr.should_show_alert('test'))
        
        # After cooldown, should show again
        self.alert_mgr.alert_cooldown = 1  # Set to 1 second for testing
        time.sleep(1.1)
        self.assertTrue(self.alert_mgr.should_show_alert('test'))

if __name__ == '__main__':
    unittest.main()
```

### Running Unit Tests

```bash
# Run all tests
python -m pytest test_counter.py -v

# Run specific test
python -m pytest test_counter.py::TestCustomerTracker::test_customer_entry -v

# Generate coverage report
python -m pytest --cov=counter_modern --cov-report=html
```

---

## Integration Testing

### Test Scenarios

#### 1. Database Integration
```python
def test_database_persistence():
    """Test data persists across sessions"""
    tracker1 = CustomerTracker()
    tracker1.customer_entered(1, 1)
    tracker1.customer_exited(1)
    tracker1.close()
    
    # Reopen database
    tracker2 = CustomerTracker()
    analytics = tracker2.get_today_analytics()
    
    assert analytics['total'] >= 1
    tracker2.close()
```

#### 2. UI Integration
```python
def test_ui_counter_update():
    """Test UI updates when counting"""
    import tkinter as tk
    from counter_modern import ModernCounter
    
    root = tk.Tk()
    app = ModernCounter(root)
    
    # Simulate counting
    app.count_in = 5
    app.update_stats()
    
    # Verify UI updated
    assert app.in_label.cget('text') == '5'
    
    root.destroy()
```

#### 3. CSV Export Integration
```python
def test_csv_export():
    """Test CSV export functionality"""
    import os
    import csv
    
    tracker = CustomerTracker()
    tracker.customer_entered(1, 1)
    tracker.customer_exited(1)
    
    # Export
    filepath = 'test_export.csv'
    count = tracker.export_to_csv(filepath, 'today')
    
    # Verify file created
    assert os.path.exists(filepath)
    assert count >= 1
    
    # Verify content
    with open(filepath, 'r') as f:
        reader = csv.reader(f)
        rows = list(reader)
        assert len(rows) > 1  # Header + data
    
    # Cleanup
    os.remove(filepath)
    tracker.close()
```

---

## System Testing

### End-to-End Test Cases

#### Test Case 1: Fresh Installation
**Objective:** Verify clean installation and first-time setup

**Steps:**
1. Install application on clean system
2. Launch for first time
3. Grant camera permissions
4. Position counting line
5. Lock line
6. Start counting
7. Verify counting works
8. Stop and check data saved

**Expected Results:**
- ✓ App launches without errors
- ✓ Camera permissions requested
- ✓ Line can be positioned and locked
- ✓ Counting increments correctly
- ✓ Data persists after restart

---

#### Test Case 2: Multiple Sessions
**Objective:** Verify data from multiple sessions

**Steps:**
1. Start counting session 1
2. Count 5 people IN
3. Count 3 people OUT
4. Stop session
5. Reset counters
6. Start session 2
7. Count 10 people IN
8. Check analytics

**Expected Results:**
- ✓ Session 1 data saved
- ✓ Reset clears displayed counters
- ✓ Session 2 counted separately
- ✓ Total analytics include both sessions

---

#### Test Case 3: Line Crossing Detection
**Objective:** Verify accurate crossing detection

**Steps:**
1. Position camera and line
2. Walk across line from IN side
3. Verify IN counter increments
4. Walk back from OUT side
5. Verify OUT counter increments
6. Stand still on line
7. Verify no additional counts

**Expected Results:**
- ✓ IN correctly detects entry
- ✓ OUT correctly detects exit
- ✓ No false positives from standing
- ✓ Direction consistent with labels

---

#### Test Case 4: Multiple Simultaneous People
**Objective:** Test with multiple people at once

**Steps:**
1. Start counting
2. Have 3 people cross line together
3. Verify all 3 counted
4. Have 2 enter, 1 exit simultaneously
5. Verify correct counts

**Expected Results:**
- ✓ All people detected
- ✓ Counts accurate
- ✓ Direction correctly identified
- ✓ Currently Inside accurate

---

#### Test Case 5: Long Running Session
**Objective:** Test stability over extended period

**Steps:**
1. Start counting
2. Let run for 8 hours
3. Monitor resource usage
4. Count people periodically
5. Check for any issues

**Expected Results:**
- ✓ No crashes or freezes
- ✓ Memory usage stable
- ✓ CPU usage reasonable
- ✓ All features work after hours

---

#### Test Case 6: Analytics Dashboard
**Objective:** Verify all analytics features

**Steps:**
1. Count customers over several hours
2. Open analytics dashboard
3. Check each tab (Traffic, Weekly, Peaks, Duration, Advanced)
4. Export CSV
5. Test all date ranges

**Expected Results:**
- ✓ All charts display correctly
- ✓ Data accurate
- ✓ CSV exports successfully
- ✓ All date ranges work

---

#### Test Case 7: Alert System
**Objective:** Test smart alerts

**Steps:**
1. Configure occupancy alert (threshold: 5)
2. Count 5+ people in
3. Verify alert shows
4. Configure long dwell alert (30 min)
5. Let person stay 30+ minutes
6. Verify alert shows

**Expected Results:**
- ✓ Occupancy alert triggers
- ✓ Long dwell alert triggers
- ✓ Alerts don't repeat immediately (cooldown)
- ✓ Alerts can be dismissed

---

## Platform-Specific Testing

### macOS Testing Matrix

| Version | Architecture | Status |
|---------|--------------|--------|
| macOS 12 (Monterey) | Intel | ✓ |
| macOS 12 (Monterey) | Apple Silicon | ✓ |
| macOS 13 (Ventura) | Intel | ✓ |
| macOS 13 (Ventura) | Apple Silicon | ✓ |
| macOS 14 (Sonoma) | Intel | ✓ |
| macOS 14 (Sonoma) | Apple Silicon | ✓ |

**macOS-Specific Tests:**
- [ ] Camera permissions prompt appears
- [ ] App icon displays correctly in Dock
- [ ] CMD+Q quits properly
- [ ] .app bundle structure correct
- [ ] Code signing (if applicable)
- [ ] Notarization (if applicable)

### Windows Testing Matrix

| Version | Architecture | Status |
|---------|--------------|--------|
| Windows 10 | x64 | ✓ |
| Windows 11 | x64 | ✓ |
| Windows 11 | ARM64 | Untested |

**Windows-Specific Tests:**
- [ ] Camera permissions in Settings
- [ ] App appears in Start Menu
- [ ] Desktop shortcut works
- [ ] Uninstaller works
- [ ] Registry entries (if applicable)
- [ ] Runs without admin rights

### Camera Compatibility

Test with various cameras:
- [ ] Built-in laptop camera
- [ ] USB webcam (Logitech C920)
- [ ] USB webcam (generic)
- [ ] 1080p camera
- [ ] 720p camera
- [ ] 4K camera (downscaled)

---

## Performance Testing

### Metrics to Monitor

#### CPU Usage
```bash
# Mac
top -pid $(pgrep -f counter_modern)

# Windows
# Use Task Manager or Resource Monitor
```

**Acceptable Ranges:**
- Idle (preview): 5-15%
- Counting (AI active): 30-50%
- Analytics: 10-20%

#### Memory Usage
**Acceptable Ranges:**
- Fresh start: 100-200 MB
- After 1 hour: 150-250 MB
- After 8 hours: < 500 MB

**Test for Memory Leaks:**
```python
import psutil
import time

process = psutil.Process()
start_mem = process.memory_info().rss / 1024 / 1024

# Run for 1 hour
time.sleep(3600)

end_mem = process.memory_info().rss / 1024 / 1024
increase = end_mem - start_mem

assert increase < 100, f"Memory leaked {increase}MB"
```

#### Frame Rate
- Preview mode: 15-20 FPS
- Counting mode: 10-15 FPS (AI processing)
- Minimum acceptable: 8 FPS

#### Database Performance
- Insert time: < 10ms
- Query time: < 50ms
- Export 10,000 records: < 5 seconds

---

## Beta Testing

### Beta Program Structure

**Phase 1: Closed Beta (2 weeks)**
- 10-20 selected users
- Diverse use cases (retail, restaurant, gym, etc.)
- Active feedback loop

**Phase 2: Open Beta (4 weeks)**
- Public signup
- Broader testing
- Bug fixes and improvements

### Beta Tester Recruitment

**Criteria:**
- Various business types
- Different technical skill levels
- Willingness to provide feedback
- Different platforms (Mac/Windows)

**Incentives:**
- Lifetime discount (50% off)
- Early access to features
- Recognition in credits

### Feedback Collection

**Daily Check-in Questions:**
1. Did the app work today?
2. Any crashes or errors?
3. Accuracy compared to manual count?
4. Any features you wished existed?
5. Overall satisfaction (1-10)?

**Weekly Survey:**
- Detailed feature feedback
- UI/UX suggestions
- Performance issues
- Use case scenarios

**Tools:**
- Google Forms for surveys
- Discord/Slack for real-time feedback
- GitHub Issues for bug reports
- Email for private feedback

---

## Bug Reporting

### Bug Report Template

```markdown
**Bug Report**

**Title:** Brief description

**Severity:** Critical / High / Medium / Low

**Description:**
Clear description of the issue

**Steps to Reproduce:**
1. Step one
2. Step two
3. Step three

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- OS: macOS 13.2 / Windows 11
- App Version: 1.0.0
- Camera: Logitech C920
- Other: Any relevant details

**Screenshots/Videos:**
Attach if applicable

**Error Messages:**
Copy any error messages

**Additional Context:**
Any other relevant information
```

### Bug Priority Levels

**Critical (P0):**
- App crashes immediately
- Data loss occurs
- Complete feature failure
- Fix within 24 hours

**High (P1):**
- Major feature broken
- Workaround exists but difficult
- Affects many users
- Fix within 1 week

**Medium (P2):**
- Minor feature issue
- Easy workaround available
- Affects some users
- Fix within 1 month

**Low (P3):**
- Cosmetic issues
- Nice-to-have fixes
- Rare edge cases
- Fix in next major release

---

## Quality Gates

Before releasing to beta:
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Manual testing complete
- [ ] No P0 or P1 bugs
- [ ] Performance within acceptable ranges
- [ ] Works on Mac and Windows
- [ ] Documentation complete

Before production release:
- [ ] Beta feedback incorporated
- [ ] All P2 bugs fixed or documented
- [ ] Load testing completed
- [ ] Security review done
- [ ] Licensing system tested
- [ ] Installer tested on clean systems
- [ ] User manual reviewed

---

## Continuous Testing

### Automated Testing Pipeline

```yaml
# Example GitHub Actions workflow
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [macos-latest, windows-latest]
        python-version: [3.8, 3.9, 3.10]
    
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: ${{ matrix.python-version }}
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run tests
      run: pytest test_counter.py -v
```

### Manual Testing Schedule

**Daily (During Active Development):**
- Quick smoke test
- New feature testing

**Weekly:**
- Full regression test suite
- Performance monitoring
- Analytics verification

**Pre-Release:**
- Complete test suite
- Multi-platform testing
- Long-running stability test

---

## Test Data

### Creating Test Data

```python
# Script to generate test data
from counter_modern import CustomerTracker
from datetime import datetime, timedelta
import random

tracker = CustomerTracker()

# Generate 1000 customer entries over last 30 days
for i in range(1000):
    # Random date in last 30 days
    days_ago = random.randint(0, 30)
    entry_date = datetime.now() - timedelta(days=days_ago)
    
    # Random duration (5 min to 2 hours)
    duration = random.randint(300, 7200)
    exit_date = entry_date + timedelta(seconds=duration)
    
    # Insert into database
    tracker.db.execute('''
        INSERT INTO customer_sessions 
        (track_id, entry_time, exit_time, duration_seconds, date, hour, session_number)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        i,
        entry_date.isoformat(),
        exit_date.isoformat(),
        duration,
        entry_date.date().isoformat(),
        entry_date.hour,
        1
    ))

tracker.db.commit()
tracker.close()
print("Test data generated!")
```

---

## Success Criteria

### Release Readiness Checklist

**Functionality:**
- ✓ All core features work
- ✓ Counting accuracy > 95%
- ✓ Analytics display correctly
- ✓ Export works reliably
- ✓ Alerts trigger appropriately

**Performance:**
- ✓ CPU usage acceptable
- ✓ No memory leaks
- ✓ Smooth frame rate
- ✓ Responsive UI

**Stability:**
- ✓ No crashes in 48-hour test
- ✓ Handles errors gracefully
- ✓ Database corruption protection
- ✓ Camera disconnect recovery

**Usability:**
- ✓ Intuitive for new users
- ✓ Clear error messages
- ✓ Helpful tooltips
- ✓ Complete documentation

**Compatibility:**
- ✓ Works on macOS 12+
- ✓ Works on Windows 10+
- ✓ Various cameras supported
- ✓ Offline functionality

---

**Testing is an ongoing process. Continue gathering feedback and improving!**

**Questions?** Contact qa@customercounterpro.com

