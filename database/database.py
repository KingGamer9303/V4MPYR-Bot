# Updated build
import random
import time
import aiosqlite

DB_NAME = "v4mpyr.db"

VAMPIRE_NAMES = [
    "Dracul",
    "Noctis",
    "Lucien",
    "Cassius",
    "Silas",
    "Vesper",
    "Kael",
    "Orion",
    "Corvus",
    "Damien",
    "Valerius",
    "Azrael",
    "Dante",
    "Raven",
    "Malakai",
]


async def setup_database():
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            blood INTEGER DEFAULT 500,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            messages INTEGER DEFAULT 0
        )
        """)
        await db.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard_config(
           guild_id INTEGER PRIMARY KEY,
           channel_id INTEGER NOT NULL,
           blood_message INTEGER,
           level_message INTEGER,
           messages_message INTEGER,
           stolen_message INTEGER
        )
        """)


        columns = [
            ("today_messages", "INTEGER DEFAULT 0"),
            ("daily_streak", "INTEGER DEFAULT 0"),
            ("voice_time", "INTEGER DEFAULT 0"),
            ("warns", "INTEGER DEFAULT 0"),
            ("vampire_name", "TEXT"),
            ("hunt_enabled", "INTEGER DEFAULT 0"),
            ("protection_until", "INTEGER DEFAULT 0"),
            ("hunt_charges", "INTEGER DEFAULT 3"),
            ("hunt_limit", "INTEGER DEFAULT 3"),
            ("hunt_max_charges", "INTEGER DEFAULT 3"),
            ("hunt_recharge", "INTEGER DEFAULT 0"),
            ("hunt_wins", "INTEGER DEFAULT 0"),
            ("hunt_losses", "INTEGER DEFAULT 0"),
            ("total_hunts", "INTEGER DEFAULT 0"),
            ("blood_stolen", "INTEGER DEFAULT 0"),
            ("blood_lost", "INTEGER DEFAULT 0"),
            ("times_hunted", "INTEGER DEFAULT 0"),
            ("blood_moon", "INTEGER DEFAULT 0"),
            ("bank_blood", "INTEGER DEFAULT 0"),
            ("vault_level", "INTEGER DEFAULT 1"),
            ("loan_amount", "INTEGER DEFAULT 0"),
            ("loan_interest", "INTEGER DEFAULT 0"),
            ("loan_due", "INTEGER DEFAULT 0"),
            ("credit_score", "INTEGER DEFAULT 100"),
            ("loan_repayments", "INTEGER DEFAULT 0"),
            ("loan_defaults", "INTEGER DEFAULT 0"),
            ("loan_cooldown", "INTEGER DEFAULT 0"),
            ("join_date", "INTEGER DEFAULT 0"),
            ("loan_tier", "INTEGER DEFAULT 1"),
            ("last_repayment", "INTEGER DEFAULT 0"),
        ]

        cursor = await db.execute("PRAGMA table_info(users)")
        existing = [row[1] for row in await cursor.fetchall()]

        for name, sql_type in columns:
            if name not in existing:
                await db.execute(
                    f"ALTER TABLE users ADD COLUMN {name} {sql_type}"
                )

        await db.commit()


async def create_user(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
                # Add hunt_limit column if missing
        try:
            await db.execute(
                "ALTER TABLE users ADD COLUMN hunt_limit INTEGER DEFAULT 3"
            )
            await db.commit()
        except:
            pass

        cursor = await db.execute(
            """
            SELECT vampire_name
            FROM users
            WHERE user_id = ?
            """,
            (user_id,)
        )

        user = await cursor.fetchone()

        # New user
        if user is None:
            await db.execute(
                """
                INSERT INTO users(
                    user_id,
                    vampire_name,
                    join_date
                )
                VALUES(?, ?, ?)
                """,
                (
                    user_id,
                    random.choice(VAMPIRE_NAMES),
                    int(time.time())
                )
            )

        # Existing user but no vampire name
        elif not user[0]:
            await db.execute(
                """
                UPDATE users
                SET vampire_name = ?
                WHERE user_id = ?
                """,
                (
                    random.choice(VAMPIRE_NAMES),
                    user_id
                )
            )

        await db.commit()


async def get_balance(user_id):
    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT blood FROM users WHERE user_id=?",
            (user_id,)
        )

        row = await cursor.fetchone()
        return row[0]

