"""
Designer Portfolio Manager
---------------------------
A console-based tool for designers to add and view design projects,
including descriptions, image references, and client feedback.

Data is stored in a JSON file (portfolio_data.json) in the same folder,
so your projects persist between runs.
"""

import json
import os
import sys
from datetime import datetime

DATA_FILE = "portfolio_data.json"


# ----------------------------- Data Layer -----------------------------

def load_portfolio():
    """Load projects from the JSON data file. Return an empty list if none exists."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        print("⚠️  Could not read existing data file. Starting with an empty portfolio.")
        return []


def save_portfolio(projects):
    """Save the list of projects back to the JSON data file."""
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, indent=2)


# --------------------------- Input Handling ----------------------------

def prompt_nonempty(label):
    """Keep asking until the user provides a non-empty response."""
    while True:
        value = input(label).strip()
        if value:
            return value
        print("  This field can't be empty. Please try again.")


def prompt_optional(label):
    """Ask for input that's allowed to be blank."""
    return input(label).strip()


def prompt_image_reference():
    """
    Ask for an image reference. Supports either a file path or, if the
    user has no image, an option to paste/generate simple ASCII art.
    """
    print("\n  Image options:")
    print("    1. Provide a file path to an image")
    print("    2. Enter ASCII art representation instead")
    print("    3. Skip image for now")
    choice = input("  Choose an option (1-3): ").strip()

    if choice == "1":
        path = prompt_nonempty("  Enter image file path: ")
        if not os.path.exists(path):
            print(f"  Note: '{path}' was not found on disk, but it has been saved as a reference.")
        return {"type": "path", "value": path}

    elif choice == "2":
        print("  Enter your ASCII art. Type 'END' on a new line when finished:")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        art = "\n".join(lines) if lines else "(no art provided)"
        return {"type": "ascii", "value": art}

    else:
        return {"type": "none", "value": ""}


def add_project(projects):
    """Collect details for a new project and append it to the portfolio."""
    print("\n--- Add New Project ---")
    name = prompt_nonempty("Project name: ")
    description = prompt_nonempty("Project description: ")
    category = prompt_optional("Category/Type (e.g. Branding, UI/UX) [optional]: ")
    image = prompt_image_reference()
    feedback = prompt_optional("Client feedback (leave blank if none yet): ")

    project = {
        "name": name,
        "description": description,
        "category": category or "Uncategorized",
        "image": image,
        "feedback": feedback or "No feedback yet.",
        "date_added": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }

    projects.append(project)
    save_portfolio(projects)
    print(f"\n✅ Project '{name}' added to your portfolio!\n")


# ------------------------------ Display --------------------------------

def display_project(project, index=None):
    """Print a single project's details in a readable card-like format."""
    header = f"[{index}] {project['name']}" if index is not None else project["name"]
    print("=" * 60)
    print(header)
    print("-" * 60)
    print(f"Category : {project['category']}")
    print(f"Added    : {project.get('date_added', 'Unknown')}")
    print(f"\nDescription:\n  {project['description']}")

    image = project.get("image", {"type": "none", "value": ""})
    print("\nImage:")
    if image["type"] == "path":
        print(f"  📁 File path: {image['value']}")
    elif image["type"] == "ascii":
        print("  🎨 ASCII art:")
        for line in image["value"].splitlines():
            print(f"     {line}")
    else:
        print("  (no image provided)")

    print(f"\nClient Feedback:\n  💬 {project['feedback']}")
    print("=" * 60 + "\n")


def view_portfolio(projects):
    """Display every project in the portfolio."""
    if not projects:
        print("\nYour portfolio is empty. Add a project first!\n")
        return

    print(f"\n--- Portfolio ({len(projects)} project(s)) ---\n")
    for i, project in enumerate(projects, start=1):
        display_project(project, index=i)


def view_single_project(projects):
    """Let the user pick one project by number to view in detail."""
    if not projects:
        print("\nYour portfolio is empty. Add a project first!\n")
        return

    list_project_names(projects)
    choice = input("\nEnter project number to view (or press Enter to cancel): ").strip()
    if not choice:
        return
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(projects):
            print()
            display_project(projects[idx], index=idx + 1)
        else:
            print("Invalid project number.\n")
    except ValueError:
        print("Please enter a valid number.\n")


def list_project_names(projects):
    """Quick numbered list of project names (used as a menu helper)."""
    print("\nProjects:")
    for i, project in enumerate(projects, start=1):
        print(f"  {i}. {project['name']}  ({project['category']})")


def delete_project(projects):
    """Remove a project from the portfolio by number."""
    if not projects:
        print("\nYour portfolio is empty. Nothing to delete.\n")
        return

    list_project_names(projects)
    choice = input("\nEnter project number to delete (or press Enter to cancel): ").strip()
    if not choice:
        return
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(projects):
            removed = projects.pop(idx)
            save_portfolio(projects)
            print(f"\n🗑️  Deleted '{removed['name']}'.\n")
        else:
            print("Invalid project number.\n")
    except ValueError:
        print("Please enter a valid number.\n")


# -------------------------------- Menu ----------------------------------

def print_menu():
    print("\n" + "#" * 60)
    print("   DESIGNER PORTFOLIO MANAGER")
    print("#" * 60)
    print("1. Add new project")
    print("2. View full portfolio")
    print("3. View a single project")
    print("4. Delete a project")
    print("5. Exit")


def main():
    projects = load_portfolio()
    print("Welcome to your Portfolio Manager!")

    while True:
        print_menu()
        choice = input("Choose an option (1-5): ").strip()

        if choice == "1":
            add_project(projects)
        elif choice == "2":
            view_portfolio(projects)
        elif choice == "3":
            view_single_project(projects)
        elif choice == "4":
            delete_project(projects)
        elif choice == "5":
            print("\nGoodbye! Your portfolio has been saved.\n")
            sys.exit(0)
        else:
            print("\nInvalid choice. Please enter a number from 1 to 5.\n")


if __name__ == "__main__":
    main()