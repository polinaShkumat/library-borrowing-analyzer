"""Library Borrowing Analyzer.

Reads three CSV-style text files (books, students, borrow records) and answers:
  1. Who borrowed which book?
  2. Which books are still not returned?
  3. Who borrows often (2+ times)?
  4. How long are books kept on average?
  5. A per-student report, written to output/student_report.txt
"""
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"


# ---------- loading ----------

def clean(raw_value):
    """Remove spaces, newlines and quotes around a value."""
    return raw_value.strip().strip('"')


def load_file(path):
    """Read a file into a list of lists. Skips the header and empty lines."""
    with path.open("r", encoding="utf-8") as f:
        next(f)  # skip the header
        return [[clean(value) for value in line.split(",")] for line in f if line.strip()]


def make_lookup(rows):
    """{id: name} from the first two columns, e.g. {'S001': 'Uma Vos'}."""
    ids = [row[0] for row in rows]
    names = [row[1] for row in rows]
    return dict(zip(ids, names))


# ---------- 1. who borrowed what ----------

def book_student_mapping(borrowed, student_lookup, book_lookup):
    return [[student_lookup[r[0]], book_lookup[r[1]]] for r in borrowed]


# ---------- 2. not returned yet ----------

def currently_borrowed(borrowed):
    """A record with an empty return date means the book is still out."""
    return [r for r in borrowed if r[3] == ""]


# ---------- 3. frequent borrowers ----------

def frequent_borrowers(students, borrowed):
    """Students with 2 or more borrows, with their count added at the end."""
    borrowed_ids = [r[0] for r in borrowed]
    return [s + [borrowed_ids.count(s[0])] for s in students if borrowed_ids.count(s[0]) >= 2]


# ---------- 4. borrow durations ----------

def to_date(text):
    return datetime.strptime(text, "%m/%d/%y").date()


def borrow_durations(borrowed, book_lookup):
    """Days each returned book was kept, paired with its title, plus the average."""
    returned = [r for r in borrowed if r[3] != ""]
    durations = [(to_date(r[3]) - to_date(r[2])).days for r in returned]
    book_titles = [book_lookup[r[1]] for r in returned]
    durations_with_books = list(zip(durations, book_titles))
    average = sum(durations) / len(durations) if durations else 0
    return durations_with_books, average


# ---------- 5. per-student report ----------

def student_summary(student, borrowed, book_lookup):
    """[name, total borrows, average days kept, book(s) kept the longest]."""
    student_id, name = student[0], student[1]
    records = [r for r in borrowed if r[0] == student_id]
    returned = [r for r in records if r[3] != ""]
    durations = [(to_date(r[3]) - to_date(r[2])).days for r in returned]
    titles = [book_lookup[r[1]] for r in returned]

    if durations:
        average = round(sum(durations) / len(durations), 2)
        longest = max(durations)
        # a tie is possible, so keep every book with the longest duration
        longest_books = [title for days, title in zip(durations, titles) if days == longest]
    else:
        average = "N/A"   # borrowed, but nothing returned yet
        longest_books = []
    return [name, len(records), average, longest_books]


def build_summary(students, borrowed, book_lookup):
    """Summary only for students who borrowed at least once."""
    borrowed_ids = [r[0] for r in borrowed]
    return [student_summary(s, borrowed, book_lookup) for s in students if s[0] in borrowed_ids]


def write_report(summary, path):
    path.parent.mkdir(exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("[student_name, total_books_borrowed, average_return_duration, longest_borrowed_books]\n")
        for record in summary:
            f.write(f"{record}\n")


# ---------- main ----------

def main():
    try:
        books = load_file(DATA_DIR / "books.txt")
        students = load_file(DATA_DIR / "students.txt")
        borrowed = load_file(DATA_DIR / "borrowed.txt")
    except FileNotFoundError as error:
        print(f"Data file not found: {error.filename}")
        return

    student_lookup = make_lookup(students)
    book_lookup = make_lookup(books)

    print(f"Loaded {len(books)} books, {len(students)} students, {len(borrowed)} borrow records.\n")

    mapping = book_student_mapping(borrowed, student_lookup, book_lookup)
    print("1) First borrow:", mapping[0])

    current = currently_borrowed(borrowed)
    print(f"2) Books not returned yet: {len(current)}")

    frequent = frequent_borrowers(students, borrowed)
    top = sorted(frequent, key=lambda s: s[-1], reverse=True)[:3]
    print(f"3) Frequent borrowers (2+): {len(frequent)} | top 3: "
          + ", ".join(f"{s[1]} ({s[-1]})" for s in top))

    durations_with_books, average = borrow_durations(borrowed, book_lookup)
    print(f"4) Returned books: {len(durations_with_books)} | average days kept: {average:.2f}")

    summary = build_summary(students, borrowed, book_lookup)
    report_path = OUTPUT_DIR / "student_report.txt"
    write_report(summary, report_path)
    print(f"5) Report for {len(summary)} students written to {report_path.relative_to(BASE_DIR)}")


if __name__ == "__main__":
    main()
