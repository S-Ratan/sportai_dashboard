# Local Testing & Verification Guide

## Quick Verification Checklist

### ✅ Part 1: Dashboard UI
- [ ] Frontend displays "PS-02 Dashboard" tab as default
- [ ] All 6 panels visible: KPI Cards, Video Analysis, Biomechanics Chart, Movement Risk, AI Coach, Historical Trends
- [ ] KPI cards show: Performance Score (78), Movement Risk (32), Asymmetry (18), Fatigue (45)
- [ ] Mock data displays correctly in all charts
- [ ] Tab switching works between Dashboard, Analyze Video, Report History
- [ ] Responsive design works on different window sizes

### ✅ Part 2: Biomechanical Service
- [ ] All 25 unit tests pass
- [ ] No syntax errors in modified files
- [ ] Video upload pipeline still works
- [ ] Backend compiles without errors

---

## Detailed Verification Steps

### Step 1: Verify Tests Pass
```bash
cd f:\download\sportai_dashboard\backend
python tests\test_biomechanics_service.py
```

**Expected Output**:
```
============================================================
Testing Biomechanical Calculation Service
============================================================

Testing Helper Functions:
✓ test_is_valid_angle passed
✓ test_clean_angle passed

... [21 more tests] ...

✅ All tests passed!
============================================================
```

**If tests fail**:
- Check Python version (3.8+)
- Verify backend/app module path is correct
- Check for syntax errors in biomechanics_service.py

---

### Step 2: Verify Backend Compilation
```bash
cd f:\download\sportai_dashboard\backend
python -m py_compile app/services/biomechanics_service.py
python -m py_compile app/api/routes.py
```

**Expected Output**: No output (silence = success)

**If you see errors**:
- Check import statements in routes.py
- Verify all function definitions are present in biomechanics_service.py

---