async def add_blood(user_id, amount):
    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            UPDATE users
            SET blood = blood + ?
            WHERE user_id = ?
            """,
            (amount, user_id)
        )
        await db.commit()



async def add_xp(user_id, amount):
    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT xp, level
            FROM users
            WHERE user_id = ?
            """,
            (user_id,)
        )

        xp, level = await cursor.fetchone()

        xp += amount
        leveled_up = False

        while True:
            required = 100 + (level * 50)

            if xp < required:
                break

            xp -= required
            level += 1
            leveled_up = True

        await db.execute(
            """
            UPDATE users
            SET
                xp = ?,
                level = ?
            WHERE user_id = ?
            """,
            (
                xp,
                level,
                user_id
            )
        )

        await db.commit()

        return leveled_up, level, xp, required

async def get_level_data(user_id):
    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT
                level,
                xp
            FROM users
            WHERE user_id = ?
            """,
            (user_id,)
        )

        level, xp = await cursor.fetchone()

        required = 100 + (level * 50)

        return level, xp, required


async def get_xp_required(level):
    return 100 + (level * 50)


async def set_level(user_id, level):
    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            UPDATE users
            SET
                level = ?,
                xp = 0
            WHERE user_id = ?
            """,
            (
                level,
                user_id
            )
        )

        await db.commit()

        await db.commit()
async def remove_blood(user_id, amount):
    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            UPDATE users
            SET blood = blood - ?
            WHERE user_id = ?
            """,
            (amount, user_id)
        )
        await db.commit()


async def transfer_blood(sender_id, receiver_id, amount):
    await create_user(sender_id)
    await create_user(receiver_id)

    sender_balance = await get_balance(sender_id)

    if amount <= 0:
        return False, "invalid_amount"

    if sender_balance < amount:
        return False, "insufficient"

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            UPDATE users
            SET blood = blood - ?
            WHERE user_id = ?
            """,
            (amount, sender_id)
        )

        await db.execute(
            """
            UPDATE users
            SET blood = blood + ?
            WHERE user_id = ?
            """,
            (amount, receiver_id)
        )

        await db.commit()

    return True, None


async def add_chat_reward(user_id, reward=True):
    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:

        # Every message
        await db.execute(
            """
            UPDATE users
            SET
                messages = messages + 1,
                today_messages = today_messages + 1
            WHERE user_id = ?
            """,
            (user_id,)
        )

        # Reward only after cooldown
        if reward:

            await db.execute(
                """
                UPDATE users
                SET
                    blood = blood + 2
                WHERE user_id = ?
                """,
                (user_id,)
            )

        await db.commit()


async def get_messages(user_id):
    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            "SELECT messages FROM users WHERE user_id=?",
            (user_id,)
        )

        row = await cursor.fetchone()
        return row[0]




async def get_level_rank(user_id):

    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
        SELECT user_id
        FROM users
        ORDER BY level DESC, xp DESC
        """)

        users = await cursor.fetchall()

    for index, row in enumerate(users, start=1):
        if row[0] == user_id:
            return index

    return len(users)


async def get_level_profile(user_id):

    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
        SELECT
            level,
            xp,
            blood,
            messages
        FROM users
        WHERE user_id=?
        """, (user_id,))

        level, xp, blood, messages = await cursor.fetchone()

    required = 100 + (level * 50)

    rank = await get_level_rank(user_id)

    return (
        level,
        xp,
        required,
        blood,
        messages,
        rank
    )

