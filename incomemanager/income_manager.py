import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox

from .data_manager import add_income_entry, summarize_totals

try:
    import openai
except ImportError:
    openai = None


class IncomeManager(tk.Tk):
    """Simple GUI for managing income stream ideas."""

    INCOME_CATEGORIES = [
        "E-commerce",
        "Affiliate Marketing",
        "Online Courses",
        "Freelancing",
        "Content Creation",
        "Digital Products",
        "Consulting",
    ]

    def __init__(self):
        super().__init__()
        self.title("Income Stream Manager")
        self.geometry("750x450")
        self.create_widgets()

    def add_category(self):
        name = self.new_cat.get().strip()
        if name and name not in self.listbox.get(0, tk.END):
            self.listbox.insert(tk.END, name)
        self.new_cat.delete(0, tk.END)

    def record_income(self):
        category = self.listbox.get(tk.ACTIVE)
        if not category:
            return

        top = tk.Toplevel(self)
        top.title(f"Record Income - {category}")
        ttk.Label(top, text="Amount:").pack(padx=5, pady=5)
        amount_var = tk.StringVar()
        ttk.Entry(top, textvariable=amount_var).pack(padx=5, pady=5)
        ttk.Label(top, text="Description:").pack(padx=5, pady=5)
        desc_var = tk.StringVar()
        ttk.Entry(top, textvariable=desc_var).pack(padx=5, pady=5)

        def save():
            try:
                amt = float(amount_var.get())
            except ValueError:
                messagebox.showerror("Invalid", "Enter a numeric amount")
                return
            add_income_entry(category, amt, desc_var.get())
            top.destroy()
            messagebox.showinfo("Saved", "Income recorded")

        ttk.Button(top, text="Save", command=save).pack(pady=5)

    def show_summary(self):
        summary = summarize_totals()
        if not summary:
            messagebox.showinfo("Summary", "No income recorded yet.")
            return
        lines = [f"{cat}: ${total:.2f}" for cat, total in summary.items()]
        lines.append("")
        lines.append(f"Total: ${sum(summary.values()):.2f}")
        messagebox.showinfo("Summary", "\n".join(lines))

    def create_widgets(self):
        left_frame = ttk.Frame(self)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=5, pady=5)

        self.listbox = tk.Listbox(left_frame, height=10)
        for cat in self.INCOME_CATEGORIES:
            self.listbox.insert(tk.END, cat)
        self.listbox.pack(fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(left_frame)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Get Suggestions", command=self.fetch_suggestions).pack(fill=tk.X)
        ttk.Button(button_frame, text="Record Income", command=self.record_income).pack(fill=tk.X)
        ttk.Button(button_frame, text="View Summary", command=self.show_summary).pack(fill=tk.X)
        ttk.Button(button_frame, text="Save Notes", command=self.save_notes).pack(fill=tk.X)

        add_frame = ttk.Frame(left_frame)
        add_frame.pack(fill=tk.X, pady=5)
        self.new_cat = ttk.Entry(add_frame)
        self.new_cat.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(add_frame, text="Add Category", command=self.add_category).pack(side=tk.RIGHT)

        right_frame = ttk.Frame(self)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.notes = scrolledtext.ScrolledText(right_frame, wrap=tk.WORD)
        self.notes.pack(fill=tk.BOTH, expand=True)

    def fetch_suggestions(self):
        if openai is None:
            messagebox.showinfo("Dependency missing", "openai package not installed.")
            return
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            messagebox.showinfo("Missing key", "Set OPENAI_API_KEY environment variable.")
            return
        openai.api_key = api_key
        category = self.listbox.get(tk.ACTIVE)
        prompt = f"Give me tips for earning money through {category}."
        try:
            resp = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
            )
            suggestion = resp.choices[0].message.content.strip()
            self.notes.insert(tk.END, f"\nSuggestions for {category}:\n{suggestion}\n")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def save_notes(self):
        try:
            with open("notes.txt", "w", encoding="utf-8") as fh:
                fh.write(self.notes.get("1.0", tk.END))
            messagebox.showinfo("Saved", "Notes saved to notes.txt")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))


if __name__ == "__main__":
    app = IncomeManager()
    app.mainloop()
