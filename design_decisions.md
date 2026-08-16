# Design Decisions — Contact Cleaner

Notes on the choices I made while designing this project, before and during
implementation. What I picked, what I didn't, and why. Most of the README's
"design choices" section comes from here.

## 1. Why a contact list cleaner

Other ideas I considered: a revenue report generator, an invoice filename
normalizer, a schedule-vs-confirmation reconciler, a sensitive-data scanner.

I picked this one because it solves a problem I actually see in small
businesses: every company has a messy contact spreadsheet. Phones in three
formats, emails with stray spaces, names in ALL CAPS, duplicates nobody
cleaned up. Cleaning that data is also the first step of any real pipeline
(CRM import, email campaign, feeding data to an AI system), so the project
maps to real work, not a toy.

It also breaks down naturally into small pure functions (normalize name,
email, phone), and those are easy to test with pytest. That mattered because
the course requires at least three tested functions.

## 2. Two output files plus a terminal summary

The program writes clean.csv (valid, normalized contacts) and rejected.csv
(the original values plus a "reason" column), then prints a summary with four
counts: read, clean, rejected, duplicates.

The simpler version would be one clean file, with bad rows silently dropped.
I rejected that: dropping data silently means the user has no idea 40
contacts disappeared. Keeping every rejected row with its reason means
nothing is lost and the file can be fixed and re-run. The summary costs
almost nothing and gives instant feedback.

## 3. Input via command-line argument

Usage is `python project.py input.csv`, using sys.argv.

A hardcoded filename would be useless in practice, since the user would have
to rename their file to match. An interactive input() prompt is bad for
automation (typing a path on every run) and awkward to test. A CLI argument
is how real command-line tools work, and it makes the error cases (missing
argument, file not found) explicit.

## 4. Strict header

The input must have exactly the header `name,email,phone`. Anything else
stops the program with a clear error.

I considered a tolerant mode that accepts extra columns and preserves them in
the output. That is more realistic, client spreadsheets always have extra
columns, but the preservation logic adds complexity I didn't want in a first
project. It would be a natural v2 feature.

## 5. Conservative normalization rules

- Name: strip whitespace, Title Case. Empty after strip: rejected.
- Email: strip, lowercase, validate with an anchored regex. Invalid: rejected.
- Phone (US format): remove every non-digit. Accept 10 digits, or 11 starting
  with 1 (country code, removed during normalization). Anything else: rejected.

The ambitious version would handle international codes, fix domain typos like
gmial.com, and get compound names right ("da Silva"). Each of those is a pit
of edge cases. Typo correction alone could eat the whole project. Three clear
rules keep the scope at "the basics, done well", and each rule becomes one
function with four or five focused tests.

The whole project is in English (code, comments, output, README) and the
phone convention is US NANP, since this is a public portfolio repo with an
international audience. The 11-digits-with-leading-1 rule is also a more
interesting transformation to test than a plain length check.

## 6. Duplicate means same normalized email, first one wins

Email is the natural unique ID for a contact. Deduplicating after
normalization means " JOAO@X.COM " and "joao@x.com" are correctly caught as
the same. The rule is objective and easy to test.

I skipped fuzzy matching (name similarity plus same phone). Smarter, but
fuzzy matching is a whole project by itself. One known consequence of my
rule: the same person with a personal and a work email passes through twice.
That's correct behavior for this tool, not a bug.

## 7. First failure wins

A row that breaks several rules gets rejected with the first failure found,
checking name, then email, then phone. Reasons: "empty name", "invalid
email", "invalid phone", "duplicate". Duplicates get their own count in the
summary but still go to rejected.csv.

One reason per row keeps the output file and the code simple, and the fixed
order makes the behavior deterministic, which matters for testing.

## 8. Normalizers raise ValueError, never print, never return None

Each normalize_* function returns the cleaned value or raises ValueError.

Printing inside a validator hides the failure from the program. Returning
None forces None-checks everywhere and invites AttributeError later. Raising
puts the decision where it belongs: main() catches the exception and routes
the row to the rejected list. The validator's only job is to validate.

