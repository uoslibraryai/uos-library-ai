"""UOS Library AI - database.py
SQLite database for the Library Assistant Chatbot (student demo project).

Rule: book availability ALWAYS comes from this SQLite database only.
The app must never invent a book or an availability status.
All 80 books below are DEMONSTRATION / SAMPLE data, clearly labelled
in the app. They are not real University of Sargodha library records.
"""

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library.db")

# (title, author, subject, isbn, publisher, year, shelf, total_copies, available_copies)
BOOKS = [
    # ---- Computer Science: 18 ----
    ("Introduction to Algorithms", "Thomas H. Cormen", "Computer Science", "978-0262033848", "MIT Press", 2009, "CS-A1", 5, 3),
    ("Computer Networking: A Top-Down Approach", "James F. Kurose", "Computer Science", "978-0133594140", "Pearson", 2017, "CS-A2", 4, 2),
    ("Operating System Concepts", "Abraham Silberschatz", "Computer Science", "978-1118063330", "Wiley", 2012, "CS-A3", 5, 0),
    ("Database System Concepts", "Abraham Silberschatz", "Computer Science", "978-0073523323", "McGraw-Hill", 2010, "CS-A4", 4, 1),
    ("Artificial Intelligence: A Modern Approach", "Stuart Russell", "Computer Science", "978-0134610993", "Pearson", 2020, "CS-B1", 5, 4),
    ("Python Crash Course", "Eric Matthes", "Computer Science", "978-1593279288", "No Starch Press", 2019, "CS-B2", 6, 5),
    ("Clean Code", "Robert C. Martin", "Computer Science", "978-0132350884", "Prentice Hall", 2008, "CS-B3", 4, 2),
    ("Computer Organization and Design", "David A. Patterson", "Computer Science", "978-0124077263", "Morgan Kaufmann", 2013, "CS-B4", 3, 1),
    ("Data Structures and Algorithms in Python", "Michael T. Goodrich", "Computer Science", "978-1118290279", "Wiley", 2013, "CS-C1", 4, 3),
    ("The C Programming Language", "Brian W. Kernighan", "Computer Science", "978-0131103627", "Prentice Hall", 1988, "CS-C2", 5, 2),
    ("Design Patterns", "Erich Gamma", "Computer Science", "978-0201633610", "Addison-Wesley", 1994, "CS-C3", 3, 0),
    ("Introduction to the Theory of Computation", "Michael Sipser", "Computer Science", "978-1133187790", "Cengage", 2012, "CS-C4", 3, 2),
    ("Operating Systems: Three Easy Pieces", "Remzi H. Arpaci-Dusseau", "Computer Science", "978-1985086593", "Arpaci-Dusseau Books", 2018, "CS-D1", 4, 3),
    ("Deep Learning", "Ian Goodfellow", "Computer Science", "978-0262035613", "MIT Press", 2016, "CS-D2", 3, 1),
    ("Machine Learning", "Tom M. Mitchell", "Computer Science", "978-0070428072", "McGraw-Hill", 1997, "CS-D3", 4, 2),
    ("Software Engineering", "Ian Sommerville", "Computer Science", "978-0133943030", "Pearson", 2015, "CS-D4", 5, 3),
    ("Computer Networks", "Andrew S. Tanenbaum", "Computer Science", "978-0132126953", "Pearson", 2010, "CS-E1", 4, 1),
    ("Discrete Mathematics and Its Applications", "Kenneth H. Rosen", "Computer Science", "978-0073399110", "McGraw-Hill", 2018, "CS-E2", 5, 4),
    # ---- Information Management: 12 ----
    ("Management Information Systems", "Kenneth C. Laudon", "Information Management", "978-0134639710", "Pearson", 2017, "IM-A1", 4, 2),
    ("Information Systems Today", "Joseph Valacich", "Information Management", "978-0134638527", "Pearson", 2017, "IM-A2", 3, 1),
    ("Fundamentals of Database Systems", "Ramez Elmasri", "Information Management", "978-0133970777", "Pearson", 2015, "IM-A3", 5, 3),
    ("Database Management Systems", "Raghu Ramakrishnan", "Information Management", "978-0072465631", "McGraw-Hill", 2002, "IM-A4", 4, 0),
    ("Information Management: A Practical Guide", "David J. Pauleen", "Information Management", "978-0415787652", "Routledge", 2013, "IM-B1", 3, 2),
    ("Knowledge Management in Theory and Practice", "Kimiz Dalkir", "Information Management", "978-0262015080", "MIT Press", 2011, "IM-B2", 3, 1),
    ("Information Retrieval: Implementing and Evaluating Search Engines", "Stefan Buttcher", "Information Management", "978-0262027268", "MIT Press", 2010, "IM-B3", 3, 2),
    ("Business Intelligence and Analytics", "Ramesh Sharda", "Information Management", "978-0133050905", "Pearson", 2013, "IM-B4", 4, 3),
    ("Data Mining: Concepts and Techniques", "Jiawei Han", "Information Management", "978-0123814791", "Morgan Kaufmann", 2011, "IM-C1", 4, 2),
    ("Information Systems for Business", "R. Kelly Rainer", "Information Management", "978-1118674361", "Wiley", 2013, "IM-C2", 3, 1),
    ("Records and Information Management", "Patricia C. Franks", "Information Management", "978-1555709109", "Neal-Schuman", 2013, "IM-C3", 3, 0),
    ("Digital Libraries and Information Access", "G. G. Chowdhury", "Information Management", "978-1856046598", "Facet Publishing", 2009, "IM-C4", 3, 2),
    # ---- Library Science: 12 ----
    ("Foundations of Library and Information Science", "Richard E. Rubin", "Library Science", "978-1555709733", "Neal-Schuman", 2016, "LS-A1", 4, 3),
    ("Introduction to Cataloging and Classification", "Arlene G. Taylor", "Library Science", "978-1591582357", "Libraries Unlimited", 2006, "LS-A2", 3, 1),
    ("The Organization of Information", "Arlene G. Taylor", "Library Science", "978-1591587006", "Libraries Unlimited", 2008, "LS-A3", 3, 2),
    ("Library and Information Center Management", "Barbara B. Moran", "Library Science", "978-1591588084", "Libraries Unlimited", 2012, "LS-A4", 4, 2),
    ("Reference and Information Services", "Kay Ann Cassell", "Library Science", "978-0838911566", "ALA Neal-Schuman", 2013, "LS-B1", 3, 1),
    ("Collection Development and Management for 21st Century Library Collections", "Vicki L. Gregory", "Library Science", "978-0838911719", "ALA Editions", 2011, "LS-B2", 3, 0),
    ("Library Services for Children and Young Adults", "Carol A. Doll", "Library Science", "978-1591586508", "Libraries Unlimited", 2009, "LS-B3", 3, 2),
    ("Information Literacy: A Practical Guide", "Esther S. Grassian", "Library Science", "978-1555706603", "Neal-Schuman", 2009, "LS-B4", 3, 1),
    ("Academic Librarianship in the 21st Century", "Tom Diamond", "Library Science", "978-1591588366", "Libraries Unlimited", 2010, "LS-C1", 3, 2),
    ("Metadata for Digital Collections", "Michael M. H. Miller", "Library Science", "978-1555707460", "Neal-Schuman", 2011, "LS-C2", 3, 1),
    ("Library Management: A Practical Approach", "Diane L. Velasquez", "Library Science", "978-1555708767", "Neal-Schuman", 2013, "LS-C3", 3, 2),
    ("Introduction to Library Services", "Maggie C. Farrell", "Library Science", "978-1591587086", "Libraries Unlimited", 2010, "LS-C4", 3, 3),
    # ---- Business: 13 ----
    ("Principles of Management", "Stephen P. Robbins", "Business", "978-0134527604", "Pearson", 2016, "BU-A1", 5, 3),
    ("Marketing Management", "Philip Kotler", "Business", "978-0133856460", "Pearson", 2015, "BU-A2", 5, 2),
    ("Principles of Marketing", "Philip Kotler", "Business", "978-0134492513", "Pearson", 2017, "BU-A3", 4, 1),
    ("Financial Management: Theory and Practice", "Eugene F. Brigham", "Business", "978-1305632295", "Cengage", 2016, "BU-A4", 4, 0),
    ("Organizational Behavior", "Stephen P. Robbins", "Business", "978-0134103983", "Pearson", 2016, "BU-B1", 4, 2),
    ("Human Resource Management", "Gary Dessler", "Business", "978-0134235457", "Pearson", 2016, "BU-B2", 4, 3),
    ("Strategic Management", "Fred R. David", "Business", "978-0134153971", "Pearson", 2016, "BU-B3", 3, 1),
    ("Principles of Economics", "N. Gregory Mankiw", "Business", "978-1305585126", "Cengage", 2017, "BU-B4", 5, 4),
    ("Business Communication", "Courtland L. Bovee", "Business", "978-0133864800", "Pearson", 2015, "BU-C1", 3, 2),
    ("Entrepreneurship: Theory, Process, and Practice", "Donald F. Kuratko", "Business", "978-1285051758", "Cengage", 2013, "BU-C2", 3, 1),
    ("Operations Management", "Jay Heizer", "Business", "978-0134130422", "Pearson", 2016, "BU-C3", 4, 2),
    ("Accounting Principles", "Jerry J. Weygandt", "Business", "978-1118162632", "Wiley", 2012, "BU-C4", 4, 3),
    ("Business Ethics: Concepts and Cases", "Manuel G. Velasquez", "Business", "978-0133832390", "Pearson", 2013, "BU-D1", 3, 1),
    # ---- Engineering: 13 ----
    ("Engineering Mechanics: Statics", "J. L. Meriam", "Engineering", "978-1118919736", "Wiley", 2014, "EN-A1", 4, 2),
    ("Engineering Mechanics: Dynamics", "J. L. Meriam", "Engineering", "978-1118885840", "Wiley", 2014, "EN-A2", 4, 1),
    ("Fundamentals of Electric Circuits", "Charles K. Alexander", "Engineering", "978-0078028229", "McGraw-Hill", 2012, "EN-A3", 5, 3),
    ("Mechanical Engineering Design", "Richard G. Budynas", "Engineering", "978-0073398204", "McGraw-Hill", 2014, "EN-A4", 4, 2),
    ("Thermodynamics: An Engineering Approach", "Yunus A. Cengel", "Engineering", "978-0073398174", "McGraw-Hill", 2014, "EN-B1", 5, 0),
    ("Signals and Systems", "Alan V. Oppenheim", "Engineering", "978-0138147570", "Prentice Hall", 1996, "EN-B2", 4, 1),
    ("Digital Design", "M. Morris Mano", "Engineering", "978-0132774208", "Pearson", 2012, "EN-B3", 4, 3),
    ("Introduction to Electrical Engineering", "Mulukutla S. Sarma", "Engineering", "978-0195136042", "Oxford University Press", 2001, "EN-B4", 3, 2),
    ("Structural Analysis", "Russell C. Hibbeler", "Engineering", "978-0133942842", "Pearson", 2014, "EN-C1", 4, 2),
    ("Fluid Mechanics", "Frank M. White", "Engineering", "978-0073398273", "McGraw-Hill", 2015, "EN-C2", 4, 1),
    ("Control Systems Engineering", "Norman S. Nise", "Engineering", "978-1118170516", "Wiley", 2010, "EN-C3", 3, 2),
    ("Engineering Mathematics", "K. A. Stroud", "Engineering", "978-0831130826", "Industrial Press", 2007, "EN-C4", 5, 4),
    ("Materials Science and Engineering", "William D. Callister", "Engineering", "978-1118324578", "Wiley", 2013, "EN-D1", 4, 3),
    # ---- English: 12 ----
    ("The Elements of Style", "William Strunk Jr.", "English", "978-0205309023", "Pearson", 1999, "ENL-A1", 4, 3),
    ("English Grammar in Use", "Raymond Murphy", "English", "978-0521189064", "Cambridge University Press", 2012, "ENL-A2", 6, 5),
    ("Practical English Usage", "Michael Swan", "English", "978-0194420980", "Oxford University Press", 2005, "ENL-A3", 4, 2),
    ("A History of English Literature", "Michael Alexander", "English", "978-0333681876", "Palgrave Macmillan", 2000, "ENL-A4", 3, 1),
    ("The Norton Anthology of English Literature", "Stephen Greenblatt", "English", "978-0393913002", "W. W. Norton", 2012, "ENL-B1", 3, 0),
    ("Academic Writing for Graduate Students", "John M. Swales", "English", "978-0472034758", "University of Michigan Press", 2012, "ENL-B2", 4, 2),
    ("How to Write Better Essays", "Bryan Greetham", "English", "978-0230393902", "Palgrave Macmillan", 2013, "ENL-B3", 3, 1),
    ("English for Academic Purposes", "R. R. Jordan", "English", "978-0521595217", "Cambridge University Press", 1997, "ENL-B4", 3, 2),
    ("The Study of Language", "George Yule", "English", "978-1107652937", "Cambridge University Press", 2014, "ENL-C1", 4, 3),
    ("Literary Theory: A Very Short Introduction", "Jonathan Culler", "English", "978-0199691345", "Oxford University Press", 2011, "ENL-C2", 3, 1),
    ("Creative Writing: A Workbook with Readings", "Linda Anderson", "English", "978-0415554057", "Routledge", 2006, "ENL-C3", 3, 2),
    ("Oxford Advanced Learner's Dictionary", "A. S. Hornby", "English", "978-0194799003", "Oxford University Press", 2015, "ENL-C4", 5, 4),
]


