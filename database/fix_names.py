import asyncio
import random
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
    "Alaric",
    "Astaroth",
    "Balthazar",
    "Cedric",
    "Cyrus",
    "Darius",
    "Draven",
    "Erebus",
    "Evander",
    "Fenrir",
    "Gideon",
    "Hadrian",
    "Ignatius",
    "Iskander",
    "Jareth",
    "Kieran",
    "Leoric",
    "Lysander",
    "Magnus",
    "Mordecai",
    "Nero",
    "Nyx",
    "Obsidian",
    "Oberon",
    "Phantom",
    "Raith",
    "Ragnar",
    "Sable",
    "Salem",
    "Soren",
    "Thorne",
    "Umbra",
    "Varian",
    "Vlad",
    "Voltaire",
    "Xavian",
    "Zephyr",
    "Zarek",
    "Zavian",
    "Morvane"
]

async def main():
    async with aiosqlite.connect(DB_NAME) as db:

        cursor = await db.execute(
            "SELECT user_id FROM users WHERE vampire_name IS NULL"
        )

        users = await cursor.fetchall()

        available_names = VAMPIRE_NAMES.copy()
        random.shuffle(available_names)

        for i, (user_id,) in enumerate(users):

            if i >= len(available_names):
                # If names run out, reuse randomly
                name = random.choice(VAMPIRE_NAMES)
            else:
                name = available_names[i]

            await db.execute(
                """
                UPDATE users
                SET vampire_name = ?
                WHERE user_id = ?
                """,
                (name, user_id)
            )

        await db.commit()

    print(f"✅ Assigned vampire names to {len(users)} user(s)!")

if __name__ == "__main__":
    asyncio.run(main())