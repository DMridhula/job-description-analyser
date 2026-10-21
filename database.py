
import sqlite3

def create_database():
    connection = sqlite3.connect("career_profile.db")

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY,
            skills TEXT,
            projects TEXT,
            certifications TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_profile(skills, projects, certifications):
    connection = sqlite3.connect("career_profile.db")

    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO profile
        (id, skills, projects, certifications)
        VALUES (1, ?, ?, ?)
    """, (skills, projects, certifications))

    connection.commit()
    connection.close()


def load_profile():
    connection = sqlite3.connect("career_profile.db")

    cursor = connection.cursor()

    cursor.execute("""
        SELECT skills, projects, certifications
        FROM profile
        WHERE id = 1
    """)

    result = cursor.fetchone()

    connection.close()

    if result:
        return result

    return ("", "", "")