def get_connection(db_path=DB_PATH):
    """Return a SQLite connection with row access by column name."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path=DB_PATH):
    """Safely create the books table and load the 80 demo books.

    Safe initialization (never destructive):
    - The table is created only if it does not already exist.
    - The demo books are inserted only when the table is empty.
    - Existing tables and book records are always preserved, so
      running this function again never deletes or duplicates books.
    Returns the total number of books in the table after initialization.
    """
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            subject TEXT NOT NULL,
            isbn TEXT,
            publisher TEXT,
            year INTEGER,
            shelf_location TEXT,
            total_copies INTEGER NOT NULL,
            available_copies INTEGER NOT NULL
        )
        """
    )
    # Insert the demo books ONLY when the table is empty.
    # If books already exist, leave every existing record untouched.
    cur.execute("SELECT COUNT(*) FROM books")
    total = cur.fetchone()[0]
    if total == 0:
        cur.executemany(
            """INSERT INTO books
               (title, author, subject, isbn, publisher, year,
                shelf_location, total_copies, available_copies)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            BOOKS,
        )
        conn.commit()
        total = len(BOOKS)
    conn.close()
    return total


def search_books(query, search_by="all", db_path=DB_PATH):
    """Search SQLite only. search_by: title | author | subject | all.
    Returns a list of dicts. Empty list means 'not found in demo data' -
    the app must say that, never invent a book.
    """
    q = f"%{query.strip()}%"
    conn = get_connection(db_path)
    cur = conn.cursor()
    if search_by == "title":
        cur.execute("SELECT * FROM books WHERE title LIKE ? COLLATE NOCASE", (q,))
    elif search_by == "author":
        cur.execute("SELECT * FROM books WHERE author LIKE ? COLLATE NOCASE", (q,))
    elif search_by == "subject":
        cur.execute("SELECT * FROM books WHERE subject LIKE ? COLLATE NOCASE", (q,))
    else:
        cur.execute(
            """SELECT * FROM books
               WHERE title LIKE ? COLLATE NOCASE
                  OR author LIKE ? COLLATE NOCASE
                  OR subject LIKE ? COLLATE NOCASE""",
            (q, q, q),
        )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def count_by_subject(db_path=DB_PATH):
    conn = get_connection(db_path)
    cur = conn.cursor()
    cur.execute("SELECT subject, COUNT(*) AS n FROM books GROUP BY subject ORDER BY subject")
    result = {r["subject"]: r["n"] for r in cur.fetchall()}
    conn.close()
    return result


if __name__ == "__main__":
    print(f"Loaded {init_db()} demo books into {DB_PATH}")
    print(count_by_subject())