async def get_profile(user_id):
    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT
                vampire_name,
                blood,
                level,
                xp,
                messages,
                today_messages,
                voice_time,
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
                blood_lost
            FROM users
            WHERE user_id=?
            """,
            (user_id,)
        )

        return await cursor.fetchone()


async def get_rank(user_id):
    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT user_id
            FROM users
            ORDER BY blood DESC
            """
        )

        users = await cursor.fetchall()

    for index, row in enumerate(users, start=1):
        if row[0] == user_id:
            return index

    return len(users)

async def set_hunt_enabled(user_id, enabled):
    await create_user(user_id)
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE users SET hunt_enabled=? WHERE user_id=?",
            (1 if enabled else 0, user_id)
        )
        await db.commit()


async def get_hunt_status(user_id):
    await create_user(user_id)
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT hunt_enabled FROM users WHERE user_id=?",
            (user_id,)
        )
        return bool((await cursor.fetchone())[0])


async def set_protection(user_id, minutes=30):
    await create_user(user_id)

    expires = int(time.time()) + (minutes * 60)

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE users SET protection_until=? WHERE user_id=?",
            (expires, user_id)
        )
        await db.commit()


async def is_protected(user_id):
    await create_user(user_id)
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT protection_until FROM users WHERE user_id=?",
            (user_id,)
        )
        return (await cursor.fetchone())[0] > int(time.time())



async def get_hunt_data(user_id):
    await create_user(user_id)
    async with aiosqlite.connect(DB_NAME) as db:
        cursor=await db.execute("""
        SELECT hunt_enabled,hunt_charges,hunt_recharge,protection_until,
        hunt_wins,hunt_losses,total_hunts,blood_stolen,blood_lost
        FROM users WHERE user_id=?""",(user_id,))
        return await cursor.fetchone()

async def restore_hunt_charges(user_id):

    await create_user(user_id)

    now = int(time.time())

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT
                hunt_charges,
                hunt_recharge,
                hunt_max_charges
            FROM users
            WHERE user_id=?
            """,
            (user_id,)
        )

        data = await cursor.fetchone()

        if not data:
            return

        charges, recharge, max_charges = data

        if charges == 0 and recharge <= now:

            await db.execute(
                """
                UPDATE users
                SET
                    hunt_charges=?,
                    hunt_recharge=0
                WHERE user_id=?
                """,
                (
                    max_charges,
                    user_id
                )
            )

            await db.commit()

async def use_hunt_charge(user_id):
    await restore_hunt_charges(user_id)
    now=int(time.time())
    async with aiosqlite.connect(DB_NAME) as db:
        cursor=await db.execute("SELECT hunt_charges FROM users WHERE user_id=?",(user_id,))
        charges=(await cursor.fetchone())[0]
        if charges<=0:
            return False
        charges-=1
        if charges==0:
            recharge=now+900
            await db.execute("UPDATE users SET hunt_charges=?,hunt_recharge=? WHERE user_id=?",(charges,recharge,user_id))
        else:
            await db.execute("UPDATE users SET hunt_charges=? WHERE user_id=?",(charges,user_id))
        await db.commit()
        return True

async def add_hunt_win(user_id,blood):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET hunt_wins=hunt_wins+1,total_hunts=total_hunts+1,blood_stolen=blood_stolen+? WHERE user_id=?",(blood,user_id))
        await db.commit()

async def add_hunt_loss(user_id,blood):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("UPDATE users SET hunt_losses=hunt_losses+1,total_hunts=total_hunts+1,blood_lost=blood_lost+? WHERE user_id=?",(blood,user_id))
        await db.commit()

async def can_hunt(user_id):
    await restore_hunt_charges(user_id)

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            """
            SELECT hunt_enabled,
                   hunt_charges,
                   hunt_recharge
            FROM users
            WHERE user_id=?
            """,
            (user_id,)
        )

        enabled, charges, recharge = await cursor.fetchone()

    now = int(time.time())

    if not enabled:
        return False, "disabled"

    if charges <= 0:
        return False, recharge - now

    return True, None

async def add_warn(user_id):
    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            UPDATE users
            SET warns = warns + 1
            WHERE user_id = ?
            """,
            (user_id,)
        )
        await db.commit()


