# File History Feature - Testing Guide

## Quick Start

1. **Run the Application**
   ```bash
   cd c:\Project\Finalbackup
   python main.py
   ```

2. **Create Master Password** (First time only)
   - Set a secure master password when prompted
   - Complete keystroke authentication enrollment

3. **Login**
   - Enter master password
   - Authenticate with keystroke dynamics (or skip if not enrolled)

## Testing Scenarios

### Scenario 1: Empty History (No Files)
**Expected Behavior:**
- File History section displays after Carrier Files section
- Shows "No files stored yet" message
- Shows helpful hint: "Upload files to see them in the history"
- Empty state properly centered

**Steps:**
1. Fresh application startup (no files stored)
2. Navigate to Home page
3. Scroll down to File History section
4. Verify empty state display

---

### Scenario 2: Single File in History
**Expected Behavior:**
- File History table shows table header with 5 columns
- One data row appears with file information
- Row has white background (#ffffff)
- All columns properly populated

**Steps:**
1. Upload a file:
   - Click "📤 Upload" in sidebar
   - Select any file (e.g., test.txt)
   - Set encryption password
   - Click "Encrypt & Store"
   
2. Return to Home
3. Scroll down to File History
4. Verify file appears with:
   - **Date & Time**: Current date/time in YYYY-MM-DD HH:MM:SS format + readable date
   - **File Name**: Original filename with correct icon
   - **Encryption**: "🔐 AES-256"
   - **Camouflage**: "✓ Yes" (green) or "✗ No" (red) based on storage settings
   - **Status**: "✓ Secure" in cyan

---

### Scenario 3: Multiple Files (5+) in History
**Expected Behavior:**
- Multiple rows appear with alternating colors
- Even rows: #ffffff (white)
- Odd rows: #f9fafb (light gray)
- Scrollbar appears if rows exceed view height
- All rows properly formatted

**Steps:**
1. Upload 5-10 different file types:
   - Text file (.txt, .doc)
   - Image (.jpg, .png)
   - PDF document
   - Spreadsheet (.xlsx)
   - Archive (.zip)

2. For each file, try both options:
   - With camouflage enabled
   - Without camouflage

3. Return to Home → File History
4. Verify:
   - Correct file type icons display
   - Alternating row colors
   - Camouflage status shows correctly
   - All dates are recent (today's date)

---

### Scenario 4: File Icons Display
**Expected Behavior:**
- Each file type shows appropriate emoji icon
- Icons align with file extension

**Test Files and Expected Icons:**
| File Name | Expected Icon | Type |
|-----------|---------------|------|
| document.pdf | 📄 | Document |
| report.xlsx | 📊 | Spreadsheet |
| photo.jpg | 📷 | Image |
| video.mp4 | 🎥 | Video |
| song.mp3 | 🎵 | Audio |
| data.zip | 📦 | Archive |
| script.py | 🐍 | Python |
| index.html | 🌐 | Web |
| app.exe | ⚙️ | Software |
| unknown.xyz | 📄 | Default |

**Steps:**
1. Upload files with these extensions
2. Verify correct icons display in File History

---

### Scenario 5: Camouflage Status Indication
**Expected Behavior:**
- Files stored with camouflage → "✓ Yes" (Green)
- Files stored without camouflage → "✗ No" (Red)
- Status properly color-coded

**Steps:**
1. Upload file with camouflage:
   - Enable "File Camouflage" option
   - Store file
   
2. Upload file without camouflage:
   - Disable "File Camouflage" option
   - Store file

3. Check File History:
   - First file: Green "✓ Yes"
   - Second file: Red "✗ No"

---

### Scenario 6: Date/Time Formatting
**Expected Behavior:**
- Timestamp formatted as: YYYY-MM-DD HH:MM:SS
- Readable date shown as: MMM DD, YYYY
- Both displayed correctly

**Steps:**
1. Upload file at specific time (e.g., 14:30:45)
2. Check File History
3. Verify timestamp shows:
   - Line 1: "2025-12-08 14:30:45"
   - Line 2: "Dec 08, 2025"

---

### Scenario 7: Table Scrolling
**Expected Behavior:**
- Scrollbar appears when many files stored
- Mousewheel scrolling works
- Arrow keys work (Up/Down)

**Steps:**
1. Upload 15-20 files
2. In File History section:
   - Use mousewheel to scroll
   - Press Up/Down arrow keys
   - Use scrollbar thumb
3. Verify smooth scrolling
4. Verify all rows accessible

---

### Scenario 8: Column Widths and Layout
**Expected Behavior:**
- Columns maintain proper proportions:
  - Date: ~20% width
  - Name: ~35% width
  - Encryption: ~15% width
  - Camouflage: ~15% width
  - Status: ~15% width
- All columns visible without horizontal scroll
- Text doesn't overflow

**Steps:**
1. Upload files with:
   - Short names (e.g., "a.txt")
   - Long names (e.g., "very_long_filename_for_testing_purposes.pdf")
   
2. Verify:
   - All text visible
   - No overflow
   - Columns properly proportioned

---

### Scenario 9: Header Row Display
**Expected Behavior:**
- Header row has distinct styling:
  - Background: Light gray (#f3f4f6)
  - Text: Bold, darker color (#374151)
  - Emoji icons for each column
  - Fixed height (50px)

**Steps:**
1. Navigate to File History
2. Verify header shows:
   - "📅 Date & Time"
   - "📄 File Name"
   - "🔐 Encryption"
   - "👁️ Camouflage"
   - "✓ Status"

---

### Scenario 10: Row Interaction
**Expected Behavior:**
- Rows are clickable (future enhancement)
- Hover effects show row is interactive
- Clear visual feedback

**Steps:**
1. Hover over different rows
2. Verify visual feedback (color change)
3. Click a row (if click handler implemented)

---

## Manual Verification Checklist

- [ ] File History section appears on home page
- [ ] Section title "📋 File History" displays correctly
- [ ] Subtitle text shows correctly
- [ ] Table header displays all 5 columns
- [ ] Header has light gray background
- [ ] Data rows alternate colors (white/light gray)
- [ ] File type icons display correctly
- [ ] Dates formatted correctly (YYYY-MM-DD + readable)
- [ ] Encryption status shows "🔐 AES-256" in green
- [ ] Camouflage status shows correctly with color coding
- [ ] Security status shows "✓ Secure" in cyan
- [ ] Scrollbar appears for many files
- [ ] Mousewheel scrolling works
- [ ] Arrow key scrolling works (Up/Down)
- [ ] Empty state shows when no files
- [ ] All text readable without overflow
- [ ] Spacing and padding correct
- [ ] Color contrast meets accessibility standards
- [ ] No console errors or exceptions

---

## Troubleshooting

### Issue: File History section not visible
**Solution:**
- Scroll down to find it (below Carrier Files section)
- Verify files are actually stored (check metadata folder)
- Check console for errors

### Issue: Dates showing "N/A"
**Solution:**
- Check file metadata JSON has `encrypted_at` field
- Verify ISO format is correct
- Check date parsing in code (line ~2770)

### Issue: Icons not displaying
**Solution:**
- Verify file extension is in icon_map dictionary
- Check if extension is lowercase
- Default icon (📄) should display for unknown types

### Issue: Camouflage status wrong
**Solution:**
- Verify file metadata has `camouflaged` field set correctly
- Check storage path in metadata
- Verify camouflage manager properly set flag

### Issue: Scrollbar not appearing
**Solution:**
- Verify height exceeds 300px threshold
- Check if many files exist
- Verify scrollbar configuration in code

### Issue: Text overflow
**Solution:**
- Reduce font size (currently 9pt)
- Truncate long filenames with ellipsis
- Adjust column widths

---

## Performance Notes

- Scrollable canvas loads all files (suitable for < 1000 files)
- For very large lists, implement pagination or lazy loading
- Current implementation tested with up to 50 files successfully

---

## Future Testing

Once implemented, test:
- [ ] Sort by date (ascending/descending)
- [ ] Sort by file name (A-Z)
- [ ] Filter by file type
- [ ] Filter by camouflage status
- [ ] Search functionality
- [ ] Delete from history row
- [ ] Export history as CSV/PDF
- [ ] Context menu on right-click
- [ ] Double-click to open file info
