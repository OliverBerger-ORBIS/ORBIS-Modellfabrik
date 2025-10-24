# Screenshot Verification Guide - Product SVG Standardization

## Purpose
This guide provides step-by-step instructions for taking screenshots to verify the product SVG standardization implementation (200×200px).

## Prerequisites
- OMF Dashboard running locally
- Access to CCU Overview tabs
- Products (BLUE, WHITE, RED) loaded in the system

## Required Screenshots

### 1. Product Catalog Tab

**Navigation:** CCU Overview → Product Catalog

**What to Capture:**
- All three products (BLUE, WHITE, RED) displayed
- Both 3DIM SVG and Product SVG for each product
- Verify all SVGs are in 200×200 containers

**Expected Result:**
- Products arranged in 3 columns
- Each product shows 2 SVGs (3DIM and Product)
- All containers are visually uniform in size
- Border around each SVG is 1px solid #ccc

**Screenshot Filename:** `screenshot_01_product_catalog.png`

**Verification Checklist:**
- [ ] All 3 products (BLUE, WHITE, RED) visible
- [ ] 6 total SVGs displayed (3 products × 2 variants each)
- [ ] All SVG containers appear same size (200×200px)
- [ ] Borders are consistent
- [ ] Product names are displayed below each section

---

### 2. Customer Order Tab

**Navigation:** CCU Overview → Customer Order

**What to Capture:**
- All three customer order options (BLUE, WHITE, RED)
- Product SVG for each workpiece type
- Order buttons and availability status

**Expected Result:**
- 3 columns layout
- Each column shows a product SVG at 200×200
- Stock count and availability displayed
- Order buttons visible (enabled/disabled based on stock)

**Screenshot Filename:** `screenshot_02_customer_order.png`

**Verification Checklist:**
- [ ] All 3 products (BLUE, WHITE, RED) visible
- [ ] Product SVGs are same size across all columns
- [ ] Stock information displayed correctly
- [ ] Order buttons present
- [ ] Layout is balanced and aligned

---

### 3. Purchase Order Tab

**Navigation:** CCU Overview → Purchase Order

**What to Capture:**
- All three workpiece types (BLUE, WHITE, RED)
- UNPROCESSED SVG for each type at 200×200
- Palett SVGs (if any shortage exists)
- Need indicators and order buttons

**Expected Result:**
- Each workpiece section shows UNPROCESSED SVG at 200×200
- Palett SVGs (if displayed) are also 200×200
- Stock and need information visible
- Order buttons present

**Screenshot Filename:** `screenshot_03_purchase_order.png`

**Verification Checklist:**
- [ ] UNPROCESSED SVGs for all 3 types visible
- [ ] All SVGs are uniform 200×200 size
- [ ] Palett SVGs (if shown) are also 200×200
- [ ] Need calculation displayed correctly
- [ ] Layout is clean and organized

---

### 4. Inventory Tab (3×3 Warehouse Grid)

**Navigation:** CCU Overview → Inventory

**What to Capture:**
- The "Lager - Ohne Manipulation (AS-IS)" section
- Full 3×3 grid (positions A1-C3)
- Mix of empty positions (palett) and filled positions (workpieces)

**Expected Result:**
- Clear 3×3 grid structure
- 9 total cells visible
- Each cell is 200×200px
- Empty cells show palett SVG
- Filled cells show workpiece SVG
- Position labels visible (A1, A2, A3, B1, B2, B3, C1, C2, C3)

**Screenshot Filename:** `screenshot_04_inventory_grid.png`

**Verification Checklist:**
- [ ] All 9 grid positions visible (A1-C3)
- [ ] Grid maintains 3×3 structure
- [ ] All cells appear same size (200×200px)
- [ ] Position labels clearly visible
- [ ] Empty vs. filled positions distinguishable
- [ ] Grid is properly aligned

---

## How to Take Screenshots

### Option 1: Full Page Screenshot (Recommended)
1. Navigate to the tab
2. Ensure full content is visible (scroll if necessary)
3. Use browser screenshot tool or:
   - **Chrome/Edge:** F12 → Cmd+Shift+P → "Capture screenshot"
   - **Firefox:** F12 → Three dots menu → "Take a screenshot"

### Option 2: Manual Screenshot
1. Navigate to the tab
2. Press `Print Screen` (Windows) or `Cmd+Shift+4` (Mac)
3. Crop to show relevant content

### Option 3: Browser Extension
Use a screenshot extension like:
- Awesome Screenshot
- Nimbus Screenshot
- Fireshot

## Screenshot Quality Guidelines

- **Resolution:** Minimum 1920×1080
- **Format:** PNG (preferred) or JPG
- **Content:** Include all relevant UI elements
- **No Obstructions:** No overlays, popups, or dev tools visible
- **Good Lighting:** Use light theme if available for clarity
- **Clear Labels:** Ensure text is readable

## Verification Steps

For each screenshot, verify:

1. **Size Consistency:** All product SVGs appear same size
2. **Grid Structure:** Inventory tab shows proper 3×3 layout
3. **Borders:** Consistent 1px borders around containers
4. **Alignment:** Products are centered within containers
5. **Labels:** All position/product labels are visible
6. **Layout:** No visual breaks or misalignments

## Expected Dimensions Reference

| Element | Size | Notes |
|---------|------|-------|
| Product SVG Container | 200×200px | Square container |
| Warehouse Cell | 200×200px | Same as product container |
| Warehouse Grid | 3×3 | Fixed layout |
| Border | 1px | Solid #ccc color |
| Padding | 10px | Inside container |
| Margin | 5px | Between containers |

## Troubleshooting

### SVGs appear different sizes
- Check browser zoom is at 100%
- Verify cache is cleared
- Reload the page

### Grid not showing 3×3
- Scroll to ensure full grid is visible
- Check browser window is wide enough
- Verify data is loaded (check for "Waiting for stock" message)

### Images not loading
- Check asset manager is initialized
- Verify SVG files exist in `omf2/assets/workpiece/`
- Check browser console for errors

## Attaching Screenshots to PR

Once all screenshots are taken:

1. Create a directory: `docs/screenshots/product_svg_standardization/`
2. Place all 4 screenshots in this directory
3. Use the exact filenames specified above
4. Add to git: `git add docs/screenshots/`
5. Commit: `git commit -m "docs: Add verification screenshots for product SVG standardization"`
6. Reference in PR description

## PR Description Template

```markdown
## Screenshots

### Product Catalog
![Product Catalog](docs/screenshots/product_svg_standardization/screenshot_01_product_catalog.png)

### Customer Order
![Customer Order](docs/screenshots/product_svg_standardization/screenshot_02_customer_order.png)

### Purchase Order
![Purchase Order](docs/screenshots/product_svg_standardization/screenshot_03_purchase_order.png)

### Inventory (3×3 Grid)
![Inventory Grid](docs/screenshots/product_svg_standardization/screenshot_04_inventory_grid.png)
```

## Questions?

If you encounter any issues or have questions about the screenshot requirements, please:
1. Check the implementation in the respective subtab files
2. Review the test suite at `tests/test_omf2/test_ui/test_product_svg_size.py`
3. Consult the main documentation at `docs/product_svg_standardization.md`