async def remove_warn(user_id):
    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            UPDATE users
            SET warns =
                CASE
                    WHEN warns > 0 THEN warns - 1
                    ELSE 0
                END
            WHERE user_id = ?
            """,
            (user_id,)
        )
        await db.commit()


async def get_warns(user_id):
    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT warns FROM users WHERE user_id=?",
            (user_id,)
        )

        return (await cursor.fetchone())[0]

async def set_blood_moon(status):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            UPDATE users
            SET blood_moon=?
            """,
            (1 if status else 0,)
        )
        await db.commit()


async def is_blood_moon():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT blood_moon FROM users LIMIT 1"
        )

        row = await cursor.fetchone()

        return bool(row[0]) if row else False
async def get_blood_moon():
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT blood_moon FROM users LIMIT 1"
        )

        row = await cursor.fetchone()

        if row:
            return bool(row[0])

        return False

async def set_hunt_charges(user_id, amount):
    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            UPDATE users
            SET hunt_charges=?,
                hunt_recharge=0
            WHERE user_id=?
            """,
            (amount, user_id)
        )

        await db.commit()



async def reset_hunt_charges(user_id):

    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            UPDATE users
            SET hunt_charges=3,
                hunt_recharge=0
            WHERE user_id=?
            """,
            (user_id,)
        )

        await db.commit()



async def set_hunt_limit(user_id, amount):

    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            UPDATE users
            SET
                hunt_max_charges=?,
                hunt_charges=?
            WHERE user_id=?
            """,
            (
                amount,
                amount,
                user_id
            )
        )

        await db.commit()



async def reset_hunt_limit(user_id):

    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            UPDATE users
            SET
                hunt_max_charges=3,
                hunt_charges=3,
                hunt_recharge=0
            WHERE user_id=?
            """,
            (user_id,)
        )

        await db.commit()



async def get_hunt_charges(user_id):

    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT
                hunt_charges,
                hunt_max_charges
            FROM users
            WHERE user_id=?
            """,
            (user_id,)
        )

        return await cursor.fetchone()

async def get_blood_leaderboard(limit=10):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT user_id, vampire_name, blood
            FROM users
            ORDER BY blood DESC
            LIMIT ?
        """, (limit,))
        return await cursor.fetchall()


async def get_level_leaderboard(limit=10):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT user_id, vampire_name, level, xp
            FROM users
            ORDER BY level DESC, xp DESC
            LIMIT ?
        """, (limit,))
        return await cursor.fetchall()


async def get_message_leaderboard(limit=10):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT user_id, vampire_name, messages
            FROM users
            ORDER BY messages DESC
            LIMIT ?
        """, (limit,))
        return await cursor.fetchall()


async def get_stolen_leaderboard(limit=10):
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
            SELECT user_id, vampire_name, blood_stolen
            FROM users
            ORDER BY blood_stolen DESC
            LIMIT ?
        """, (limit,))
        return await cursor.fetchall()

async def get_bank_leaderboard(limit=10):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
        SELECT
            user_id,
            vampire_name,
            bank_blood
        FROM users
        ORDER BY bank_blood DESC
        LIMIT ?
        """,(limit,))

        return await cursor.fetchall()
        # =========================
# LEADERBOARD CONFIG
# =========================

