import os
import discord
from discord.ext import commands, tasks
from vinted import search_vinted

TOKEN = os.getenv("TOKEN")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

watched_searches = []
seen_items = set()


@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")

    if not deal_watcher.is_running():
        deal_watcher.start()


@bot.command()
async def ping(ctx):
    await ctx.send("Pong !")


@bot.command()
async def search(ctx, *, query):

    await ctx.send(f"Recherche de : {query}")

    results = await search_vinted(query)

    if not results:
        await ctx.send("Aucun résultat.")
        return

    prices = []

    for item in results:

        try:

            price_text = (
                item["price"]
                .replace("€", "")
                .replace(",", ".")
                .strip()
            )

            price_text = "".join(
                c for c in price_text
                if c.isdigit() or c == "."
            )

            numeric_price = float(price_text)

            prices.append(numeric_price)

        except:
            continue

    if not prices:
        await ctx.send("Impossible de calculer les prix.")
        return

    average_price = sum(prices) / len(prices)

    scored_results = []

    for item in results:

        try:

            price_text = (
                item["price"]
                .replace("€", "")
                .replace(",", ".")
                .strip()
            )

            price_text = "".join(
                c for c in price_text
                if c.isdigit() or c == "."
            )

            numeric_price = float(price_text)

            profit = average_price - numeric_price

            score = (
                (profit / average_price) * 10
            )

            scored_results.append({
                "item": item,
                "score": score,
                "profit": profit
            })

        except:
            continue

    scored_results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    for result in scored_results:

        item = result["item"]

        message = (
            f"🔥 {item['title']}\n"
            f"💰 {item['price']}\n"
            f"📈 Prix moyen : {round(average_price, 2)}€\n"
            f"💸 Profit estimé : +{round(result['profit'],2)}€\n"
            f"⭐ Deal Score : {round(result['score'],1)}/10\n"
            f"🔗 {item['url']}"
        )

        await ctx.send(message)


@bot.command()
async def watch(ctx, *, query):

    watched_searches.append({
        "channel": ctx.channel,
        "query": query
    })

    await ctx.send(f"🔍 Surveillance activée pour : {query}")


@tasks.loop(minutes=2)
async def deal_watcher():

    for watch in watched_searches:

        query = watch["query"]
        channel = watch["channel"]

        results = await search_vinted(query)

        if not results:
            continue

        prices = []

        for item in results:

            try:

                price_text = (
                    item["price"]
                    .replace("€", "")
                    .replace(",", ".")
                    .strip()
                )

                price_text = "".join(
                    c for c in price_text
                    if c.isdigit() or c == "."
                )

                numeric_price = float(price_text)

                prices.append(numeric_price)

            except:
                continue

        if not prices:
            continue

        average_price = sum(prices) / len(prices)

        for item in results:

            try:

                price_text = (
                    item["price"]
                    .replace("€", "")
                    .replace(",", ".")
                    .strip()
                )

                price_text = "".join(
                    c for c in price_text
                    if c.isdigit() or c == "."
                )

                numeric_price = float(price_text)

                profit = average_price - numeric_price

                score = (
                    (profit / average_price) * 10
                )

                if score >= 3:

                    if item["url"] not in seen_items:

                        seen_items.add(item["url"])

                        await channel.send(
                            f"🚨 DEAL DETECTÉ\n\n"
                            f"🔥 {item['title']}\n"
                            f"💰 {item['price']}\n"
                            f"📈 Prix moyen : {round(average_price,2)}€\n"
                            f"💸 Profit estimé : +{round(profit,2)}€\n"
                            f"⭐ Score : {round(score,1)}/10\n"
                            f"🔗 {item['url']}"
                        )

            except:
                continue


bot.run(TOKEN)