import time
import discord
from discord.ext import commands

from database.database import (
    add_chat_reward,
    add_xp,
    add_blood
)

LEVEL_CHANNEL_ID = 1532257298251120790

LEVEL_ROLES = {
    10: 1532263134625005620,
    25: 1532263210143715348,
    50: 1532263263457251428,
    75: 1532263363973746828,
    100: 1532263438850723860,
}

cooldowns = {}


class Chat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.xp_cooldown = {}

    def can_gain_xp(self, user_id):
        now = time.time()

        last = self.xp_cooldown.get(user_id, 0)

        if now - last < 30:
            return False

        self.xp_cooldown[user_id] = now
        return True

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author.bot:
            return

        if message.guild is None:
            return

        if len(message.content.strip()) < 10:
            return

        user_id = message.author.id
        now = time.time()

        # Count every valid message
        await add_chat_reward(user_id, reward=False)

        # Existing Blood reward cooldown
        if user_id in cooldowns:
            if now - cooldowns[user_id] < 10:
                return

        cooldowns[user_id] = now

        # Existing economy reward
        await add_chat_reward(user_id, reward=True)

        # XP System
        if self.can_gain_xp(user_id):

            leveled, level, xp, required = await add_xp(
                user_id,
                5
            )

            if leveled:

                reward = level * 250

                await add_blood(user_id, reward)

                role_reward = None

                for lvl, role_id in sorted(LEVEL_ROLES.items()):

                    if level == lvl:

                        role_reward = message.guild.get_role(role_id)

                        if role_reward:

                            try:

                                remove_roles = []

                                for rid in LEVEL_ROLES.values():

                                    role = message.guild.get_role(rid)

                                    if role and role in message.author.roles:
                                        remove_roles.append(role)

                                if remove_roles:
                                    await message.author.remove_roles(
                                        *remove_roles,
                                        reason="Level Role Update"
                                    )

                                await message.author.add_roles(
                                    role_reward,
                                    reason="Level Reward"
                                )

                            except discord.Forbidden:
                                pass

                        break

                embed = discord.Embed(
                    title="🎉 Level Up!",
                    description=(
                        f"Congratulations {message.author.mention}!\n\n"
                        f"⭐ **Level:** {level}\n"
                        f"🩸 **Reward:** {reward:,} Blood"
                        + (
                            f"\n🎭 **Role Unlocked:** {role_reward.mention}"
                            if role_reward else ""
                        )
                    ),
                    color=discord.Color.red()
                )

                channel = message.guild.get_channel(LEVEL_CHANNEL_ID)

                if channel:
                    await channel.send(
                        content=message.author.mention,
                        embed=embed
                    )
                else:
                    await message.channel.send(
                        content=message.author.mention,
                        embed=embed
                    )


async def setup(bot):
    await bot.add_cog(Chat(bot))