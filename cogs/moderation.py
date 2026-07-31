print(">>> moderation.py imported <<<")

import discord

from discord.ext import commands
from discord import app_commands

from database.database import (
    add_warn,
    remove_warn,
    get_warns
)


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(
        name="warn",
        description="Warn a member."
    )
    @app_commands.default_permissions(
        moderate_members=True
    )
    @app_commands.describe(
        member="Member to warn",
        reason="Reason for warning"
    )
    async def warn(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str
    ):

        if member.bot:
            return await interaction.response.send_message(
                "❌ You can't warn bots.",
                ephemeral=True
            )

        if member == interaction.user:
            return await interaction.response.send_message(
                "❌ You can't warn yourself.",
                ephemeral=True
            )

        await add_warn(member.id)

        warns = await get_warns(member.id)

        embed = discord.Embed(
            title="⚠️ Warning Issued",
            color=0x8B0000
        )

        embed.add_field(
            name="Member",
            value=member.mention,
            inline=False
        )

        embed.add_field(
            name="Moderator",
            value=interaction.user.mention,
            inline=False
        )

        embed.add_field(
            name="Reason",
            value=reason,
            inline=False
        )

        embed.add_field(
            name="Total Warns",
            value=str(warns),
            inline=False
        )

        await interaction.response.send_message(embed=embed)


    @app_commands.command(
        name="warnings",
        description="View a member's warnings."
    )
    async def warnings(
        self,
        interaction: discord.Interaction,
        member: discord.Member = None
    ):

        member = member or interaction.user

        warns = await get_warns(member.id)

        embed = discord.Embed(
            title="⚠️ Warning Record",
            color=0x8B0000
        )

        embed.description = (
            f"👤 {member.mention}\n\n"
            f"⚠️ **Warnings:** {warns}"
        )

        await interaction.response.send_message(embed=embed)


    @app_commands.command(
        name="unwarn",
        description="Remove one warning."
    )
    @app_commands.default_permissions(
        moderate_members=True
    )
    async def unwarn(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):

        await remove_warn(member.id)

        warns = await get_warns(member.id)

        embed = discord.Embed(
            title="✅ Warning Removed",
            color=0x8B0000
        )

        embed.add_field(
            name="Member",
            value=member.mention,
            inline=False
        )

        embed.add_field(
            name="Current Warns",
            value=str(warns),
            inline=False
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Moderation(bot))