
import discord
import time
from discord.ext import commands
from discord import app_commands

from database.database import (
    get_bank,
    deposit_blood,
    withdraw_blood,
    upgrade_vault,
    get_vault_name,
    VAULT_CAPACITY,
    UPGRADE_COST,
    get_progress_bar,
    get_bank_leaderboard,
    get_bank_profile,
    LOAN_TIERS,
    get_net_worth,
    get_credit_score,
    get_loan_repayments,
    get_level,
    get_best_loan_tier,
)


class Bank(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="bank", description="View your Blood Bank")
    async def bank(self, interaction: discord.Interaction):
        blood, bank, level = await get_bank(interaction.user.id)
        capacity = VAULT_CAPACITY[level]
        total = blood + bank

        embed = discord.Embed(title="🏦 Blood Bank", color=0x7A0000)
        embed.add_field(name="🩸 Blood", value=f"{blood:,}")
        embed.add_field(name="🏦 Stored Blood", value=f"{bank:,}")
        embed.add_field(name="💎 Net Worth", value=f"{total:,}", inline=False)
        embed.add_field(name="🏛 Vault", value=get_vault_name(level)) 
        bar = get_progress_bar(bank, capacity)
        embed.add_field(
            name="📦 Vault Capacity",
            value=f"{bar}\n{bank:,}/{capacity:,} Blood",
            inline=False
        )

        if level < 6:
            embed.set_footer(text=f"Upgrade Cost • {UPGRADE_COST[level]:,} Blood")
        else:
            embed.set_footer(text="Maximum Vault Level")

        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="bankhelp",
        description="Learn how the Blood Bank works."
    )
    async def bankhelp(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="🏦 Blood Bank Guide",
            description="Everything you need to know about the Blood Bank.",
            color=0x8B0000
        )

        embed.set_author(
            name="V4MPYR Blood Bank",
            icon_url=interaction.guild.icon.url if interaction.guild.icon else None
        )

        embed.add_field(
            name="🏦 Banking",
            value=(
                "`/bank`\n"
                "`/bankprofile`\n"
                "`/loan`\n"
                "`/loaninfo`"
            ),
            inline=True
        )

        embed.add_field(
            name="💰 Transactions",
            value=(
                "`/deposit <amount>`\n"
                "`/withdraw <amount>`"
            ),
            inline=True
        )

        embed.add_field(
            name="🏛 Vault",
            value=(
                "`/bankupgrade`\n"
                "`/vaults`"
            ),
            inline=True
        )

        embed.add_field(
            name="🏆 Leaderboards",
            value="`/banktop`",
            inline=False
        )

        embed.add_field(
            name="📖 Banking Tips",
            value=(
                "• Store Blood to increase your **Net Worth**.\n"
                "• Upgrade your Vault for more storage.\n"
                "• Repay loans on time to increase **Credit Score**.\n"
                "• Better Credit Score unlocks bigger loans.\n"
                "• Maximum loan is **25% of your Net Worth**."
            ),
            inline=False
        )

        embed.set_image(
            url="https://cdn.discordapp.com/attachments/1530395730387140718/1531536216405708982/header_red_white_red_black_vampire_aesthetic.jpg"
        )

        embed.set_footer(
            text="V4MPYR • Blood Never Sleeps"
        )

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="deposit", description="Deposit Blood")
    async def deposit(self, interaction: discord.Interaction, amount: str):
        success, data = await deposit_blood(interaction.user.id, amount)

        if not success:
            errors = {
                "invalid": "❌ Invalid amount.",
                "blood": "❌ You don't have enough Blood.",
                "capacity": "❌ Your vault is full."
            }
            await interaction.response.send_message(errors[data], ephemeral=True)
            return

        embed = discord.Embed(title="🏦 Deposit Successful", color=0x8B0000)
        embed.description = f"🩸 **{data:,} Blood** has been stored safely."
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="withdraw", description="Withdraw Blood")
    async def withdraw(self, interaction: discord.Interaction, amount: str):
        result = await withdraw_blood(interaction.user.id, amount)

        if not result[0]:
            errors = {
                "invalid": "❌ Invalid amount.",
                "bank": "❌ Not enough Blood in your Blood Bank."
            }
            await interaction.response.send_message(errors[result[1]], ephemeral=True)
            return

        _, receive, tax = result
        embed = discord.Embed(title="🏦 Withdrawal Complete", color=0x8B0000)
        embed.add_field(name="Received", value=f"{receive:,} Blood")
        embed.add_field(name="Tax", value=f"{tax:,} Blood")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="bankupgrade", description="Upgrade your Blood Vault")
    async def bankupgrade(self, interaction: discord.Interaction):
        success = await upgrade_vault(interaction.user.id)

        if success is True:
            _, _, level = await get_bank(interaction.user.id)
            embed = discord.Embed(title="🏛 Vault Upgraded", color=0x990000)
            
            await interaction.response.send_message(embed=embed)
            return

        reason = success[1] if isinstance(success, tuple) else "unknown"
        reasons = {
            "blood": "❌ Not enough Blood.",
            "max": "❌ Maximum Vault reached."
        }
        await interaction.response.send_message(reasons.get(reason, "❌ Upgrade failed."), ephemeral=True)


    @app_commands.command(
        name="vaults",
        description="View every Blood Vault."
    )
    async def vaults(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="🏛 Blood Vaults",
            color=0x8B0000
        )

        names = {
            1:"🪨 Stone Vault",
            2:"⚙️ Iron Vault",
            3:"🥇 Golden Vault",
            4:"💎 Crystal Vault",
            5:"🩸 Blood Vault",
            6:"👑 Royal Treasury"
        }

        for level in range(1,7):
            capacity = VAULT_CAPACITY[level]

            if level == 6:
                cost = "MAX"
                cap = "Unlimited"
            else:
                cost = f"{UPGRADE_COST[level]:,} Blood"
                cap = f"{capacity:,} Blood"

            embed.add_field(
                name=names[level],
                value=f"Capacity: {cap}\nUpgrade: {cost}",
                inline=False
            )

        await interaction.response.send_message(embed=embed)



    @app_commands.command(
        name="loaninfo",
        description="View Blood Bank loan requirements."
    )
    async def loaninfo(self, interaction: discord.Interaction):

        worth = await get_net_worth(interaction.user.id)
        credit = await get_credit_score(interaction.user.id)
        repayments = await get_loan_repayments(interaction.user.id)
        level = await get_level(interaction.user.id)
        current = await get_best_loan_tier(interaction.user.id)

        def eligible(req, have):
            return "✅" if have >= req else "❌"

        embed = discord.Embed(
            title="🏦 V4MPYR Blood Bank • Loan Information",
            description=(
                "Increase your **Net Worth**, **Level**, and **Credit Score** "
                "to unlock bigger loans.\n\n"
                "⚠️ Only **1 Active Loan** is allowed at a time."
            ),
            color=0x8B0000
        )

        embed.set_author(
            name="V4MPYR Blood Bank",
            icon_url=interaction.guild.icon.url if interaction.guild.icon else None
        )

        embed.add_field(
            name="🥉 Starter Loan",
            value=(
                f"{'🟢 ELIGIBLE' if current and current >= 1 else '🔒 LOCKED'}\n\n"
                "💰 **10,000 Blood**\n"
                f"{eligible(5, level)} Level {level}/5\n"
                f"{eligible(100, credit)} Credit {credit}/100\n"
                f"{eligible(40000, worth)} Net Worth {worth:,}/40,000\n"
                "📅 **15 Days**\n"
                "⭐ **Level 5+**\n"
                "💳 **Credit 100+**\n"
                "💎 **40,000 Net Worth**\n"
                "📈 **10% Interest**"
            ),
            inline=True
        )

        embed.add_field(
            name="🥈 Personal Loan",
            value=(
                f"{'🟢 ELIGIBLE' if current and current >= 2 else '🔒 LOCKED'}\n\n"
                "💰 **50,000 Blood**\n"
                f"{eligible(15, level)} Level {level}/15\n"
                f"{eligible(130, credit)} Credit {credit}/130\n"
                f"{eligible(200000, worth)} Net Worth {worth:,}/200,000\n"
                f"{eligible(3, repayments)} Repayments {repayments}/3\n"
                "📅 **30 Days**\n"
                "⭐ **Level 15+**\n"
                "💳 **Credit 130+**\n"
                "💎 **200,000 Net Worth**\n"
                "✅ **3 Repayments**\n"
                "📈 **9% Interest**"
            ),
            inline=True
        )

        embed.add_field(
            name="🥇 Business Loan",
            value=(
                f"{'🟢 ELIGIBLE' if current and current >= 3 else '🔒 LOCKED'}\n\n"
                "💰 **250,000 Blood**\n"
                f"{eligible(30, level)} Level {level}/30\n"
                f"{eligible(180, credit)} Credit {credit}/180\n"
                f"{eligible(1000000, worth)} Net Worth {worth:,}/1,000,000\n"
                f"{eligible(10, repayments)} Repayments {repayments}/10\n"
                "📅 **60 Days**\n"
                "⭐ **Level 30+**\n"
                "💳 **Credit 180+**\n"
                "💎 **1,000,000 Net Worth**\n"
                "✅ **10 Repayments**\n"
                "📈 **8% Interest**"
            ),
            inline=True
        )

        embed.add_field(
            name="💎 Corporate Loan",
            value=(
                f"{'🟢 ELIGIBLE' if current and current >= 4 else '🔒 LOCKED'}\n\n"
                "💰 **1,000,000 Blood**\n"
                "📅 **120 Days**\n"
                "⭐ **Level 50+**\n"
                "💳 **Credit 300+**\n"
                "💎 **5,000,000 Net Worth**\n"
                "✅ **25 Repayments**\n"
                "📈 **7% Interest**"
            ),
            inline=True
        )

        embed.add_field(
            name="👑 Royal Blood Credit",
            value=(
                f"{'🟢 ELIGIBLE' if current and current >= 5 else '🔒 LOCKED'}\n\n"
                "💰 **2,500,000 Blood**\n"
                "📅 **365 Days**\n"
                "⭐ **Level 100+**\n"
                "💳 **Credit 500+**\n"
                "💎 **20,000,000 Net Worth**\n"
                "✅ **50 Repayments**\n"
                "📈 **5% Interest**"
            ),
            inline=False
        )

        embed.add_field(
            name="📜 Blood Bank Rules",
            value=(
                "• Only **1 Active Loan** at a time.\n"
                "• Previous loan must be fully repaid.\n"
                "• Loan cooldown starts after repayment.\n"
                "• Loan amount cannot exceed **25% of your Net Worth**.\n"
                "• Late repayments lower your **Credit Score**.\n"
                "• Higher Credit Score unlocks larger loans with lower interest."
            ),
            inline=False
        )

        embed.set_footer(
            text="🏦 Build Your Reputation • Unlock Bigger Loans"
        )

        await interaction.response.send_message(embed=embed)


    @app_commands.command(
        name="bankprofile",
        description="View your Blood Bank profile."
    )
    async def bankprofile(self, interaction: discord.Interaction):

        (
            blood,
            bank,
            vault,
            credit,
            repayments,
            worth,
            tier,
            defaults,
            cooldown
        ) = await get_bank_profile(interaction.user.id)

        names = {
            1: "🪨 Stone Vault",
            2: "⚙️ Iron Vault",
            3: "🥇 Golden Vault",
            4: "💎 Crystal Vault",
            5: "🩸 Blood Vault",
            6: "👑 Royal Treasury"
        }

        if credit >= 500:
            rating = "🟢 Excellent"
        elif credit >= 300:
            rating = "🔵 Trusted"
        elif credit >= 150:
            rating = "🟡 Good"
        else:
            rating = "🔴 New Customer"

        highest = LOAN_TIERS[tier]["name"] if tier else "None"

        if cooldown > int(time.time()):
            left = (cooldown - int(time.time())) // 86400
            cooldown_text = f"{left} Days"
        else:
            cooldown_text = "None"

        embed = discord.Embed(
            title="🏦 Blood Bank Profile",
            color=0x8B0000
        )

        embed.set_author(
            name=interaction.user.display_name,
            icon_url=interaction.user.display_avatar.url
        )

        embed.add_field(
            name="💳 Credit Score",
            value=f"{credit}\n{rating}",
            inline=True
        )

        embed.add_field(
            name="💎 Net Worth",
            value=f"{worth:,} Blood",
            inline=True
        )

        embed.add_field(
            name="🏛 Vault",
            value=names[vault],
            inline=True
        )

        embed.add_field(
            name="🏦 Stored Blood",
            value=f"{bank:,}",
            inline=True
        )

        embed.add_field(
            name="🩸 Wallet Blood",
            value=f"{blood:,}",
            inline=True
        )

        embed.add_field(
            name="💰 Highest Loan",
            value=highest,
            inline=True
        )

        embed.add_field(
            name="✅ Repayments",
            value=str(repayments),
            inline=True
        )

        embed.add_field(
            name="❌ Defaults",
            value=str(defaults),
            inline=True
        )

        embed.add_field(
            name="⏳ Cooldown",
            value=cooldown_text,
            inline=True
        )

        embed.set_footer(
            text="V4MPYR • Blood Bank"
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Bank(bot))
