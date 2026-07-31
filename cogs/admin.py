import discord
from discord import app_commands
from discord.ext import commands

from database.database import (
    add_blood,
    add_raw_xp,
    remove_blood,
    get_balance,
    add_xp,
    reset_xp,
    set_hunt_enabled,
    set_level,
    set_protection,
    set_blood_moon,
    get_blood_moon,
    set_hunt_charges,
    reset_hunt_charges,
    get_hunt_data,
    set_hunt_limit,
    reset_hunt_limit,
    get_hunt_charges,
    get_profile,
    get_rank,
    create_user,
    set_xp
)

from database.database import (
    reset_xp,
    set_level,
    add_raw_xp,
    set_xp
)

class Admin(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    async def admin_check(self, interaction):

        if interaction.user.guild_permissions.administrator:
            return True

        await interaction.response.send_message(
            "❌ You don't have permission.",
            ephemeral=True
        )

        return False


    # =========================
    # ADMIN CHECK
    # =========================

    @app_commands.command(
        name="admincheck",
        description="Check admin system."
    )
    async def admincheck(
        self,
        interaction: discord.Interaction
    ):

        if not await self.admin_check(interaction):
            return

        embed = discord.Embed(
            title="🛠️ Admin System",
            description="✅ V4MPYR Control Panel is online.",
            color=0x8B0000
        )

        await interaction.response.send_message(
            embed=embed
        )


    # =========================
    # BLOOD
    # =========================

    @app_commands.command(
        name="addblood",
        description="Add blood."
    )
    async def addblood(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        amount: int
    ):

        if not await self.admin_check(interaction):
            return

        await add_blood(user.id, amount)

        await interaction.response.send_message(
            f"🩸 Added **{amount} Blood** to {user.mention}"
        )


    @app_commands.command(
        name="removeblood",
        description="Remove blood."
    )
    async def removeblood(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        amount: int
    ):

        if not await self.admin_check(interaction):
            return

        await remove_blood(user.id, amount)

        await interaction.response.send_message(
            f"🩸 Removed **{amount} Blood** from {user.mention}"
        )


    @app_commands.command(
        name="resetblood",
        description="Reset blood."
    )
    async def resetblood(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):

        if not await self.admin_check(interaction):
            return

        balance = await get_balance(user.id)

        await remove_blood(
            user.id,
            balance
        )

        await interaction.response.send_message(
            f"🩸 Reset blood of {user.mention}"
        )


    # =========================
    # XP
    # =========================

    @app_commands.command(
        name="addxp",
        description="Add XP."
    )
    async def addxp(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        amount: int
    ):

        if not await self.admin_check(interaction):
            return

        await add_xp(
            user.id,
            amount
        )

        await interaction.response.send_message(
            f"⭐ Added **{amount} XP** to {user.mention}"
        )

    @app_commands.command(
        name="resetxp",
        description="Reset a user's XP and level."
    )
    async def resetxp(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):

        if not await self.admin_check(interaction):
            return

        await reset_xp(user.id)

        embed = discord.Embed(
            title="⭐ XP Reset",
            description=(
                f"👤 **User:** {user.mention}\n"
                f"⭐ **Level:** 1\n"
                f"✨ **XP:** 0"
            ),
            color=0x8B0000
        )

        await interaction.response.send_message(embed=embed)


    @app_commands.command(
        name="setlevel",
        description="Set a user's level."
    )
    async def setlevelcmd(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        level: int
    ):

        if not await self.admin_check(interaction):
            return

        if level < 1:
            level = 1

        await set_level(user.id, level)

        embed = discord.Embed(
            title="⭐ Level Updated",
            description=(
                f"👤 **User:** {user.mention}\n"
                f"⭐ **New Level:** {level}"
            ),
            color=0x8B0000
        )

        await interaction.response.send_message(embed=embed)


    @app_commands.command(
        name="addrawxp",
        description="Add raw XP without forcing level recalculation."
    )
    async def addrawxpcmd(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        amount: int
    ):

        if not await self.admin_check(interaction):
            return

        await add_raw_xp(user.id, amount)

        await interaction.response.send_message(
            f"⭐ Added **{amount} Raw XP** to {user.mention}"
        )


    @app_commands.command(
        name="setxp",
        description="Set current XP."
    )
    async def setxpcmd(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        amount: int
    ):

        if not await self.admin_check(interaction):
            return

        await set_xp(user.id, amount)

        await interaction.response.send_message(
            f"⭐ Set {user.mention}'s XP to **{amount}**"
        )


    @app_commands.command(
        name="removexp",
        description="Remove current XP."
    )
    async def removexp(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        amount: int
    ):

        if not await self.admin_check(interaction):
            return

        await add_raw_xp(user.id, -amount)

        await interaction.response.send_message(
            f"⭐ Removed **{amount} XP** from {user.mention}"
        )


    # =========================
    # HUNT MODE
    # =========================

    @app_commands.command(
        name="enablehunt",
        description="Enable hunt."
    )
    async def enablehunt(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):

        if not await self.admin_check(interaction):
            return

        await set_hunt_enabled(
            user.id,
            True
        )

        await interaction.response.send_message(
            f"⚔️ Hunt enabled for {user.mention}"
        )


    @app_commands.command(
        name="disablehunt",
        description="Disable hunt."
    )
    async def disablehunt(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):

        if not await self.admin_check(interaction):
            return

        await set_hunt_enabled(
            user.id,
            False
        )

        await interaction.response.send_message(
            f"🛑 Hunt disabled for {user.mention}"
        )


    # =========================
    # PROTECTION
    # =========================

    @app_commands.command(
        name="protect",
        description="Give protection."
    )
    async def protect(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        minutes: int = 30
    ):

        if not await self.admin_check(interaction):
            return

        await set_protection(
            user.id,
            minutes
        )

        await interaction.response.send_message(
            f"🛡️ Protected {user.mention} for {minutes} minutes"
        )


    # =========================
    # BLOOD MOON
    # =========================

    @app_commands.command(
        name="bloodmoon",
        description="Control Blood Moon."
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(
                name="Start",
                value="start"
            ),
            app_commands.Choice(
                name="Stop",
                value="stop"
            )
        ]
    )
    async def bloodmoon(
        self,
        interaction: discord.Interaction,
        action: app_commands.Choice[str]
    ):

        if not await self.admin_check(interaction):
            return

        if action.value == "start":

            await set_blood_moon(True)
            msg = "🌕 Blood Moon Started"

        else:

            await set_blood_moon(False)
            msg = "🌑 Blood Moon Stopped"


        await interaction.response.send_message(msg)


    @app_commands.command(
        name="bloodmoonstatus",
        description="Check Blood Moon."
    )
    async def bloodmoonstatus(
        self,
        interaction: discord.Interaction
    ):

        status = await get_blood_moon()

        await interaction.response.send_message(
            "🌕 Blood Moon ACTIVE"
            if status
            else
            "🌑 Blood Moon INACTIVE"
        )


    # =========================
    # HUNT CHARGES
    # =========================

    @app_commands.command(
        name="setcharges",
        description="Set current charges."
    )
    async def setcharges(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        amount: int
    ):

        if not await self.admin_check(interaction):
            return

        await set_hunt_charges(
            user.id,
            amount
        )

        await interaction.response.send_message(
            f"⚔️ Charges Updated\n"
            f"{user.mention}: **{amount}**"
        )


    @app_commands.command(
        name="resetcharges",
        description="Reset charges."
    )
    async def resetcharges(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):

        if not await self.admin_check(interaction):
            return

        await reset_hunt_charges(user.id)

        await interaction.response.send_message(
            f"⚔️ Charges reset for {user.mention}"
        )


    @app_commands.command(
        name="charges",
        description="Check charges."
    )
    async def charges(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):

        data = await get_hunt_data(user.id)

        await interaction.response.send_message(
            f"⚔️ {user.mention}\n"
            f"Charges: **{data[1]}**"
        )


    # =========================
    # CHARGE LIMIT
    # =========================

    @app_commands.command(
        name="setchargelimit",
        description="Set max hunt charges."
    )
    async def setchargelimit(
        self,
        interaction: discord.Interaction,
        user: discord.Member,
        amount: int
    ):

        if not await self.admin_check(interaction):
            return

        await set_hunt_limit(
            user.id,
            amount
        )

        await interaction.response.send_message(
            f"⚔️ Hunt Limit Updated\n\n"
            f"Player: {user.mention}\n"
            f"Limit: **{amount}**"
        )


    @app_commands.command(
        name="resetchargelimit",
        description="Reset max charges."
    )
    async def resetchargelimit(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):

        if not await self.admin_check(interaction):
            return

        await reset_hunt_limit(user.id)

        await interaction.response.send_message(
            f"⚔️ Hunt Limit Reset\n"
            f"{user.mention}: **3**"
        )


    @app_commands.command(
        name="checkchargelimit",
        description="Check charge limit."
    )
    async def checkchargelimit(
        self,
        interaction: discord.Interaction,
        user: discord.Member
    ):

        data = await get_hunt_charges(user.id)

        await interaction.response.send_message(
            f"⚔️ {user.mention}\n"
            f"Charges: **{data[0]}/{data[1]}**"
        )



    @app_commands.command(
        name="checkbalance",
        description="Check another user's Blood balance."
    )
    async def checkbalance(self, interaction: discord.Interaction, user: discord.Member):

        if not await self.admin_check(interaction):
            return

        balance = await get_balance(user.id)

        embed = discord.Embed(
            title="🩸 Blood Balance",
            color=0x8B0000
        )

        embed.description = (
            f"👤 **User:** {user.mention}\n"
            f"🩸 **Blood:** {balance:,}"
        )

        embed.set_thumbnail(url=user.display_avatar.url)

        await interaction.response.send_message(embed=embed)


    @app_commands.command(
        name="checkprofile",
        description="View another user's profile."
    )
    async def checkprofile(self, interaction: discord.Interaction, user: discord.Member):

        if not await self.admin_check(interaction):
            return

        await create_user(user.id)

        profile = await get_profile(user.id)
        rank = await get_rank(user.id)

        (
            vampire_name,
            blood,
            level,
            xp,
            messages,
            today_messages,
            _,
            warns,
            hunt_enabled,
            hunt_charges,
            hunt_limit,
            hunt_max_charges,
            hunt_recharge,
            protection_until,
            hunt_wins,
            hunt_losses,
            total_hunts,
            blood_stolen,
            blood_lost,
        ) = profile

        embed = discord.Embed(
            title=f"🩸 {vampire_name}'s Profile",
            color=0x8B0000
        )

        embed.description = (
            f"🩸 **Blood:** {blood:,}\n"
            f"⭐ **Level:** {level}\n"
            f"🏆 **Rank:** #{rank}\n"
            f"⚔️ **Hunt Mode:** {'Enabled' if hunt_enabled else 'Disabled'}\n"
            f"🗡️ **Charges:** {hunt_charges}/{hunt_max_charges}\n"
            f"🏆 **Wins:** {hunt_wins}\n"
            f"💀 **Losses:** {hunt_losses}\n"
            f"⚔️ **Total Hunts:** {total_hunts}\n"
            f"🩸 **Blood Stolen:** {blood_stolen:,}\n"
            f"🩸 **Blood Lost:** {blood_lost:,}\n"
            f"💬 **Messages:** {messages}\n"
            f"⚠️ **Warns:** {warns}"
        )

        embed.set_thumbnail(url=user.display_avatar.url)

        await interaction.response.send_message(embed=embed)


async def setup(bot):

    await bot.add_cog(Admin(bot))