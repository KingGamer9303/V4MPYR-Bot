import os
import discord
import asyncio

from datetime import datetime, time
import pytz

from discord.ext import commands
from dotenv import load_dotenv

from database.database import (
    setup_database,
    set_blood_moon,
    get_all_leaderboards,
    get_blood_leaderboard,
    get_level_leaderboard,
    get_message_leaderboard,
    get_stolen_leaderboard,
    process_overdue_loans,
)


BLOOD_MOON_CHANNEL_ID = 1530402841250889818
BLOOD_MOON_ROLE_ID = 1531183886430769243


BLOOD_BANNER = "https://cdn.discordapp.com/attachments/1530395730387140718/1531536170322886816/thearcanewitch.jpg?ex=6a6991b5&is=6a684035&hm=86cf3e1c8104b3ad34931b5a426356ea4c2ad3e2b51d13fe803a6e6a69eb7ec6&"
LEVEL_BANNER = "https://cdn.discordapp.com/attachments/1530395730387140718/1531536122122080357/104427285106163435.jpg?ex=6a6991aa&is=6a68402a&hm=ef97bd3b9b1573915ed0a1206e9a7078e67a1bf25e5460aae4e53485b811fb2a&"
MESSAGE_BANNER = "https://cdn.discordapp.com/attachments/1530395730387140718/1531536251898036334/header_dark_red_.jpg?ex=6a6991c9&is=6a684049&hm=1010bf3c4c04ed4605a0f59bc472b3290848dbf4718782646739ad2508e2f7f4&"
STOLEN_BANNER = "https://cdn.discordapp.com/attachments/1530395730387140718/1531536216405708982/header_red_white_red_black_vampire_aesthetic.jpg?ex=6a6991c0&is=6a684040&hm=42e7debf6619fa451bdfdaf5bb745270f0378dc47610a0b0fa4210a4d7851846&"

BLOOD_MOON_GIF = "https://cdn.discordapp.com/attachments/1530395730387140718/1531539492421505144/pobierz_3.gif?ex=6a6994cd&is=6a68434d&hm=5a2116a4056111d3f0ebca122fd3d22f8c7b5eb8fa1114c261d7cf15ddad964e&"



load_dotenv()

TOKEN = os.getenv("TOKEN")

if not TOKEN:
    raise ValueError("❌ TOKEN not found in .env file!")


intents = discord.Intents.default()
intents.message_content = True
intents.members = True



