import discord
from discord import app_commands
from discord.ext import commands

from database.database import (
    get_blood_leaderboard,
    get_level_leaderboard,
    get_message_leaderboard,
    get_stolen_leaderboard,
    save_leaderboard,
)

MEDALS = ["🥇", "🥈", "🥉"]

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="leaderboard",
        description="View V4MPYR leaderboards."
    )
    @app_commands.choices(category=[
        app_commands.Choice(name="Blood", value="blood"),
        app_commands.Choice(name="Level", value="level"),
        app_commands.Choice(name="Messages", value="messages"),
        app_commands.Choice(name="Blood Stolen", value="stolen"),
    ])
    async def leaderboard(self, interaction: discord.Interaction, category: app_commands.Choice[str]):

        if category.value == "blood":
            data = await get_blood_leaderboard()
            title = "🩸 Blood Leaderboard"
            rows = [f'{MEDALS[i] if i<3 else str(i+1)+"."} **{interaction.guild.get_member(uid).display_name if interaction.guild.get_member(uid) else name}** — `{blood:,} Blood`'
                    for i,(uid,name,blood) in enumerate(data)]

        elif category.value == "level":
            data = await get_level_leaderboard()
            title = "⭐ Level Leaderboard"
            rows = [f'{MEDALS[i] if i<3 else str(i+1)+"."} **{interaction.guild.get_member(uid).display_name if interaction.guild.get_member(uid) else name}** — `Level {lvl}` • `{xp:,} XP`'
                    for i,(uid,name,lvl,xp) in enumerate(data)]

        elif category.value == "messages":
            data = await get_message_leaderboard()
            title = "💬 Message Leaderboard"
            rows = [f'{MEDALS[i] if i<3 else str(i+1)+"."} **{interaction.guild.get_member(uid).display_name if interaction.guild.get_member(uid) else name}** — `{msg:,} Messages`'
                    for i,(uid,name,msg) in enumerate(data)]
        else:
            data = await get_stolen_leaderboard()
            title = "🩸 Blood Stolen Leaderboard"
            rows = [f'{MEDALS[i] if i<3 else str(i+1)+"."} **{interaction.guild.get_member(uid).display_name if interaction.guild.get_member(uid) else name}** — `{stolen:,} Blood`'
                    for i,(uid,name,stolen) in enumerate(data)]

        embed = discord.Embed(title=title, description="\n".join(rows) or "No data.", colour=0x8B0000)
        embed.set_footer(text="V4MPYR • Live Leaderboard")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="setleaderboard", description="Create live leaderboard.")
    @app_commands.default_permissions(administrator=True)
    async def setleaderboard(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        msgs=[]
        for title in (
            "🩸 Blood Leaderboard",
            "⭐ Level Leaderboard",
            "💬 Message Leaderboard",
            "🩸 Blood Stolen Leaderboard",
        ):
            m=await interaction.channel.send(embed=discord.Embed(title=title,description="Loading...",colour=0x8B0000))
            msgs.append(m)
        await save_leaderboard(interaction.guild.id, interaction.channel.id,
                               msgs[0].id,msgs[1].id,msgs[2].id,msgs[3].id)
        await interaction.followup.send("✅ Leaderboards created.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Leaderboard(bot))
