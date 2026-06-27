# File History UI - Visual Layout

## Home Page Structure

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🔒 SecureVault                  Welcome Back! 👋                            │
│                                 Secure your files with advanced encryption   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│ 📁 Total Files: 5    🔐 Encrypted: AES-256   🛡️ Security: Protected   ⭐ 4 Active│
│                                                                              │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ 📷 CARRIER FILES                                                        │ │
│ │ Secure files embedded within carrier images using advanced steganography│ │
│ │                                                                         │ │
│ │  [Card1]   [Card2]   [Card3]   [Card4]                                 │ │
│ │  [Card5]   [Card6]   [Card7]                                           │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│ ┌─────────────────────────────────────────────────────────────────────────┐ │
│ │ 📋 FILE HISTORY                                                         │ │
│ │ Complete audit trail of all encrypted files with timestamps and status  │ │
│ │                                                                         │ │
│ │ ┌─────────────────────────────────────────────────────────────────────┐ │
│ │ │ 📅 Date & Time     │ 📄 File Name     │ 🔐 Encryption│ 👁️ Cam│✓ Stat│ │
│ │ ├─────────────────────────────────────────────────────────────────────┤ │
│ │ │ 2025-12-08 14:30  │ 📊 report.xlsx   │ 🔐 AES-256  │ ✓ Yes   │ ✓Secure│ │
│ │ │ Dec 08, 2025      │                  │             │         │        │ │
│ │ ├─────────────────────────────────────────────────────────────────────┤ │
│ │ │ 2025-12-08 13:15  │ 📷 vacation.jpg  │ 🔐 AES-256  │ ✗ No    │ ✓Secure│ │
│ │ │ Dec 08, 2025      │                  │             │         │        │ │
│ │ ├─────────────────────────────────────────────────────────────────────┤ │
│ │ │ 2025-12-07 09:45  │ 📄 contract.pdf  │ 🔐 AES-256  │ ✓ Yes   │ ✓Secure│ │
│ │ │ Dec 07, 2025      │                  │             │         │        │ │
│ │ ├─────────────────────────────────────────────────────────────────────┤ │
│ │ │ 2025-12-05 16:20  │ 🎵 audio.mp3     │ 🔐 AES-256  │ ✓ Yes   │ ✓Secure│ │
│ │ │ Dec 05, 2025      │                  │             │         │        │ │
│ │ ├─────────────────────────────────────────────────────────────────────┤ │
│ │ │ 2025-12-01 11:30  │ 📦 archive.zip   │ 🔐 AES-256  │ ✗ No    │ ✓Secure│ │
│ │ │ Dec 01, 2025      │                  │             │         │        │ │
│ │ └─────────────────────────────────────────────────────────────────────┘ │
│ │                                                        [Scrollbar ▼]     │ │
│ └─────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## File History Table - Detailed View

### Header Row (Background: #f3f4f6)
```
┌───────────────────────┬──────────────────────────┬─────────────────┬──────────────┬────────────┐
│ 📅 Date & Time        │ 📄 File Name             │ 🔐 Encryption   │ 👁️ Camouflage│ ✓ Status  │
│ (Bold, 10pt)          │ (Bold, 10pt)             │ (Bold, 10pt)    │ (Bold, 10pt) │ (Bold, 10pt)
│ #374151 on #f3f4f6    │ #374151 on #f3f4f6       │ #374151 on #f3f4f6 │ #374151  │ #374151   │
└───────────────────────┴──────────────────────────┴─────────────────┴──────────────┴────────────┘
```

