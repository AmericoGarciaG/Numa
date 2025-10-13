
---
### **`AGENTS.md`**

---

#### **## Core Governance & Methodology**

-   **Primary Directive:** Before writing any code, you MUST read and adhere to the principles outlined in the **`GOVERNANCE.md`** file.
-   **Source of Truth for Business Logic:** All business logic is defined in `/Context/LOGIC.md`. The `GOVERNANCE.md` file explains how you must use it.

---

#### **## Setup commands**

-   **Install deps:** `py -m pip install -r requirements.txt` (ALWAYS in .venv virtual environment)
-   **Start dev server:** `py -m uvicorn app.main:app --reload` (ALWAYS in separate terminal)
-   **Run tests:** `py -m pytest`

---

#### **## Code style**

-   **Formatting:** All code MUST be formatted with `black`.
-   **Import Sorting:** All imports MUST be sorted with `isort`.
-   **Typing:** Use Python type hints strictly.
-   **Quotes:** Use double quotes for strings, unless single quotes are required for clarity.
-   **Docstrings:** Use Google-style docstrings for all public modules and functions.

---

#### **## Environment Management**

-   **Virtual Environment Rule:** ALL package installations MUST be done within the `.venv` virtual environment. NEVER install packages globally.
-   **Package Installation:** Always use `py -m pip install <package>` or `py -m pip install -r requirements.txt` to ensure installation in the virtual environment.
-   **Server Execution Rule:** When starting development servers (uvicorn, etc.), ALWAYS run them in SEPARATE terminals to avoid blocking the current working terminal.
-   **Multiple Servers:** If multiple services need to run simultaneously, each MUST run in its own dedicated terminal window.

---

#### **## Development Environment Tips**

-   **Add a new dependency:** Add the library to `requirements.txt` and then run `py -m pip install -r requirements.txt`.
-   **Database Models:** All database models are defined in `models.py` using SQLAlchemy.
-   **API Schemas:** All Pydantic schemas for API validation are in `schemas.py`.
-   **Business Logic:** Core application logic resides in `services.py`. API endpoints in `main.py` should be lean and delegate to the service layer.

---

#### **## Testing instructions**

-   **Run all tests:** From the root, run `py -m pytest`. The commit should pass all tests before you merge.
-   **Focus on one test:** To run a specific test file, use `py -m pytest path/to/your/test_file.py`.
-   **Linting:** Before committing, always run `py -m black .` and `py -m isort .` to ensure code style rules pass.
-   **New Code:** Any new function or business logic added MUST be accompanied by corresponding unit tests.

---

#### **## PR instructions**

-   **Title format:** `[Module] <Concise Description of Change>` (e.g., `[API] Add user authentication endpoint`)
-   **Pre-commit checks:** Always run `py -m black .`, `py -m isort .`, and `py -m pytest` before requesting a review.

---