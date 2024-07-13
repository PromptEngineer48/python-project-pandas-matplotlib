import pandas as pd
import csv
from datetime import datetime

from data_entry import get_amount, get_category, get_date, get_description
import matplotlib.pyplot as plt


class CSV:
    CSV_FILE = "finance_data.csv"
    COLUMNS = ["date", "amount", "category", "description"]
    FORMAT = "%d-%m-%Y"

    @classmethod
    def initalize_csv(cls):
        try:
            pd.read_csv(cls.CSV_FILE)
        except FileNotFoundError:
            df = pd.DataFrame(columns=cls.COLUMNS)
            df.to_csv(cls.CSV_FILE, index=False)

    @classmethod
    def add_entry(cls, date, amount, category, description):
        new_entry = {
            "date": date,
            "amount": amount,
            "category": category,
            "description": description,
        }

        with open(cls.CSV_FILE, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=cls.COLUMNS)
            writer.writerow(new_entry)

        print("Entry Added Successfully")

    @classmethod
    def get_transactions(cls, start_date, end_date):
        df = pd.read_csv(cls.CSV_FILE)
        df["date"] = pd.to_datetime(df["date"], format=CSV.FORMAT)
        start_date = datetime.strptime(start_date, CSV.FORMAT)
        end_date = datetime.strptime(end_date, CSV.FORMAT)

        mask = (df["date"] >= start_date) & (df["date"] <= end_date)
        filtered_df = df.loc[mask]

        if filtered_df.empty:
            print("No transactions found in the specified date range.")
        else:
            print(
                f"Transactions from {start_date.strftime(CSV.FORMAT)} TO {end_date.strftime(CSV.FORMAT)}"
            )
            print(
                filtered_df.to_string(
                    index=False, formatters={"data": lambda x: x.strftime(CSV.FORMAT)}
                )
            )

            total_income = filtered_df[filtered_df["category"] == "Income"][
                "amount"
            ].sum()
            total_expense = filtered_df[filtered_df["category"] == "Expense"][
                "amount"
            ].sum()

            print("\nSummary:")
            print(f"Total Income: ${total_income:.2f}")
            print(f"Total Expense: ${total_expense:.2f}")
            print(f"Net Savings: ${(total_income - total_expense):.2f}")

        return filtered_df


def add():
    CSV.initalize_csv()
    date = get_date(
        "Enter the date of the transaction (dd-mm-yyyy) or Enter for today's date: ",
        allow_default=True,
    )
    amount = get_amount()
    category = get_category()
    description = get_description()
    CSV.add_entry(date, amount, category, description)


def plot_transactions1(df):
    # Convert date to datetime if it's not already
    df["date"] = pd.to_datetime(df["date"])
    df.set_index("date", inplace=True)

    # Separate income and expenses
    income_df = df[df["category"] == "Income"]["amount"]
    expense_df = df[df["category"] == "Expense"]["amount"]

    # Resample to weekly frequency and calculate cumulative sum
    income_cumsum = income_df.resample("W").sum().cumsum()
    expense_cumsum = expense_df.resample("W").sum().cumsum()

    # Create a date range from the earliest to the latest date
    date_range = pd.date_range(start=df.index.min(), end=df.index.max(), freq="W")

    # Reindex the cumulative sums to fill in any missing weeks
    income_cumsum = income_cumsum.reindex(date_range, method="ffill")
    expense_cumsum = expense_cumsum.reindex(date_range, method="ffill")

    # Calculate net savings
    net_savings = income_cumsum - expense_cumsum

    # Plotting
    plt.figure(figsize=(12, 6))
    plt.fill_between(
        income_cumsum.index,
        income_cumsum,
        label="Cumulative Income",
        alpha=0.3,
        color="g",
    )
    plt.fill_between(
        expense_cumsum.index,
        expense_cumsum,
        label="Cumulative Expenses",
        alpha=0.3,
        color="r",
    )
    plt.plot(net_savings.index, net_savings, label="Net Savings", color="b")

    plt.xlabel("Date")
    plt.ylabel("Amount ($)")
    plt.title("Cumulative Income vs. Expenses Over Time")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def plot_transactions(df):
    df.set_index("date", inplace=True)

    income_df = (
        df[df["category"] == "Income"]
        .resample("D")
        .sum()
        .reindex(df.index, fill_value=0)
    )

    expense_df = (
        df[df["category"] == "Expense"]
        .resample("D")
        .sum()
        .reindex(df.index, fill_value=0)
    )

    plt.figure(figsize=(10, 5))
    plt.plot(income_df.index, income_df["amount"], label="Income", color="g")
    plt.plot(expense_df.index, expense_df["amount"], label="Expense", color="r")
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.title("Income vs. Expense Over Time")
    plt.legend()
    plt.grid(True)
    plt.show()


def main():
    while True:
        print("\n1. Add a new transaction")
        print("2. View transactions and summary within a date range")
        print("3. Exit")
        choice = input("Enter your choice (1-3): ")

        if choice == "1":
            add()

        elif choice == "2":
            start_date = input("Enter the start date (dd-mm-yyyy): ")
            end_date = input("Enter the end date (dd-mm-yyyy): ")
            df = CSV.get_transactions(start_date, end_date)
            if input("Do you want to see a plot? (y/n): ").lower() == "y":
                plot_transactions1(df)

        elif choice == "3":
            print("Exiting the program. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 3.")


if __name__ == "__main__":
    main()
