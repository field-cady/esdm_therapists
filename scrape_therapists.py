import asyncio
import csv
from playwright.async_api import async_playwright

async def scrape_esdm_therapists():
    url = "https://www.esdm.co/esdm-therapists"
    print(f"Navigating to {url}...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Go to the page and wait for it to load
        await page.goto(url, wait_until="networkidle")
        
        print("Waiting for Table Master to load...")
        # Increase the timeout to ensure the table content is loaded
        await page.wait_for_timeout(10000)
        
        try:
            # Look for the frame with "Table Master" in its title
            frame = None
            for f in page.frames:
                try:
                    title = await f.title()
                    if "Table Master" in title:
                        frame = f
                        break
                except:
                    continue
            
            if not frame:
                print("Could not find Table Master iframe.")
                return
            
            print(f"Found Table Master iframe. Extracting table data...")
            
            # Find the table with the most rows
            tables = await frame.query_selector_all('table')
            if not tables:
                print("No tables found in the iframe.")
                return
            
            # Find the one with most rows
            target_table = None
            max_rows = -1
            for t in tables:
                rows = await t.query_selector_all('tr')
                if len(rows) > max_rows:
                    max_rows = len(rows)
                    target_table = t
            
            if not target_table:
                print("Could not find target table.")
                return
            
            print(f"Found target table with {max_rows} rows.")
            
            # Extract headers from the first row of this table
            header_elements = await target_table.query_selector_all('tr:first-child th')
            if not header_elements:
                 header_elements = await target_table.query_selector_all('tr:first-child td')
                 
            headers = [await el.inner_text() for el in header_elements]
            headers = [h.strip() for h in headers]
            
            print(f"Found headers: {headers}")
            
            # Extract all rows
            row_elements = await target_table.query_selector_all('tr')
            data_rows = []
            for i, row in enumerate(row_elements):
                # Skip header row if necessary
                cells = await row.query_selector_all('td')
                if not cells:
                    cells = await row.query_selector_all('th')
                
                row_data = [await cell.inner_text() for cell in cells]
                row_data = [r.strip() for r in row_data]
                
                if any(row_data) and row_data != headers:
                    data_rows.append(row_data)
                    
            print(f"Extracted {len(data_rows)} rows.")
            
            # Save to data.tsv
            with open('data.tsv', 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter='\t')
                writer.writerow(headers)
                writer.writerows(data_rows)
            
            print("Successfully saved data to data.tsv")
            
        except Exception as e:
            print(f"An error occurred: {e}")
            await page.screenshot(path="error_screenshot.png")
            print("Screenshot saved as error_screenshot.png")
            
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_esdm_therapists())
