import streamlit as st
import sqlite3

# Set page config FIRST
st.set_page_config(page_title="📚 Personal Library", layout="wide")

# Database connection
def get_db_connection():
    conn = sqlite3.connect('library.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create table if not exists
def create_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            publication_year INTEGER,
            genre TEXT,
            read_status BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()

# Add a book
def add_book(title, author, year, genre, read_status):
    conn = get_db_connection()
    conn.execute("INSERT INTO books (title, author, publication_year, genre, read_status) VALUES (?, ?, ?, ?, ?)",
                 (title, author, year, genre, read_status))
    conn.commit()
    conn.close()

# Remove a book
def remove_book(title):
    conn = get_db_connection()
    conn.execute("DELETE FROM books WHERE title = ?", (title,))
    conn.commit()
    conn.close()

# Update a book
def update_book(book_id, title, author, year, genre, read_status):
    conn = get_db_connection()
    conn.execute("""
        UPDATE books
        SET title = ?, author = ?, publication_year = ?, genre = ?, read_status = ?
        WHERE id = ?
    """, (title, author, year, genre, read_status, book_id))
    conn.commit()
    conn.close()

# Search books
def search_book(search_term, search_by):
    conn = get_db_connection()
    query = f"SELECT * FROM books WHERE {search_by.lower()} LIKE ?"
    results = conn.execute(query, (f"%{search_term}%",)).fetchall()
    conn.close()
    return results

# Display all books
def display_books():
    conn = get_db_connection()
    books = conn.execute("SELECT * FROM books").fetchall()
    conn.close()
    return books

# Get library statistics
def display_statistics():
    conn = get_db_connection()
    total_books = conn.execute("SELECT COUNT(*) FROM books").fetchone()[0]
    read_books = conn.execute("SELECT COUNT(*) FROM books WHERE read_status = 1").fetchone()[0]
    unread_books = total_books - read_books
    percentage_read = (read_books / total_books * 100) if total_books > 0 else 0
    conn.close()
    return total_books, read_books, unread_books, percentage_read

# Streamlit app
st.title("📚 Personal Library Manager")

# Sidebar menu
st.sidebar.title("📚 Menu")
menu = st.sidebar.radio("Navigate", ["➕ Add Book", "✏️ Edit Book", "❌ Remove Book", "🔎 Search", "📖 View Library", "📊 Stats"])

# Initialize database
create_table()

# Add Book
if menu == "➕ Add Book":
    st.subheader("📚 Add a Book")
    col1, col2 = st.columns(2)
    with col1:
        title = st.text_input("Book Title")
        author = st.text_input("Author")
    with col2:
        year = st.number_input("Publication Year", min_value=0, max_value=2100, step=1)
        genre = st.text_input("Genre")
    read_status = st.checkbox("Have you read this book?")
    if st.button("Add Book"):
        if title and author and genre:
            add_book(title, author, year, genre, read_status)
            st.success("✅ Book added successfully!")
        else:
            st.error("⚠️ Please fill in all fields!")

# Edit Book
elif menu == "✏️ Edit Book":
    st.subheader("✏️ Edit a Book")
    books = display_books()
    if books:
        book_titles = [book['title'] for book in books]
        selected_title = st.selectbox("Select a book to edit", book_titles)
        selected_book = next(book for book in books if book['title'] == selected_title)
        
        with st.form("edit_form"):
            new_title = st.text_input("Title", value=selected_book['title'])
            new_author = st.text_input("Author", value=selected_book['author'])
            new_year = st.number_input("Publication Year", value=selected_book['publication_year'])
            new_genre = st.text_input("Genre", value=selected_book['genre'])
            new_read_status = st.checkbox("Read Status", value=bool(selected_book['read_status']))
            
            if st.form_submit_button("Update Book"):
                update_book(selected_book['id'], new_title, new_author, new_year, new_genre, new_read_status)
                st.success("✅ Book updated successfully!")
    else:
        st.info("📭 Your library is empty!")

# Remove Book
elif menu == "❌ Remove Book":
    st.subheader("🗑️ Remove a Book")
    title = st.text_input("Enter the title of the book to remove")
    if st.button("Remove Book"):
        if title:
            remove_book(title)
            st.success("🗑️ Book removed successfully!")
        else:
            st.error("⚠️ Please enter a title!")

# Search
elif menu == "🔎 Search":
    st.subheader("🔍 Search for a Book")
    search_by = st.radio("Search by", ["Title", "Author", "Genre", "Year"])
    search_term = st.text_input(f"Enter the {search_by}")
    if st.button("Search"):
        results = search_book(search_term, search_by)
        if results:
            for book in results:
                st.markdown(f"**{book['title']}** by {book['author']} ({book['publication_year']}) - *{book['genre']}*")
        else:
            st.warning("No matching books found!")

# View Library
elif menu == "📖 View Library":
    st.subheader("📚 Your Library")
    books = display_books()
    if books:
        for book in books:
            with st.expander(f"📘 {book['title']} by {book['author']}"):
                st.write(f"**Year:** {book['publication_year']}  |  **Genre:** {book['genre']}")
    else:
        st.info("📭 Your library is empty!")