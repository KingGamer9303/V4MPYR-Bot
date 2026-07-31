import discord
from discord import app_commands
from discord.ext import commands

from database.database import (
    get_level_data,
    get_level_profile,
)

class Level(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_title(self, level: int) -> str:
        if level >= 100:
            return "🩸 Immortal"
        if level >= 75:
            return "⚜ Ancient Lord"
        if level >= 50:
            return "👑 Elder Vampire"
        if level >= 25:
            return "🦇 Blood Knight"
        if level >= 10:
            return "🌙 Night Walker"
        return "🩸 Newborn"

    @app_commands.command(name="level", description="View your current level.")
    async def level(self, interaction: discord.Interaction):
        level, xp, required = await get_level_data(interaction.user.id)
        filled = int((xp / required) * 10) if required else 10
        bar = "█" * filled + "░" * (10 - filled)

        embed = discord.Embed(title="⭐ Level", colour=0x8B0000)
        embed.description = (
            f"👤 {interaction.user.mention}\n\n"
            f"⭐ **Level:** {level}\n"
            f"✨ **XP:** {xp}/{required}\n"
            f"`{bar}`\n\n"
            f"🏅 **Title:** {self.get_title(level)}"
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="rank", description="View your or another user's rank.")
    async def rank(self, interaction: discord.Interaction, user: discord.Member | None = None):
        user = user or interaction.user
        level, xp, required, blood, messages, rank = await get_level_profile(user.id)

        filled = int((xp / required) * 10) if required else 10
        bar = "█" * filled + "░" * (10 - filled)

        embed = discord.Embed(title="🏆 Rank Card", colour=0x8B0000)
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.description = (
            f"👤 {user.mention}\n\n"
            f"🏆 **Server Rank:** #{rank}\n"
            f"⭐ **Level:** {level}\n"
            f"✨ **XP:** {xp}/{required}\n"
            f"`{bar}`\n\n"
            f"🩸 **Blood:** {blood:,}\n"
            f"💬 **Messages:** {messages:,}\n"
            f"🏅 **Title:** {self.get_title(level)}"
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="levelrewards", description="View level milestone rewards.")
    async def levelrewards(self, interaction: discord.Interaction):
        embed = discord.Embed(title="🩸 Level Rewards", colour=0x8B0000)
        rewards = [
            (10, "🌙 Night Walker", "5,000"),
            (25, "🦇 Blood Knight", "20,000"),
            (50, "👑 Elder Vampire", "75,000"),
            (75, "⚜ Ancient Lord", "150,000"),
            (100, "🩸 Immortal", "300,000"),
        ]
        for lvl, title, reward in rewards:
            embed.add_field(
                name=f"Level {lvl}",
                value=f"{title}\n🩸 {reward} Blood",
                inline=False
            )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Level(bot))
