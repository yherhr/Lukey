#!/usr/bin/env python3
"""
Luke Davis Mechanical — Price Updater
======================================
How to use:
  1. Open prices.csv in Excel, Google Sheets, or any spreadsheet app
  2. Edit the 'price' column for any products you want to change
  3. Change 'from_price' to 'yes' or 'no' as needed
  4. Save the CSV file
  5. Run this script:  python3 update-prices.py

The script will update EVERY part-*.html file with the new prices.
It will NOT change anything else — only the price display.

Files it reads:  prices.csv  (must be in the same folder)
Files it writes: part-{id}.html  (one per product, same folder)

Column guide:
  id          - Don't edit this (used to match product to HTML file)
  name        - Product name (for reference, not used by script)
  sku         - Stock keeping unit (for reference)
  category    - Category label (for reference)
  price       - Price in AUD cents-free integer, e.g. 1450 = $1,450
  from_price  - 'yes' means show "From $X,XXX" / 'no' means show "$X,XXX"
  currency    - Always AUD (for reference)
  notes       - Any notes you want to keep (not used by script)
"""

import csv, re, os, sys

PRICES_FILE = 'prices.csv'
PARTS_FOLDER = '.'  # Change if your HTML files are in a subfolder

def fmt_price(n):
    return '${:,}'.format(int(n))

def update_file(filepath, price, from_price):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    new_price_html = fmt_price(price)
    
    # Update the price value between markers
    new_html, count = re.subn(
        r'<!-- PRICE_START -->.*?<!-- PRICE_END -->',
        f'<!-- PRICE_START --><div class="price-val">{new_price_html}</div><!-- PRICE_END -->',
        html, flags=re.DOTALL
    )
    
    if count == 0:
        print(f'  ⚠️  No price marker found in {filepath}')
        return False

    # Update "From" label visibility
    if from_price:
        # Make sure from label is present
        if '<span class="price-from">From</span>' not in new_html:
            new_html = new_html.replace(
                '<!-- PRICE_START -->',
                '<span class="price-from">From</span>\n      <!-- PRICE_START -->'
            )
    else:
        # Remove "From" label if present
        new_html = re.sub(
            r'\n?\s*<span class="price-from">From</span>\n?\s*',
            '\n      ',
            new_html
        )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_html)
    return True


def main():
    if not os.path.exists(PRICES_FILE):
        print(f'❌ Cannot find {PRICES_FILE}')
        print('   Make sure prices.csv is in the same folder as this script.')
        sys.exit(1)

    updated, skipped, errors = 0, 0, 0

    with open(PRICES_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f'Reading {PRICES_FILE}: {len(rows)} products found')
    print('─' * 50)

    for row in rows:
        pid = row.get('id', '').strip()
        if not pid:
            continue

        filepath = os.path.join(PARTS_FOLDER, f'part-{pid}.html')

        if not os.path.exists(filepath):
            print(f'  ⚠️  Skipping — file not found: {filepath}')
            skipped += 1
            continue

        try:
            price = int(str(row['price']).replace(',', '').replace('$', '').strip())
            from_price = row.get('from_price', 'no').strip().lower() == 'yes'
        except (ValueError, KeyError) as e:
            print(f'  ❌ Bad price for {pid}: {e}')
            errors += 1
            continue

        success = update_file(filepath, price, from_price)
        if success:
            from_str = 'From ' if from_price else '     '
            print(f'  ✅ {pid[:55]:<55} {from_str}{fmt_price(price)}')
            updated += 1
        else:
            errors += 1

    print('─' * 50)
    print(f'Done: {updated} updated  |  {skipped} skipped  |  {errors} errors')


if __name__ == '__main__':
    main()