async def save_leaderboard(
    guild_id,
    channel_id,
    blood_message,
    level_message,
    messages_message,
    stolen_message
):
    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        INSERT OR REPLACE INTO leaderboard_config
        VALUES(?,?,?,?,?,?)
        """,
        (
            guild_id,
            channel_id,
            blood_message,
            level_message,
            messages_message,
            stolen_message
        ))

        await db.commit()


async def get_leaderboard(guild_id):

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
        SELECT
            channel_id,
            blood_message,
            level_message,
            messages_message,
            stolen_message
        FROM leaderboard_config
        WHERE guild_id=?
        """,(guild_id,))

        return await cursor.fetchone()


async def get_all_leaderboards():

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
        SELECT
            guild_id,
            channel_id,
            blood_message,
            level_message,
            messages_message,
            stolen_message
        FROM leaderboard_config
        """)

        return await cursor.fetchall()

async def get_loan(user_id):

    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
        SELECT
            loan_amount,
            loan_interest,
            loan_due,
            credit_score,
            loan_repayments,
            loan_cooldown,
            loan_tier
        FROM users
        WHERE user_id=?
        """, (user_id,))

        return await cursor.fetchone()


async def take_loan(user_id, amount):
    await create_user(user_id)

    ok, data = await can_take_loan(user_id, amount)

    if not ok:
        return False, data

    tier = await get_best_loan_tier(user_id)

    tier_data = LOAN_TIERS[tier]

    interest = int(amount * (tier_data["interest"] / 100))

    due = int(time.time()) + (tier_data["days"] * 86400)

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute("""
        UPDATE users
        SET
            blood = blood + ?,
            loan_amount = ?,
            loan_interest = ?,
            loan_due = ?,
            loan_tier = ?
        WHERE user_id = ?
        """,
        (
            amount,
            amount,
            interest,
            due,
            tier,
            user_id
        ))

        await db.commit()

    return True, tier_data



async def repay_loan(user_id, amount):
    await create_user(user_id)

    loan_amount, interest, due, credit, _, _, _ = await get_loan(user_id)

    total = loan_amount + interest

    if total <= 0:
        return False, "no_loan"

    balance = await get_balance(user_id)

    if amount > balance:
        return False, "no_blood"

    if amount > total:
        amount = total

    remaining = total - amount

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE users SET blood=blood-? WHERE user_id=?",
            (amount, user_id)
        )

        if remaining == 0:
            await db.execute("""
                UPDATE users
                SET loan_amount=0,
                    loan_interest=0,
                    loan_due=0,
                    credit_score=credit_score+5,
                    loan_amount=0,
                    loan_interest=0,
                    loan_due=0,
                    loan_repayments=loan_repayments+1,
                    last_repayment=?,
                    loan_cooldown=?
                WHERE user_id=?
            """, (
                int(time.time()),
                int(time.time()) + (7 * 86400),
                user_id
            ))
        else:
            principal = max(0, remaining - interest)
            new_interest = max(0, remaining - principal)

            await db.execute("""
                UPDATE users
                SET loan_amount=?,
                    loan_interest=?
                WHERE user_id=?
            """, (principal, new_interest, user_id))

        await db.commit()

    return True, remaining


VAULT_CAPACITY = {
    1:25000,
    2:100000,
    3:500000,
    4:2000000,
    5:10000000,
    6:999999999999
}



async def get_level(user_id):

    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
        SELECT level
        FROM users
        WHERE user_id=?
        """,(user_id,))

        return (await cursor.fetchone())[0]


async def get_net_worth(user_id):

    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
        SELECT blood, bank_blood
        FROM users
        WHERE user_id=?
        """,(user_id,))

        blood, bank = await cursor.fetchone()
        return blood + bank


async def get_credit_score(user_id):

    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT credit_score FROM users WHERE user_id=?",
            (user_id,)
        )

        return (await cursor.fetchone())[0]


async def get_loan_repayments(user_id):

    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT loan_repayments FROM users WHERE user_id=?",
            (user_id,)
        )

        return (await cursor.fetchone())[0]


async def get_join_days(user_id):

    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT join_date FROM users WHERE user_id=?",
            (user_id,)
        )

        join = (await cursor.fetchone())[0]

    return (int(time.time()) - join) // 86400


