# Personal Expense Tracker - Step 3
# Add expenses, view them, see weekly and monthly totals,
# and track a monthly budget.
# Amounts are in Bangladeshi Taka (Tk).

import csv
import json
import os
from datetime import datetime, date, timedelta

EXPENSES_FILE = "expenses.csv"
BUDGET_FILE = "budget.json"

CATEGORIES = ["Food", "Transport", "Shopping", "Bills"]

# Warn when this share of the budget is used
WARNING_SHARE = 0.8


def ask_amount(question):
    # Keep asking until the user types a number bigger than 0
    while True:
        text = input(question)
        try:
            amount = float(text)
        except ValueError:
            print("Please type a number, like 150 or 75.5")
            continue
        if amount <= 0:
            print("The amount must be more than 0.")
            continue
        return amount


def load_expenses():
    # Read expenses.csv and return a list of expenses.
    # Each expense is a small dictionary: date, category, amount, note.
    if not os.path.exists(EXPENSES_FILE):
        return []

    expenses = []
    with open(EXPENSES_FILE, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            expenses.append({
                "date": datetime.strptime(row["date"], "%Y-%m-%d").date(),
                "category": row["category"],
                "amount": float(row["amount"]),
                "note": row["note"],
            })
    return expenses


def load_budget():
    # Return the saved monthly budget, or None if there isn't one yet
    if not os.path.exists(BUDGET_FILE):
        return None
    with open(BUDGET_FILE) as f:
        return json.load(f)["monthly_budget"]


def save_budget(amount):
    with open(BUDGET_FILE, "w") as f:
        json.dump({"monthly_budget": amount}, f)


def set_budget():
    print("\n--- Set monthly budget ---")
    current = load_budget()
    if current is not None:
        print(f"Current budget: Tk {current:.2f}")

    amount = ask_amount("New monthly budget in Tk: ")
    save_budget(amount)
    print(f"Budget saved: Tk {amount:.2f} per month.")


def add_expense():
    print("\n--- Add expense ---")

    amount = ask_amount("Amount in Tk: ")

    # Choose a category
    print("Category:")
    for number, name in enumerate(CATEGORIES, start=1):
        print(f"{number}. {name}")

    while True:
        choice = input("Choose a category number: ")
        if choice.isdigit() and 1 <= int(choice) <= len(CATEGORIES):
            category = CATEGORIES[int(choice) - 1]
            break
        print("Please choose a number from the list.")

    note = input("Short note (press Enter to skip): ")

    # Save one row: date, category, amount, note
    file_exists = os.path.exists(EXPENSES_FILE)
    with open(EXPENSES_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["date", "category", "amount", "note"])
        today = datetime.now().strftime("%Y-%m-%d")
        writer.writerow([today, category, amount, note])

    print(f"Saved: Tk {amount:.2f} for {category}.")


def view_expenses():
    expenses = load_expenses()
    if not expenses:
        print("\nNo expenses yet.")
        return

    print("\n--- All expenses ---")
    for e in expenses:
        print(f"{e['date']}  {e['category']:<10} Tk {e['amount']:>8.2f}  {e['note']}")


def show_summary():
    expenses = load_expenses()
    if not expenses:
        print("\nNo expenses yet.")
        return

    today = date.today()

    # Last 7 days, counting today
    week_start = today - timedelta(days=6)
    week_total = 0
    for e in expenses:
        if week_start <= e["date"] <= today:
            week_total += e["amount"]

    # This calendar month
    month_total = 0
    by_category = {}
    for e in expenses:
        if e["date"].year == today.year and e["date"].month == today.month:
            month_total += e["amount"]
            name = e["category"]
            by_category[name] = by_category.get(name, 0) + e["amount"]

    print("\n--- Spending summary ---")
    print(f"Last 7 days:  Tk {week_total:.2f}")
    print(f"This month:   Tk {month_total:.2f}")

    if by_category:
        print("\nThis month by category:")
        for name, total in by_category.items():
            print(f"  {name:<10} Tk {total:.2f}")

    # Budget
    budget = load_budget()
    if budget is None:
        print("\nNo budget set yet. Use the menu to set one.")
        return

    remaining = budget - month_total
    print(f"\nMonthly budget: Tk {budget:.2f}")
    if remaining >= 0:
        print(f"Remaining:      Tk {remaining:.2f}")
    else:
        print(f"Over budget by: Tk {-remaining:.2f}")

    if remaining >= 0 and month_total >= budget * WARNING_SHARE:
        used = month_total / budget * 100
        print(f"Careful: you have used {used:.0f}% of this month's budget.")


def main():
    while True:
        print("\n=== Expense Tracker ===")
        print("1. Add an expense")
        print("2. View all expenses")
        print("3. Weekly and monthly summary")
        print("4. Set monthly budget")
        print("5. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            add_expense()
        elif choice == "2":
            view_expenses()
        elif choice == "3":
            show_summary()
        elif choice == "4":
            set_budget()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Please choose 1, 2, 3, 4 or 5.")


main()