### Data Row - Even (Background: #ffffff)
```
┌───────────────────────────────────────────────────────────────────────────────────────────────┐
│ 2025-12-08 14:30:45  │ 📊 quarterly_report.xlsx │ 🔐 AES-256     │ ✓ Yes       │ ✓ Secure   │
│ Dec 08, 2025         │ (Segoe UI, 9pt)          │ (Green #10b981) │ (Green)     │ (Cyan)     │
│ (Segoe UI, 9pt)      │ #1f2937 on #ffffff       │ (Segoe UI, 9pt) │ (Segoe UI)  │ (Segoe UI) │
│ #1f2937 on #ffffff   │                          │                 │ #10b981     │ #06b6d4    │
│                      │                          │                 │             │            │
│ Secondary:           │                          │                 │             │            │
│ Dec 08, 2025         │                          │                 │             │            │
│ (Segoe UI, 8pt)      │                          │                 │             │            │
│ #9ca3af on #ffffff   │                          │                 │             │            │
└───────────────────────────────────────────────────────────────────────────────────────────────┘
Height: 60px, Padding: 20px horizontal, 12px vertical
Spacing: 10px between columns
```

### Data Row - Odd (Background: #f9fafb)
```
┌───────────────────────────────────────────────────────────────────────────────────────────────┐
│ 2025-12-07 09:45:20  │ 📷 vacation_photos.jpg   │ 🔐 AES-256     │ ✗ No        │ ✓ Secure   │
│ Dec 07, 2025         │ (Segoe UI, 9pt)          │ (Green #10b981) │ (Red)       │ (Cyan)     │
│ (Segoe UI, 9pt)      │ #1f2937 on #f9fafb       │ (Segoe UI, 9pt) │ (Segoe UI)  │ (Segoe UI) │
│ #1f2937 on #f9fafb   │                          │                 │ #ef4444     │ #06b6d4    │
└───────────────────────────────────────────────────────────────────────────────────────────────┘
```

## Color Scheme

```
Primary Background:     #f5f7fb (Light blue-gray)
Card Background:        #ffffff (White)
Alternate Row:          #f9fafb (Very light gray)
Header Background:      #f3f4f6 (Light gray)
Border Color:           #e5e7eb (Light border)

Text - Primary:         #1f2937 (Dark gray)
Text - Secondary:       #6b7280 (Medium gray)
Text - Tertiary:        #9ca3af (Light gray)
Text - Placeholder:     #d1d5db (Very light gray)

Encryption Status:      #10b981 (Green - AES-256)
Camouflage Yes:         #10b981 (Green)
Camouflage No:          #ef4444 (Red)
Status/Secure:          #06b6d4 (Cyan)
```

## File Type Icons

```
Documents:    📄  PDF, DOC, DOCX, TXT
Spreadsheets: 📊  XLSX, CSV
Images:       📷  JPG, JPEG, PNG, GIF, BMP
Videos:       🎥  MP4, AVI, MOV, MKV
Audio:        🎵  MP3, WAV, FLAC, AAC
Archives:     📦  ZIP, RAR, 7Z, TAR
Software:     ⚙️  EXE, MSI, APP
Web:          🌐  HTML, CSS, JS
Python:       🐍  PY
Default:      📄  (Any other type)
```

## Empty State

```
┌─────────────────────────────────────────────────────────────────┐
│                                                                 │
│                   No files stored yet                           │
│               (Segoe UI, 11pt, #9ca3af)                        │
│                                                                 │
│          Upload files to see them in the history               │
│           (Segoe UI, 9pt, #d1d5db)                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Responsive Features

✅ **Scrollbar**: Appears when content exceeds height (300px default)
✅ **Mousewheel**: Scroll up/down with mouse wheel
✅ **Alternating Rows**: Easy to scan and read
✅ **Proportional Columns**: Fixed width distribution across table
✅ **Row Highlighting**: Subtle background color change
✅ **Date Formatting**: Automatic conversion from ISO format

## Accessibility

- High contrast text (#1f2937 on #ffffff/#f9fafb)
- Clear emoji indicators for quick status scanning
- Color-coded camouflage status (red/green)
- Logical column order: Date → Name → Security → Camouflage → Status
- Font sizing appropriate for readability