## 9. Line-by-line processing

Rows are validated as they're read, not loaded into memory first.

My first instinct was that deduplication would require having all rows to
compare against each other. It doesn't: to know if row 50 is a duplicate, I
only need the emails already accepted so far, which is an accumulator that
grows during the loop. With 200 contacts either approach works. With 2
million rows, streaming is the difference between working and crashing. It's
also the same pattern used for API pagination and large-file processing,
which I'll need later anyway.

## 10. A set for "have I seen this email?"

`seen = set()` holds the emails already accepted. Membership testing with
`in` is effectively instant on a set regardless of size; on a list it scans
element by element. A set is the standard structure for this exact question.

## 11. No counters, everything derived

The loop accumulates into exactly three structures: seen (set), valid (list),
errors (list). The four summary numbers come afterwards:

- clean = len(valid)
- duplicates = count of errors whose reason == "duplicate"
- rejected = len(errors) - duplicates
- read = len(valid) + len(errors)

I almost created a counters dict updated inside the loop. Rejected it because
counters kept alongside the lists are the same information stored twice. If
some future edit updates a list and forgets the counter, the summary lies.
A value derived at the moment of use can't desynchronize.

## 12. Rejected rows are dicts, not positional lists

Each rejected row is stored as
`{"name": ..., "email": ..., "phone": ..., "reason": ...}`.

With a positional list, the reason lives at e[3], a magic number I'd have to
decode months from now. With a dict, e["reason"] reads itself, and counting
duplicates compares the exact field instead of checking whether "duplicate"
appears somewhere in the row (fragile). Bonus: csv.DictWriter writes lists of
dicts almost for free.

Worth noting the contrast with decision 11: a dict as a record (named fields
of one thing) is good design. A dict as a parallel counter of something the
lists already know is redundancy. Same structure, different purpose.

## 13. rich is presentation only

The summary table uses the rich library (listed in requirements.txt), but the
four numbers are computed by plain logic before the table exists. rich only
draws. Swapping it for print would change zero logic, and that's the point:
the logic stays testable without a terminal-rendering dependency.

Build order: plain print first, working end to end with tests green, rich as
final polish. Ugly but working comes first.

## 14. Repo choices

- Own public repo (contact-cleaner), separate from my private exercises repo.
  A portfolio project needs its own visible home.
- Public since the first commit. The history includes an early fix removing
  IDE files from tracking. I left it visible on purpose: an honest history
  says more than a repo that appears fully formed in one commit.
- .gitignore excludes .idea/ (IDE config), .venv/, __pycache__/, and the
  output CSVs, since generated files don't belong in version control.
- sample.csv, a small messy input covering every rejection type, IS
  committed, so anyone cloning the repo can run the tool immediately.

## 15. Email regex: pragmatic, not RFC-complete

The pattern is `[\w.]+@\w+(\.\w+)+`, checked with re.fullmatch.

I'm not trying to cover the full email RFC. That regex is famously enormous
and nobody uses it in practice. What I want is the essential structure:
user part (letters, digits, underscore, dots), @, then domain blocks
separated by dots, at least two of them.

Two choices worth recording:

- fullmatch instead of search with ^ and $ anchors. Forgetting an anchor is
  a bug I've hit before: an unanchored validator silently accepts trailing
  garbage ("jose@gmail.com xyz" would pass). fullmatch anchors by
  definition, so the whole class of bug stops being possible.
- `(\.\w+)+` with plus, not optional. My first sketch modeled .com.br as a
  special case (2-3 letters, then optionally dot plus 2 more). That rejects
  .info, .travel and subdomains. The general rule "one or more dot-blocks"
  covers all of them with no special cases, and the mandatory first block
  is what rejects TLD-less garbage like jose@gmail.

Known cost, accepted: a@b.c passes (single-letter TLDs don't exist in
practice). Not worth another rule.

Decisions 1 through 15 cover the design phase, written down before the first
function. New entries get added as implementation decisions come up.
