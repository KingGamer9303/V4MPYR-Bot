import discord
from discord.ext import commands
from discord import app_commands

from database.database import (
    create_user,
    assign_quest,
    get_current_quest,
    finish_quest,
    MAX_DAILY_QUESTS
)

import json


class Quests(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(
        name="quest",
        description="View your daily quest."
    )
    async def quest(
        self,
        interaction: discord.Interaction
    ):

        user_id = interaction.user.id

        await create_user(user_id)

        quest = await get_current_quest(user_id)


        if not quest or not quest[0]:

            quest_data = await assign_quest(user_id)

            if quest_data is None:

                embed = discord.Embed(
                    title="✅ Daily Quests Complete",
                    description=(
                        "You have completed all daily quests.\n"
                        "Come back tomorrow."
                    ),
                    color=0x00ff00
                )

                return await interaction.response.send_message(
                    embed=embed
                )


            quest = await get_current_quest(user_id)



        (
            qtype,
            goal,
            progress,
            reward,
            completed,
            done
        ) = quest


        completed_list = []


        if False:

            embed = discord.Embed(
                title="✅ Daily Quests Finished",
                description=(
                    f"You completed {MAX_DAILY_QUESTS}/"
                    f"{MAX_DAILY_QUESTS} quests today."
                ),
                color=0x00ff00
            )

            return await interaction.response.send_message(
                embed=embed
            )


        names = {

            "messages":
            "💬 Spread the Legend",

            "xp":
            "⭐ Ancient Training",

            "blood":
            "🩸 Gather Blood",

            "hunt":
            "⚔ Fresh Prey",

            "deposit":
            "🏦 Secure The Treasury"

        }


        if progress >= goal:

            reward_amount = await finish_quest(
                user_id
            )

            embed = discord.Embed(
                title="🎉 Quest Completed",
                description=(
                    f"You earned\n\n"
                    f"🩸 **{reward_amount:,} Blood**"
                ),
                color=0xffd700
            )

            return await interaction.response.send_message(
                embed=embed
            )


        percent = min(
            progress / goal,
            1
        )

        filled = int(percent * 10)

        bar = (
            "█" * filled +
            "░" * (10-filled)
        )


        embed = discord.Embed(
            title="📜 Daily Quest",
            color=0x8B0000
        )


        embed.set_author(
            name="V4MPYR Quest System",
            icon_url=interaction.user.display_avatar.url
        )


        embed.add_field(
            name="Quest",
            value=names.get(
                qtype,
                qtype.title()
            ),
            inline=False
        )


        embed.add_field(
            name="Progress",
            value=(
                f"`{bar}`\n"
                f"**{progress:,}/{goal:,}**"
            ),
            inline=False
        )


        embed.add_field(
            name="Reward",
            value=f"🩸 {reward:,} Blood",
            inline=True
        )


        embed.add_field(
            name="Status",
            value="🕒 In Progress",
            inline=True
        )


        embed.set_footer(
            text=(
                f"Completed Today: "
                f"{len(completed_list)}/{MAX_DAILY_QUESTS}"
            )
        )


        await interaction.response.send_message(
            embed=embed
        )



async def setup(bot):

    await bot.add_cog(
        Quests(bot)
    )