async def loan_on_cooldown(user_id):

    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute(
            "SELECT loan_cooldown FROM users WHERE user_id=?",
            (user_id,)
        )

        cooldown = (await cursor.fetchone())[0]

    return cooldown > int(time.time())


async def set_loan_cooldown(user_id, days):

    await create_user(user_id)

    expires = int(time.time()) + (days * 86400)

    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            "UPDATE users SET loan_cooldown=? WHERE user_id=?",
            (expires, user_id)
        )

        await db.commit()



LOAN_TIERS = {
    1: {
        "emoji": "🥉",
        "name": "Starter",
        "max": 10000,
        "interest": 10,
        "days": 15,
        "level": 5,
        "credit": 100,
        "worth": 40000,
        "repayments": 0
    },
    2: {
        "emoji": "🥈",
        "name": "Personal",
        "max": 50000,
        "interest": 9,
        "days": 30,
        "level": 15,
        "credit": 130,
        "worth": 200000,
        "repayments": 3
    },
    3: {
        "emoji": "🥇",
        "name": "Business",
        "max": 250000,
        "interest": 8,
        "days": 60,
        "level": 30,
        "credit": 180,
        "worth": 1000000,
        "repayments": 10
    },
    4: {
        "emoji": "💎",
        "name": "Corporate",
        "max": 1000000,
        "interest": 7,
        "days": 120,
        "level": 50,
        "credit": 300,
        "worth": 5000000,
        "repayments": 25
    },
    5: {
        "emoji": "👑",
        "name": "Royal",
        "max": 2500000,
        "interest": 5,
        "days": 365,
        "level": 100,
        "credit": 500,
        "worth": 20000000,
        "repayments": 50
    }
}


async def get_best_loan_tier(user_id):

    worth = await get_net_worth(user_id)
    credit = await get_credit_score(user_id)
    repayments = await get_loan_repayments(user_id)
    level = await get_level(user_id)

    unlocked = None

    for tier, data in LOAN_TIERS.items():

        if (
            worth >= data["worth"] and
            credit >= data["credit"] and
            repayments >= data["repayments"] and
            level >= data["level"]
        ):
            unlocked = tier

    return unlocked


async def can_take_loan(user_id, amount):

    if await loan_on_cooldown(user_id):
        return False, "cooldown"

    loan = await get_loan(user_id)

    if loan[0] > 0:
        return False, "active"

    tier = await get_best_loan_tier(user_id)

    if tier is None:
        return False, "locked"

    data = LOAN_TIERS[tier]

    if amount > data["max"]:
        return False, "limit"

    worth = await get_net_worth(user_id)

    if amount > worth * 0.25:
        return False, "worth"

    return True, data


async def get_bank(user_id):

    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("""
        SELECT
            blood,
            bank_blood,
            vault_level
        FROM users
        WHERE user_id=?
        """,(user_id,))

        return await cursor.fetchone()


