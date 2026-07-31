import random
import time
import aiosqlite
import discord
from discord import app_commands
from discord.ext import commands

from database.database import (
    create_user,
    get_balance,
    add_blood,
    remove_blood,
    transfer_blood,
    get_profile,
    get_rank,
    set_hunt_enabled,
    get_hunt_status,
    can_hunt,
    is_protected,
    set_protection,
    use_hunt_charge,
    restore_hunt_charges,
    add_hunt_win,
    add_hunt_loss,
    get_hunt_data,
    add_xp,
    get_blood_moon,
    get_loan,
    take_loan,
    repay_loan
)

WIN_MESSAGES = [
    "🦇 You lunged from the shadows and drained **{blood} Blood** from {target}.",
    "⚔️ {target} was defeated beneath the crimson moon. **+{blood} Blood**.",
    "🩸 Your fangs pierced {target}'s defence. **+{blood} Blood**.",
    "🍷 The hunt was successful. You stole **{blood} Blood** from {target}.",
    "☠️ {target} became tonight's prey. **+{blood} Blood**."
]

LOSE_MESSAGES = [
    "💀 {target} fought back. **-{blood} Blood**.",
    "🩸 Your hunt failed. **-{blood} Blood**.",
    "🥀 Darkness abandoned you. **-{blood} Blood**.",
    "⚔️ {target} escaped your attack. **-{blood} Blood**.",
    "🦇 Your prey became the hunter. **-{blood} Blood**."
]


