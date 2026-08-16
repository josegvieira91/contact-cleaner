import re
import sys
import csv
from rich.table import Table
from rich.console import Console
from rich.panel import Panel



def main():
    # 1. check command line argument
    if len(sys.argv) != 2:
        sys.exit("invalid number of arguments")

    seen = set()
    valid = []
    errors = []

    # 2. check if file exists and can be opened
    try:
        with open(sys.argv[1]) as file:
            # 3. check for expected header format
            reader = csv.DictReader(file)
            if reader.fieldnames != ["name", "email", "phone"]:
                sys.exit("invalid header: expected name,email,phone")

            # 4. loop to read and process data
            for row in reader:
                # 4a. try to normalize name, email and phone
                try:
                    name = normalize_name(row["name"])
                    email = normalize_email(row["email"])
                    phone = normalize_phone(row["phone"])
                except ValueError as e:
                    # 4b. if normalization fails -> add to errors list with reason
                    errors.append(
                        {
                            "name": row["name"],
                            "email": row["email"],
                            "phone": row["phone"],
                            "reason": str(e),
                        }
                    )
                    continue

                # 4c. if email already seen -> add to errors list as duplicate
                if email in seen:
                    errors.append(
                        {
                            "name": row["name"],
                            "email": row["email"],
                            "phone": row["phone"],
                            "reason": "duplicate",
                        }
                    )
                    continue

                # 4d. otherwise -> add email to seen, add contact to valid list
                seen.add(email)
                valid.append({"name": name, "email": email, "phone": phone})

    except FileNotFoundError:
        sys.exit("could not open file")

    # 5. write output files (clean and rejected)
    with open("clean.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "email", "phone"])
        writer.writeheader()
        writer.writerows(valid)

    with open("rejected.csv", "w", newline="") as f:
        writer = csv.DictWriter(f1, fieldnames=["name", "email", "phone", "reason"])
        writer.writeheader()
        writer.writerows(errors)

    # 6. summary on terminal
    clean = len(valid)
    duplicates = 0
    for row in errors:
        if row["reason"] == "duplicate":
            duplicates += 1
    rejected = len(errors) - duplicates
    read = clean + len(errors)

    console = Console()

    table = Table(
        show_header=True,
        header_style="bold cyan",
        show_lines=True,
    )

    table.add_column("Metric", style="bold white", justify="left")
    table.add_column("Count", justify="right")

    table.add_row("Total Read", f"[bold]{read}[/]")
    table.add_row("Clean", f"[green]{clean}[/]")
    table.add_row("Duplicates", f"[yellow]{duplicates}[/]")
    table.add_row("Rejected", f"[red]{rejected}[/]")

    summary_panel = Panel(
        table,
        title="[bold green]Processing Complete[/]",
        subtitle="[dim]Pipeline Summary[/]",
        border_style="bright_blue",
        expand=False,
    )

    console.print(summary_panel)


def normalize_name(name):
    clean_name = name.strip()
    if not clean_name:
        raise ValueError("empty name")
    return clean_name.title()


def normalize_email(email):
    clean_email = email.strip().lower()
    if not re.fullmatch(r"[\w.]+@\w+(\.\w+)+", clean_email):
        raise ValueError("invalid email")
    return clean_email


def normalize_phone(phone):
    phone_digits = re.sub(r"\D", "", phone)
    if len(phone_digits) == 10:
        return phone_digits
    if len(phone_digits) == 11 and phone_digits[0] == "1":
        return phone_digits[1:]
    raise ValueError("invalid phone")


if __name__ == "__main__":
    main()
