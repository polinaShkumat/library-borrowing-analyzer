"""Tests with small hand-made data, so every expected answer can be checked by hand."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import library_analyzer as lib

STUDENTS = [["S1", "Anna"], ["S2", "Bob"], ["S3", "Eva"]]
BOOKS = {"B1": "Dune", "B2": "1984", "B3": "Emma"}
BORROWED = [
    ["S1", "B1", "01/01/24", "01/11/24"],   # 10 days
    ["S1", "B2", "02/01/24", "02/11/24"],   # 10 days (tie with Dune)
    ["S1", "B3", "03/01/24", "03/03/24"],   # 2 days
    ["S2", "B1", "01/05/24", ""],           # not returned
]


def test_clean_removes_spaces_and_quotes():
    assert lib.clean('  "Dune"\n') == "Dune"


def test_currently_borrowed():
    assert lib.currently_borrowed(BORROWED) == [["S2", "B1", "01/05/24", ""]]


def test_frequent_borrowers_adds_count():
    assert lib.frequent_borrowers(STUDENTS, BORROWED) == [["S1", "Anna", 3]]


def test_average_duration():
    _, average = lib.borrow_durations(BORROWED, BOOKS)
    assert round(average, 2) == 7.33   # (10 + 10 + 2) / 3


def test_summary_keeps_ties_and_skips_inactive_students():
    summary = lib.build_summary(STUDENTS, BORROWED, BOOKS)
    assert summary == [
        ["Anna", 3, 7.33, ["Dune", "1984"]],
        ["Bob", 1, "N/A", []],   # borrowed but nothing returned
    ]                            # Eva never borrowed -> not in the report