def format_time(seconds):
    if seconds <= 0:
        return "Ready"
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if h:
        return f"{h}h {m}m"
    return f"{m}m {s}s"


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="balance",
        description="Check your Blood balance."
)
    async def balance(self, interaction: discord.Interaction):
        await create_user(interaction.user.id)

        balance = await get_balance(interaction.user.id)

        embed = discord.Embed(
            title="🩸 Blood Balance",
            color=0x8B0000
        )

        embed.add_field(
            name="Blood",
            value=f"🩸 {balance}",
            inline=False
        )

        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="daily",
        description="Claim your daily reward."
    )
    @app_commands.checks.cooldown(1, 86400)
    async def daily(self, interaction: discord.Interaction):
        await create_user(interaction.user.id)

        reward = 100
        await add_blood(interaction.user.id, reward)

        balance = await get_balance(interaction.user.id)

        embed = discord.Embed(
            title="🩸 Daily Reward",
            description=f"You received **{reward} Blood**.",
            color=0x8B0000
        )

        embed.add_field(
            name="Current Balance",
            value=f"🩸 {balance}",
            inline=False
        )

        embed.set_footer(text="Come back in 24 hours!")
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

        await interaction.response.send_message(embed=embed)

    @daily.error
    async def daily_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CommandOnCooldown):
            hours = int(error.retry_after // 3600)
            minutes = int((error.retry_after % 3600) // 60)

            embed = discord.Embed(
                title="⏳ Daily Already Claimed",
                description=f"You can claim your next daily reward in **{hours}h {minutes}m**.",
                color=0xFFAA00
            )

            await interaction.response.send_message(
                embed=embed,
                ephemeral=True
            )

    @app_commands.command(
        name="profile",
        description="View your V4MPYR profile."
    )
    async def profile(self, interaction: discord.Interaction):

        await create_user(interaction.user.id)

        profile = await get_profile(interaction.user.id)
        rank = await get_rank(interaction.user.id)

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

        now = int(time.time())

        recharge = format_time(hunt_recharge - now) if hunt_recharge > now else "Ready"
        protection = format_time(protection_until - now) if protection_until > now else "None"

    

        embed = discord.Embed(
            title=f"🩸 {vampire_name}'s Profile",
            color=0x8B0000
        )

        embed.description = (
            f"🩸 **Blood:** {blood:,}\n"
            f"⭐ **Level:** {level}\n"
            f"🏆 **Rank:** #{rank}\n"
            f"\n━━━━━━━━━━━━━━━━━━\n"
            f"⚔️ **Hunt Mode:** {'Enabled' if hunt_enabled else 'Disabled'}\n"
            f"🗡️ **Charges:** {hunt_charges}/{hunt_max_charges}\n"
            f"⏳ **Next Hunt:** {recharge}\n"
            f"🛡️ **Protection:** {protection}\n"
            f"\n━━━━━━━━━━━━━━━━━━\n"
            f"🏆 **Wins:** {hunt_wins}\n"
            f"💀 **Losses:** {hunt_losses}\n"
            f"⚔️ **Total Hunts:** {total_hunts}\n"
            f"🩸 **Blood Stolen:** {blood_stolen:,}\n"
            f"\n━━━━━━━━━━━━━━━━━━\n"
            f"💬 **Messages:** {messages}\n"
            f"🔥 **Today's Messages:** {today_messages}\n"
            f"⚠️ **Vampire Warns:** {warns}\n"
            f"📅 **Joined:** <t:{int(interaction.user.joined_at.timestamp())}:D>"
        )

        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        embed.set_footer(text="V4MPYR • Vampire Kingdom")

        await interaction.response.send_message(embed=embed)


    @app_commands.command(
        name="pay",
        description="Transfer Blood to another vampire."
    )
    @app_commands.describe(
        member="The vampire to pay.",
        amount="Amount of Blood to transfer."
    )
    async def pay(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        amount: int
    ):
        if member.bot:
            await interaction.response.send_message(
                "❌ You can't pay bots.",
                ephemeral=True
            )
            return

        if member.id == interaction.user.id:
            await interaction.response.send_message(
                "❌ You can't pay yourself.",
                ephemeral=True
            )
            return

        success, reason = await transfer_blood(
            interaction.user.id,
            member.id,
            amount
        )

        if not success:
            if reason == "invalid_amount":
                await interaction.response.send_message(
                    "❌ Amount must be greater than 0.",
                    ephemeral=True
                )
                return

            if reason == "insufficient":
                await interaction.response.send_message(
                    "❌ You don't have enough Blood.",
                    ephemeral=True
                )
                return

        balance = await get_balance(interaction.user.id)

        embed = discord.Embed(
            title="🩸 Blood Transfer",
            description=f"Successfully transferred **{amount} Blood** to {member.mention}.",
            color=0x8B0000
        )

        embed.add_field(
            name="Remaining Balance",
            value=f"🩸 {balance}",
            inline=False
        )

        await interaction.response.send_message(embed=embed)




    @app_commands.command(
        name="huntmode",
        description="Manage Hunt Mode."
    )
    @app_commands.describe(
        action="enable, disable or status"
    )
    async def huntmode(
        self,
        interaction: discord.Interaction,
        action: str
    ):
        action = action.lower()

        if action == "enable":
            await set_hunt_enabled(interaction.user.id, True)
            return await interaction.response.send_message("""🦇 You have embraced the darkness.

You are now part of the Blood Hunt.

⚠️ Other vampires can now hunt you.""")

        if action == "disable":

            blood_moon = await get_blood_moon()

            if blood_moon:
                return await interaction.response.send_message(
                    "🌕 You cannot disable Hunt Mode during Blood Moon.",
                    ephemeral=True
                )

            await set_hunt_enabled(interaction.user.id, False)

            return await interaction.response.send_message(
                """🌑 You disappeared into the shadows.

You can no longer hunt or be hunted."""
            )

        if action == "status":
            enabled = await get_hunt_status(interaction.user.id)
            return await interaction.response.send_message(
                f"Status: {'🩸 Enabled' if enabled else '🛡️ Disabled'}"
            )

        await interaction.response.send_message(
            "Use: enable, disable or status.",
            ephemeral=True
        )



    @app_commands.command(
        name="hunt",
        description="Hunt a vampire."
    )
    @app_commands.describe(
        member="Target vampire"
    )
    async def hunt(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):
        if member.bot:
            return await interaction.response.send_message(
                "🤖 Machines have no blood to drink.",
                ephemeral=True
            )

        if member.id == interaction.user.id:
            return await interaction.response.send_message(
                "🩸 Even vampires don't feed on themselves.",
                ephemeral=True
            )

        await restore_hunt_charges(interaction.user.id)

        blood_moon = await get_blood_moon()

        ok, reason = await can_hunt(interaction.user.id)

        if blood_moon:
            ok = True

        if not ok:
            if reason == "disabled":
                return await interaction.response.send_message(
                    "❌ Enable Hunt Mode first using `/huntmode enable`."
                )

            if reason == "protected":
                return await interaction.response.send_message(
                    "🛡️ You are currently protected."
                )

            return await interaction.response.send_message(
                f"⏳ Hunt Charges are empty.\nRecharge: **{format_time(reason)}**"
            )

        if not blood_moon and not await get_hunt_status(member.id):
            return await interaction.response.send_message(
                "❌ Target has Hunt Mode disabled."
            )


        if await is_protected(member.id) and not blood_moon:
            return await interaction.response.send_message(
                "🛡️ Target is protected."
            )

        await use_hunt_charge(interaction.user.id)

        win = random.choice([True, False])

        if win:
            target_blood = await get_balance(member.id)
            steal = max(1, target_blood // 10)

            if blood_moon:
                steal *= 2

            await remove_blood(member.id, steal)
            await add_blood(interaction.user.id, steal)
            await add_xp(interaction.user.id, 20)

            async with aiosqlite.connect("v4mpyr.db") as db:
                cursor = await db.execute(
                    "SELECT times_hunted FROM users WHERE user_id=?",
                    (member.id,)
                )

                row = await cursor.fetchone()
                count = (row[0] if row else 0) + 1

                if count >= 3:
                    await set_protection(member.id, 30)
                    count = 0

                await db.execute(
                    "UPDATE users SET times_hunted=? WHERE user_id=?",
                    (count, member.id)
                )

                await db.commit()

            await add_hunt_win(
                interaction.user.id,
                steal
            )

            embed = discord.Embed(
                title="⚔️ Hunt Successful",
                description=random.choice(WIN_MESSAGES).format(target=member.mention,blood=steal),
                color=0x8B0000
            )
            if blood_moon:
                base_reward = steal // 2

                reward = (
                    f"🩸 Base Blood: +{base_reward}\n"
                    f"🌕 Blood Moon ×2: +{steal} Blood\n"
                    f"⭐ +20 XP"
                )

            else:
                reward = (
                    f"🩸 +{steal} Blood\n"
                    f"⭐ +20 XP"
                )

            embed.add_field(
                name="Reward",
                value=reward
            )
            return await interaction.response.send_message(embed=embed)

        own_blood = await get_balance(interaction.user.id)
        loss = max(1, own_blood // 10)

        await remove_blood(interaction.user.id, loss)
        await add_hunt_loss(
            interaction.user.id,
            loss
        )

        embed = discord.Embed(
            title="💀 Hunt Failed",
            description=random.choice(LOSE_MESSAGES).format(target=member.mention,blood=loss),
            color=0x550000
        )
        embed.add_field(name="Penalty", value=f"🩸 -{loss} Blood")
        await interaction.response.send_message(embed=embed)


    @app_commands.command(
        name="loan",
        description="Blood Bank Loan"
    )
    @app_commands.describe(
        action="view or take",
        amount="Loan amount"
    )
    @app_commands.choices(
        action=[
            app_commands.Choice(name="view", value="view"),
            app_commands.Choice(name="take", value="take"),
            app_commands.Choice(name="repay", value="repay"),
        ]
    )
    async def loan(
        self,
        interaction: discord.Interaction,
        action: app_commands.Choice[str],
        amount: str | None = None
    ):

        if action.value == "view":

            loan_amount, interest, due, credit, repayments, cooldown, tier = await get_loan(
    interaction.user.id
    
            )

            embed = discord.Embed(
                title="🏦 Blood Bank Loan",
                color=0x8B0000
            )

            if loan_amount <= 0:
                embed.add_field(
                    name="🩸 Active Loan",
                    value="None",
                    inline=False
                )
                embed.add_field(
                    name="⭐ Credit Score",
                    value=str(credit),
                    inline=True
                )

            else:
                total = loan_amount + interest
                remaining = max(0, due - int(time.time()))

                embed.add_field(
                    name="🩸 Borrowed",
                    value=f"{loan_amount:,} Blood"
                )

                embed.add_field(
                    name="💰 Interest",
                    value=f"{interest:,} Blood"
                )

                embed.add_field(
                    name="📦 Total Due",
                    value=f"{total:,} Blood"
                )

                embed.add_field(
                    name="📅 Due In",
                    value=f"{remaining // 86400}d"
                )

                embed.add_field(
                    name="⭐ Credit Score",
                    value=str(credit)
                )

            await interaction.response.send_message(embed=embed)
            return


        if action.value == "repay":

            if amount is None:
                return await interaction.response.send_message(
                    "❌ Enter an amount or 'all'.",
                    ephemeral=True
                )

            loan_amount, interest, due, credit, repayments, cooldown, tier = await get_loan(
    interaction.user.id
)

            total_due = loan_amount + interest

            if total_due <= 0:
                return await interaction.response.send_message(
                    "❌ You don't have an active loan.",
                    ephemeral=True
                )

            balance = await get_balance(interaction.user.id)

            if amount.lower() == "all":
                amount = min(balance, total_due)
            else:
                try:
                    amount = int(amount.replace(",", ""))
                except:
                    return await interaction.response.send_message(
                        "❌ Invalid amount.",
                        ephemeral=True
                    )

            success, remaining = await repay_loan(
                interaction.user.id,
                amount
            )

            if not success:
                return await interaction.response.send_message(
                    "❌ You don't have enough Blood.",
                    ephemeral=True
                )

            embed = discord.Embed(
                color=0x8B0000
            )

            if remaining == 0:
                embed.title = "🩸 Debt Cleared"
                embed.description = (
                 "The Blood Bank has accepted your final payment.\n\n"
                "⭐ Credit Score +5\n"
                "⏳ 7 Day Loan Cooldown Started"
          ) 
            else:
                embed.title = "🩸 Loan Repayment"
                embed.add_field(
                    name="Paid",
                    value=f"{amount:,} Blood",
                    inline=True
                )
                embed.add_field(
                    name="Remaining Debt",
                    value=f"{remaining:,} Blood",
                    inline=True
                )

            return await interaction.response.send_message(embed=embed)


        if action.value == "take":

            if amount is None:
                return await interaction.response.send_message(
                    "❌ Enter loan amount.",
                    ephemeral=True
                )

            try:
                amount = int(amount.replace(",", ""))
            except:
                return await interaction.response.send_message(
                    "❌ Invalid amount.",
                    ephemeral=True
                )

            success, data = await take_loan(
                interaction.user.id,
                amount
            )

            if not success:

                errors = {
                    "cooldown": "⏳ You recently repaid a loan. Wait until the cooldown ends.",
                    "active": "❌ You already have an active loan.",
                    "locked": "🔒 You haven't unlocked any loan tier yet.",
                    "limit": "❌ Requested amount exceeds your current loan limit.",
                    "worth": "❌ Loan cannot exceed 25% of your Net Worth."
                }

                return await interaction.response.send_message(
                    errors.get(data, "❌ Loan rejected."),
                    ephemeral=True
                )

            embed = discord.Embed(
                title=f"{data['emoji']} {data['name']} Loan Approved",
                color=0x8B0000
            )

            embed.add_field(
                name="💰 Borrowed",
                value=f"{amount:,} Blood",
                inline=True
            )

            embed.add_field(
                name="📈 Interest",
                value=f"{data['interest']}%",
                inline=True
            )

            embed.add_field(
                name="💸 Total Interest",
                value=f"{int(amount * data['interest'] / 100):,} Blood",
                inline=False
            )

            embed.set_footer(text="Repay within 7 days.")

            return await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Economy(bot))