### Step 3: Verify Frontend Dashboard
1. Open terminal in workspace root
2. Start dev server: `npm run dev` or `npm start`
3. Open browser to localhost (usually http://localhost:5173)
4. Verify you see the Dashboard tab active by default
5. Scroll through all panels and verify:

**KPI Cards Section**:
- 4 cards with icons and trend arrows
- Green card: Performance Score (78)
- Orange card: Movement Risk (32)
- Orange card: Asymmetry (18)
- Red card: Fatigue (45)

**Video Analysis Panel**:
- Shows "Last Analyzed: 5 minutes ago"
- Shows "1,240 frames processed"
- Shows "98.5% detection rate"
- Shows video metadata

**Biomechanics Chart Panel**:
- Bar chart with left (green) and right (blue) measurements
- X-axis labels: Knee, Hip, Ankle, Shoulder
- Y-axis: Angle values (0-180)

**Movement Risk Panel**:
- 3 risk factors listed
- Each has a progress bar
- Shows severity badges (High/Medium/Low)

**AI Coach Panel**:
- 3 prioritized recommendations
- Each has a priority badge
- Shows actionable text

**Historical Trend Panel**:
- Line chart showing 7-day trend
- 3 colored lines for: Performance (green), Risk (orange), Fatigue (red)
- X-axis shows day abbreviations

---

### Step 4: Verify Integration Intact
1. Click the "Analyze Video" tab
2. Verify the upload interface still works
3. Upload a test video (if available)
4. Wait for analysis to complete
5. Check that results appear

**What to look for**:
- No 404 or 500 errors
- Analysis completes successfully
- Results display properly
- Dashboard data can be refreshed

---

### Step 5: Test Data Flow (Manual)
To manually trace the data flow:

1. **Monitor Backend Logs**:
```bash
cd backend
python app/main.py
# Observe logs during video upload
```

2. **Check Video Analysis Response**:
- Upload a video
- Open browser DevTools (F12)
- Go to Network tab
- Look for `/analyze` request
- Check the response JSON for `biomechanics_summary`

3. **Verify biomechanics_summary Structure**:
```json
{
  "left_knee": {
    "min_angle": number,
    "max_angle": number,
    "avg_angle": number,
    "range_of_motion": number,
    "avg_angular_velocity": number
  },
  // ... other joints ...
  "asymmetry_summary": {
    "avg_knee_asymmetry": number,
    "avg_hip_asymmetry": number,
    "avg_elbow_asymmetry": number
  }
}
```

---

## Testing Individual Functions

### Test calculate_knee_rom()
```python
from backend.app.services.biomechanics_service import calculate_knee_rom

# Test with sample data
angles = [80.0, 85.0, 90.0, 100.0, 120.0, 110.0]
result = calculate_knee_rom(angles)
print(result)
# Expected: {"min_angle": 80.0, "max_angle": 120.0, "range_of_motion": 40.0, ...}
```

### Test calculate_angular_velocity()
```python
from backend.app.services.biomechanics_service import calculate_angular_velocity

# Test steady movement (5° per frame)
angles = [90.0, 95.0, 100.0, 105.0, 110.0]
velocity = calculate_angular_velocity(angles)
print(velocity)
# Expected: 5.0
```

### Test aggregate_biomechanics()
```python
from backend.app.services.biomechanics_service import aggregate_biomechanics

frames = [
    {
        "left_knee_angle": 85.0,
        "right_knee_angle": 87.0,
        "left_hip_angle": 95.0,
        "right_hip_angle": 93.0,
        "trunk_tilt": 10.0,
        "knee_asymmetry": 2.0,
        "hip_asymmetry": 2.0,
        "elbow_asymmetry": 3.0,
    },
    # ... more frames ...
]

result = aggregate_biomechanics(frames)
print(result)
# Expected: Complete biomechanics summary with all joints and asymmetries
```

---

## Troubleshooting

### Issue: Tests fail with ModuleNotFoundError
**Solution**:
```bash
cd backend
pip install -r requirements.txt  # or pip install fastapi uvicorn etc.
python tests/test_biomechanics_service.py
```

### Issue: Dashboard not showing in browser
**Solution**:
1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh page (Ctrl+Shift+R)
3. Check dev server is running: `npm run dev`
4. Look for errors in browser console (F12)

### Issue: Video upload fails after changes
**Solution**:
1. Verify routes.py imports aggregate_biomechanics
2. Check that biomechanics_service.py has all new functions
3. Look at backend error logs for specific error message
4. Run tests to isolate issue: `python tests/test_biomechanics_service.py`

### Issue: biomechanics_summary missing from response
**Solution**:
1. Verify routes.py has this line:
   ```python
   biomechanics_summary = aggregate_biomechanics(biomechanics_frames)
   analysis["biomechanics_summary"] = biomechanics_summary
   ```
2. Check that biomechanics_frames is populated correctly
3. Add debug logging to see data flow
4. Run integration test with sample video

---

## Performance Notes

- **Small videos** (< 30 sec): Analysis < 2 seconds
- **Medium videos** (30-90 sec): Analysis 2-10 seconds
- **Large videos** (> 90 sec): Analysis 10+ seconds

If analysis is very slow:
- Check CPU usage (may need system resources)
- Consider frame sampling for long videos
- Check network latency if using remote backend

---

## Success Criteria

You'll know everything is working correctly when:

✅ All 25 tests pass  
✅ No compilation errors  
✅ Dashboard displays with mock data  
✅ Video upload still works  
✅ Video analysis includes biomechanics_summary  
✅ All UI panels responsive on different screen sizes  
✅ Navigation between tabs works smoothly  
✅ No console errors in browser DevTools  

---

## Next Actions (When Ready)

1. **Connect Dashboard to Real Data**:
   - Replace mockDashboardData with API calls
   - Parse biomechanics_summary from video analysis response
   - Display real metrics instead of mock values

2. **Enhance Biomechanical Analysis**:
   - Use biomechanics_summary in performance calculation
   - Add more joint metrics (stride, speed, etc.)
   - Implement machine learning model for injury risk

3. **Deploy to Production**:
   - Update backend with new service
   - Test with live video data
   - Monitor performance metrics
   - Gather user feedback

---

## Files Reference

**Frontend**:
- src/main.jsx - PS-02 Dashboard component
- src/styles.css - Dashboard styling

**Backend**:
- backend/app/services/biomechanics_service.py - New functions
- backend/app/api/routes.py - Integration point
- backend/tests/test_biomechanics_service.py - Test suite

**Documentation**:
- IMPLEMENTATION_SUMMARY.md - Complete overview
- LOCAL_TESTING_GUIDE.md - This file
