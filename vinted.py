from playwright.async_api import async_playwright

async def search_vinted(query):

    results = []

    async with async_playwright() as p:

        browser = await p.chromium.launch(headless=True)

        page = await browser.new_page()

        url = f"https://www.vinted.fr/catalog?search_text={query}&localization_id=5"

        await page.goto(url)

        await page.wait_for_timeout(5000)

        cards = await page.locator('[data-testid="grid-item"]').all()

        for card in cards[:10]:

            try:

                title = "Produit"

                img = card.locator("img")

                if await img.count() > 0:

                    alt = await img.first.get_attribute("alt")

                    if alt:
                        title = alt

                link = card.locator("a").first

                href = await link.get_attribute("href")

                if not href:
                    continue

                if "/items/" not in href:
                    continue

                full_url = href

                if not href.startswith("http"):
                    full_url = "https://www.vinted.fr" + href

                text = await card.inner_text()

                lines = text.split("\n")

                price = None

                for line in lines:

                    line = line.strip()

                    if "€" in line:

                        price = line
                        break

                if not price:
                    continue

                results.append({
                    "title": title,
                    "price": price,
                    "currency": "€",
                    "url": full_url
                })

            except:
                continue

        await browser.close()

    return results