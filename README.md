# Contact Cleaner

#### Video demo: https://youtu.be/nCwGATlj2YQ

#### Description

Contact Cleaner is a command-line tool that helps small businesses organize
messy customer data, fast and with precision. You feed it a contact list
exported from wherever (a spreadsheet, a form, an old CRM) and it gives you
back two files: one with every contact validated, normalized and deduplicated,
ready to import anywhere, and one with every rejected row and the exact reason
it was rejected. Nothing gets silently dropped.

I run a small business myself, and dirty contact lists are one of those
problems almost every small business has and nobody wants to fix by hand: phones in three formats, emails with stray spaces, names in ALL CAPS,
the same person entered twice. I wanted my final project to be something
genuinely useful for that day to day, not a demo. This is a tool I would
actually run for a client.

#### How it works

```
python project.py sample.csv
```

The input must be a CSV with the header `name,email,phone`. The program:

1. Validates the command-line argument, that the file opens, and that the
   header is exactly the expected one. Anything wrong stops with a clear
   message.
2. Reads the file row by row. Each field goes through its own normalizer:
   names are stripped and title-cased, emails are lowercased and validated
   against a pragmatic regex, phones are reduced to digits and must be 10
   digits (or 11 starting with 1, in which case the country code is removed).
3. A row that fails validation goes to the rejected list with the reason of
   the first failure found. A row whose normalized email already appeared
   goes to the rejected list as a duplicate. Everything else is kept.
4. Writes `clean.csv` (normalized contacts) and `rejected.csv` (original
   values plus a `reason` column), then prints a summary table with four
   counts: read, clean, duplicates, rejected.

#### Files

- `project.py`: the whole program. `main()` plus the three normalizers
  (`normalize_name`, `normalize_email`, `normalize_phone`).
- `test_project.py`: pytest suite for the three normalizers, including the
  adversarial cases that bit me during development.
- `sample.csv`: a 20-row messy input covering every rejection type, so anyone
  cloning the repo can run the tool immediately.
- `requirements.txt`: `rich` (summary table) and `pytest`.
- `design_decisions.md`: a log I kept while designing, with every choice, the
  alternatives and why. Most of the section below comes from there.

#### Design decisions

**Two output files instead of silently dropping bad rows.** In a real client
scenario, "40 contacts disappeared" is a support call. Every rejected row
keeps its original values and gains a reason, so the file can be fixed and
re-run.

**Input as a command-line argument.** I wanted real functionality and simple
use. A hardcoded filename would force the user to rename their file, and an
interactive prompt is bad for automation and hard to test. `python project.py
yourfile.csv` is how real CLI tools work.

**Normalizers raise ValueError, never print, never return None.** The
validator's only job is to validate. The decision of what to do with a bad
row belongs to `main()`, which catches the exception and routes the row to
the rejected list. The exception message itself ("empty name", "invalid
email", "invalid phone") becomes the reason column.

**Duplicate means same normalized email, first one wins.** Deduplicating
after normalization is what catches " JOHN@GMAIL.COM " and
"john@gmail.com" as the same person. Emails already accepted live in a set,
so the membership check stays instant no matter the file size.

**No counters.** The loop accumulates into three structures (a set of seen
emails, a valid list, an errors list) and the four summary numbers are
derived from them afterwards. A counter updated alongside a list is the same
information stored twice, and two sources of truth eventually disagree.

**A pragmatic email regex, not the full RFC.** `[\w.]+@\w+(\.\w+)+` checked
with `re.fullmatch`. fullmatch anchors the whole string by definition, which
kills a bug I kept hitting in exercises: an unanchored validator silently
accepts trailing garbage.

**rich is presentation only.** The four numbers are computed by plain logic
before the table exists. Swapping rich for print would change zero logic.

#### A bug worth telling

Near the end, with everything working and tested, I renamed a variable for
consistency: the second file handle was `f1` and I wanted plain `f`. I
changed the `with` line, committed, pushed, and moved on. What I did not do
was run the program again, because "a rename changes nothing". Except I had
only renamed half of it: the `DictWriter` call still said `f1`. The committed,
public version of the program crashed with a NameError on the line that
writes the rejected file.

The lesson stuck: edited code expires previous test results, with no
exception for cosmetic changes. Run it again. Always.

#### Running it

```
pip install -r requirements.txt
python project.py sample.csv
pytest test_project.py
```

#### Ideas for a v2

- Tolerant header mode: accept and preserve extra columns, validating only
  the three core ones. Client spreadsheets always have extra columns.
- International phone formats beyond US.
- Fuzzy duplicate detection (name similarity plus same phone), which I left
  out on purpose: it is a project of its own.