async def deposit_blood(user_id, amount):

    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
        SELECT blood, bank_blood, vault_level
        FROM users
        WHERE user_id=?
        """,(user_id,))

        blood, bank, level = await cursor.fetchone()

        if amount == "all":
            amount = blood

        amount = int(amount)

        if amount <= 0:
            return False, "invalid"

        if blood < amount:
            return False, "blood"

        if bank + amount > VAULT_CAPACITY[level]:
            return False, "capacity"

        await db.execute("""
        UPDATE users
        SET blood=blood-?,
            bank_blood=bank_blood+?
        WHERE user_id=?
        """,(amount, amount, user_id))

        await db.commit()

        return True, amount


async def withdraw_blood(user_id, amount):

    await create_user(user_id)

    TAX = 0.02

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            "SELECT bank_blood FROM users WHERE user_id=?",
            (user_id,)
        )

        bank = (await cursor.fetchone())[0]

        if amount == "all":
            amount = bank

        amount = int(amount)

        if amount <= 0:
            return False, "invalid"

        if bank < amount:
            return False, "bank"

        tax = int(amount * TAX)
        receive = amount - tax

        await db.execute("""
        UPDATE users
        SET bank_blood=bank_blood-?,
            blood=blood+?
        WHERE user_id=?
        """,(amount, receive, user_id))

        await db.commit()

        return True, receive, tax


UPGRADE_COST = {
    1:10000,
    2:50000,
    3:150000,
    4:500000,
    5:2000000
}


async def upgrade_vault(user_id):

    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            "SELECT blood, vault_level FROM users WHERE user_id=?",
            (user_id,)
        )

        blood, level = await cursor.fetchone()

        if level >= 6:
            return False, "max"

        cost = UPGRADE_COST[level]

        if blood < cost:
            return False, "blood"

        await db.execute("""
        UPDATE users
        SET blood=blood-?,
            vault_level=vault_level+1
        WHERE user_id=?
        """,(cost, user_id))

        await db.commit()

        return True


def get_vault_name(level):

    names = {
        1:"🪨 Stone Vault",
        2:"⚙️ Iron Vault",
        3:"🥇 Golden Vault",
        4:"💎 Crystal Vault",
        5:"🩸 Blood Vault",
        6:"👑 Royal Treasury"
    }

    return names[level]

async def process_overdue_loans():

    now = int(time.time())

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
        SELECT
            user_id,
            loan_amount,
            loan_interest,
            loan_due,
            credit_score
        FROM users
        WHERE loan_amount > 0
        """)

        loans = await cursor.fetchall()

        for user_id, amount, interest, due, credit in loans:

            if due == 0:
                continue

            if due > now:
                continue

            new_interest = interest + int(amount * 0.05)

            new_credit = max(0, credit - 10)

            new_due = now + (24 * 60 * 60)

            await db.execute("""
            UPDATE users
            SET
                loan_interest=?,
                credit_score=?,
                loan_due=?
            WHERE user_id=?
            """,
            (
                new_interest,
                new_credit,
                new_due,
                user_id
            ))

        await db.commit()


async def get_bank_profile(user_id):

    await create_user(user_id)

    blood, bank, vault = await get_bank(user_id)

    credit = await get_credit_score(user_id)

    repayments = await get_loan_repayments(user_id)

    worth = await get_net_worth(user_id)

    tier = await get_best_loan_tier(user_id)

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute("""
        SELECT
            loan_defaults,
            loan_cooldown
        FROM users
        WHERE user_id=?
        """,(user_id,))

        defaults, cooldown = await cursor.fetchone()

    return (
        blood,
        bank,
        vault,
        credit,
        repayments,
        worth,
        tier,
        defaults,
        cooldown
    )


def get_progress_bar(current, maximum):

    if maximum <= 0:
        return "██████████"

    percent = current / maximum

    filled = int(percent * 10)

    return "█" * filled + "░" * (10 - filled)

async def reset_xp(user_id):
    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            UPDATE users
            SET
                level = 1,
                xp = 0
            WHERE user_id = ?
            """,
            (user_id,)
        )

        await db.commit()


async def add_raw_xp(user_id, amount):
    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            """
            SELECT xp
            FROM users
            WHERE user_id = ?
            """,
            (user_id,)
        )

        xp = (await cursor.fetchone())[0]

        xp += amount

        if xp < 0:
            xp = 0

        await db.execute(
            """
            UPDATE users
            SET xp = ?
            WHERE user_id = ?
            """,
            (
                xp,
                user_id
            )
        )

        await db.commit()


async def set_xp(user_id, amount):
    await create_user(user_id)

    async with aiosqlite.connect(DB_NAME) as db:

        await db.execute(
            """
            UPDATE users
            SET xp = ?
            WHERE user_id = ?
            """,
            (
                max(0, amount),
                user_id
            )
        )

        await db.commit()