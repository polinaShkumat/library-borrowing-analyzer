# 📚 Library Borrowing Analyzer

A Python command-line tool that analyses a library's borrowing history from three
plain-text data files. It links students and books by ID (like a JOIN in SQL, but
in pure Python), finds books that are still out, spots frequent borrowers, measures
how long books are kept, and writes a per-student report.

## Example output

```
Loaded 25 books, 30 students, 200 borrow records.

1) First borrow: ['Bram Lopez', 'Emma']
2) Books not returned yet: 28
3) Frequent borrowers (2+): 26 | top 3: Sara Lopez (16), Levi Kovalenko (14), Olena Peters (12)
4) Returned books: 172 | average days kept: 22.99
5) Report for 26 students written to output/student_report.txt
```

`output/student_report.txt`:

```
[student_name, total_books_borrowed, average_return_duration, longest_borrowed_books]
['Uma Vos', 3, 29.0, ['1984']]
['Liam de Vries', 5, 27.75, ['Les Miserables']]
['Sofia Lopez', 3, 14.67, ['The Trial']]
```

## Data format

| File | Columns |
|---|---|
| `data/books.txt` | `book_id, title, author` |
| `data/students.txt` | `student_id, name, email` |
| `data/borrowed.txt` | `student_id, book_id, borrow_date (MM/DD/YY), return_date (empty = not returned)` |

The included data is generated sample data (fake names), so the project runs out of the box.

## How it works

- **Loading** – each file becomes a list of lists with one list comprehension; values are cleaned of spaces, newlines and quotes.
- **ID lookups** – `dict(zip(ids, names))` builds an `{id: name}` dictionary, so every borrow record can be translated from `S001, B015` to `Uma Vos, Hamlet` in one step.
- **Durations** – `datetime.strptime` turns dates into `date` objects; subtracting two dates gives the number of days.
- **Edge cases handled**
  - students who never borrowed are left out of the report
  - students who borrowed but returned nothing get `N/A` instead of a division-by-zero crash
  - ties are kept: if two books were kept equally long, both are listed

## How to run

```bash
python library_analyzer.py
```

Run the tests:

```bash
pip install pytest
pytest -v
```

The tests use a tiny hand-made dataset, so every expected answer (for example the
average of `(10 + 10 + 2) / 3 = 7.33`) can be checked by hand.

## Project structure

```
library-borrowing-analyzer/
├── library_analyzer.py
├── data/
│   ├── books.txt
│   ├── students.txt
│   └── borrowed.txt
└── tests/
    └── test_library.py
```

## What I learned

- `zip`, `dict` and list comprehensions can replace many manual loops.
- Lists are mutable: `s + [count]` creates a new list, while `s.append(count)` would change the original student data.
- Real data has gaps (empty return dates), and the code has to decide what an empty value means.

## Tech

Python 3 (standard library only: `pathlib`, `datetime`) · pytest