class V4MPYR(commands.Bot):

    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

        self.blood_moon_active = False



    async def blood_moon_scheduler(self):

        tz = pytz.timezone("Asia/Kolkata")

        await self.wait_until_ready()

        while True:

            now = datetime.now(tz).time()

            # TEST TIME
            # Change to:
            # start = time(20,0)
            # end = time(22,0)
            # for real event

            start = time(20, 0)
            end = time(22, 0)


            channel = self.get_channel(
                BLOOD_MOON_CHANNEL_ID
            )


            if start <= now < end:

                await set_blood_moon(True)


                if not self.blood_moon_active:

                    self.blood_moon_active = True

                    print("🌕 Blood Moon ACTIVE")


                    if channel:

                        embed = discord.Embed(
                            title="🌕 THE BLOOD MOON HAS RISEN",
                            description=(
                                "🩸 **The crimson moon awakens...**\n"
                                "The night belongs to the vampires.\n\n"

                                "━━━━━━━━━━━━━━━━━━\n\n"

                                "⚔️ **Hunt Mode:** Unleashed\n"
                                "🩸 **Blood Gain:** ×2 Rewards\n"
                                "⭐ **XP Gain:** Increased\n"
                                "⏳ **Cooldown:** Disabled\n"
                                "🛡️ **Protection:** Broken\n\n"

                                "━━━━━━━━━━━━━━━━━━\n\n"

                                "🌑 The weak will fall.\n"
                                "🦇 The hunters become the hunted."
                            ),
                            color=0x8B0000
                        )


                        embed.set_image(url=BLOOD_MOON_GIF)

                        embed.set_footer(
                            text="V4MPYR • Vampire Kingdom"
                        )


                        await channel.send(
                            content=f"<@&{BLOOD_MOON_ROLE_ID}>",
                            embed=embed
                        )



            else:

                await set_blood_moon(False)


                if self.blood_moon_active:

                    self.blood_moon_active = False

                    print("🌑 Blood Moon ENDED")


                    if channel:

                        embed = discord.Embed(
                            title="🌑 THE BLOOD MOON HAS ENDED",
                            description=(
                                "The crimson curse fades away...\n\n"
                                "⚔️ Normal Hunt Rules Restored.\n"
                                "🛡️ Protection Active.\n"
                                "⏳ Cooldowns Active."
                            ),
                            color=0x8B0000
                        )


                        embed.set_footer(
                            text="V4MPYR • Vampire Kingdom"
                        )


                        await channel.send(
                            embed=embed
                        )


            await asyncio.sleep(60)



    async def leaderboard_loop(self):

        await self.wait_until_ready()

        while not self.is_closed():

            try:

                guilds = await get_all_leaderboards()

                for guild_id, channel_id, blood_id, level_id, message_id, stolen_id in guilds:

                    guild = self.get_guild(guild_id)

                    if guild is None:
                        continue

                    channel = guild.get_channel(channel_id)

                    if channel is None:
                        continue


                    async def build_embed(title, data, mode):

                        medals = ["🥇", "🥈", "🥉"]
                        rows = []

                        for i, row in enumerate(data):

                            member = guild.get_member(row[0])
                            name = member.display_name if member else row[1]

                            medal = medals[i] if i < 3 else f"{i+1}."

                            if mode == "blood":
                                rows.append(f"{medal} **{name}** — `{row[2]:,} Blood`")

                            elif mode == "level":
                                rows.append(f"{medal} **{name}** — `Level {row[2]}` • `{row[3]:,} XP`")

                            elif mode == "messages":
                                rows.append(f"{medal} **{name}** — `{row[2]:,} Messages`")

                            elif mode == "stolen":
                                rows.append(f"{medal} **{name}** — `{row[2]:,} Blood`")

                        embed = discord.Embed(
                            title=title,
                            description="\n".join(rows) if rows else "No data available.",
                            color=0x8B0000
                        )

                        if mode == "blood":
                            embed.set_image(url=BLOOD_BANNER)
                        elif mode == "level":
                            embed.set_image(url=LEVEL_BANNER)
                        elif mode == "messages":
                            embed.set_image(url=MESSAGE_BANNER)
                        elif mode == "stolen":
                            embed.set_image(url=STOLEN_BANNER)

                        embed.set_footer(text="V4MPYR • Live Leaderboard")

                        return embed


                    blood = await build_embed(
                        "🩸 Blood Leaderboard",
                        await get_blood_leaderboard(),
                        "blood"
                    )

                    level = await build_embed(
                        "⭐ Level Leaderboard",
                        await get_level_leaderboard(),
                        "level"
                    )

                    messages = await build_embed(
                        "💬 Message Leaderboard",
                        await get_message_leaderboard(),
                        "messages"
                    )

                    stolen = await build_embed(
                        "🩸 Blood Stolen Leaderboard",
                        await get_stolen_leaderboard(),
                        "stolen"
                    )

                    await (await channel.fetch_message(blood_id)).edit(embed=blood)
                    await (await channel.fetch_message(level_id)).edit(embed=level)
                    await (await channel.fetch_message(message_id)).edit(embed=messages)
                    await (await channel.fetch_message(stolen_id)).edit(embed=stolen)

            except Exception as e:
                print(f"Leaderboard Error: {e}")

            await asyncio.sleep(30)


    async def loan_scheduler(self):

        await self.wait_until_ready()

        while not self.is_closed():

            try:

                await process_overdue_loans()

            except Exception as e:

                print(f"Loan Scheduler Error: {e}")

            await asyncio.sleep(3600)



    async def setup_hook(self):

        await setup_database()


        await self.load_extension("cogs.economy")
        print("✅ Economy Cog Loaded!")


        await self.load_extension("cogs.chat")
        print("✅ Chat Cog Loaded!")


        await self.load_extension("cogs.moderation")
        print("✅ Moderation Cog Loaded!")

        await self.load_extension("cogs.admin")
        print("✅ Admin Cog Loaded!")

        await self.load_extension("cogs.leaderboard")
        print("✅ Leaderboard Cog Loaded!")
        
        await self.load_extension("cogs.bank")
        print("✅ Bank Cog Loaded!")

        await self.load_extension("cogs.level")
        print("✅ Level Cog Loaded!")

        guild = discord.Object(
            id=1233939059194466374
        )


        self.tree.copy_global_to(
            guild=guild
        )

        synced = await self.tree.sync(
            guild=guild
        )


        self.loop.create_task(
            self.blood_moon_scheduler()
        )

        self.loop.create_task(
            self.leaderboard_loop()
        )

        self.loop.create_task(
            self.loan_scheduler()
        )


        print("=" * 40)
        print("🩸 V4MPYR ONLINE")
        print(f"✅ Synced {len(synced)} guild command(s)")
        print("=" * 40)



bot = V4MPYR()



@bot.event
async def on_ready():

    print("=" * 40)
    print(f"🤖 Logged in as {bot.user}")
    print(f"🆔 Bot ID: {bot.user.id}")
    print("=" * 40)



bot.run(TOKEN)