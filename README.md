# RetailPulse

Retail Sales Intelligence Dashboard

RetailPulse is a Python portfolio project for learning data cleaning, exploratory
data analysis (EDA), business metrics, visualization, and dashboard development.
The Streamlit dashboard uses the official UCI Online Retail workbook, with six
working pages, shared date/country/product filters, positive-sales KPIs, Plotly
charts, recorded-credit analysis, and a searchable transaction explorer with CSV
downloads. The source workbook and your learning notebooks are preserved.

## Quick start

Clone the repository and create an environment with Python 3.11:

```powershell
git clone https://github.com/eilrahcdev/RetailPulse.git
cd RetailPulse
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Download the [UCI Online Retail workbook](#dataset) into
`data/raw/Online Retail.xlsx`, or upload it through **Dataset & methodology**
in the sidebar. The workbook is excluded from Git.

Use the sidebar to change pages. The default period is the latest fully covered
calendar month, November 2011 for this workbook. The dataset is historical.

## Tools and prerequisites

- Windows and Visual Studio Code
- Python 3.12 or 3.13 preferred; this initial environment uses the existing Python
  3.11.5 installation. No new system Python was installed.
- Git, already available locally
- VS Code extensions: Python (`ms-python.python`) and Jupyter
  (`ms-toolsai.jupyter`)

The ten requested Python tools are pandas and NumPy for tables and numerical
work; Matplotlib, seaborn, and Plotly for charts; Streamlit for the app; openpyxl
for Excel files; JupyterLab and ipykernel for notebooks; and pytest for tests.
Their supporting dependencies are included in the pinned requirements.

If Python is missing, or you want the preferred version:

1. Open <https://www.python.org/downloads/windows/> and choose a Python 3.13
   **Windows installer (64-bit)** for a standard x64 Windows computer.
2. Run the installer yourself. Enable **Add python.exe to PATH**, retain pip and
   the Python launcher, and use the per-user installation option when available.
   Administrator approval depends on your computer's policy.
3. Reopen your VS Code terminal and check `py -3.13 --version` and
   `py -3.13 -m pip --version`.

To install either VS Code extension if needed, use the Extensions panel
(`Ctrl+Shift+X`), or run:

```powershell
code --install-extension ms-python.python
code --install-extension ms-toolsai.jupyter
```

If Git is missing on another machine, install it from
<https://git-scm.com/download/win>, reopen the terminal, and run `git --version`.

## Environment setup

Open this folder in VS Code. All commands below assume a terminal at the project
root, where `app.py` lives. The current `.venv` has already been created.

For a **fresh checkout** with Python 3.13 installed:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```

If you are reproducing the initial Python 3.11 environment instead, replace
`py -3.13` with `py -3.11`. The dependency snapshot is verified on Windows x64
with Python 3.11.5; rerun verification after changing Python versions. A virtual
environment uses the Python version that created it. Installing Python 3.13 does
not upgrade an existing `.venv`; keep your working environment until you are
ready to recreate it and select the new interpreter.

`requirements.txt` records exact versions of installed third-party dependencies.
The `-e .` entry installs this project's `src` package in editable mode. That
means changes to your own Python files are picked up immediately, and imports
work from notebooks without inserting machine-specific folders into `sys.path`.
`pyproject.toml` supplies the small amount of package metadata needed for this.
Setuptools is the standard packaging tool used to install that local package.

### Activate the virtual environment

```powershell
.\.venv\Scripts\Activate.ps1
python --version
python -c "import sys; print(sys.executable); print(sys.prefix != sys.base_prefix)"
```

The executable should end in `.venv\Scripts\python.exe`, and the last line should
be `True`. Activation changes which Python this terminal uses; it does not
install Python or dependencies.

PowerShell on this computer currently has a **Restricted** execution policy.
Activation may therefore be blocked. You can use the explicit interpreter in
every command without changing any policy:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m streamlit run app.py
```

If your computer's policy permits it, this optional command allows local scripts
only for the current PowerShell session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

There is no need to change the machine-wide policy. Organizational policies may
still prevent activation. Use the explicit interpreter in that case. In Command
Prompt, the equivalent activation command is `.venv\Scripts\activate.bat`.
Run `deactivate` when finished with an activated terminal.

### Select the interpreter and notebook kernel in VS Code

1. Reload VS Code if the newly installed Jupyter extension is not yet visible.
2. Press `Ctrl+Shift+P`, run **Python: Select Interpreter**, and select
   `.venv\Scripts\python.exe`. Workspace settings supply it as the default;
   an interpreter previously selected in VS Code may need to be changed manually.
3. Open either notebook, click **Select Kernel** in its top-right corner, then
   choose **Python Environments** and the same `.venv` interpreter.
4. Run the starter cell. It prints the interpreter and the imported module path.
   The interpreter should be inside this project's `.venv`.

The notebook kernel is chosen separately from the Python editor's interpreter.
Selecting `.venv` explicitly prevents notebooks from accidentally using a global
environment. No user-wide kernel registration is needed.

## Run the application

The interface uses a compact Swiss-inspired reporting system with one blue
accent, a revenue-focused metric strip, a full-width sales trend, and native
table alternatives for charts. Design rules are in
[the interface master](design-system/retailpulse/MASTER.md), and rendered browser
checks and limitations are in [the UI review](docs/ui-review.md).

With the environment activated:

```powershell
python -m streamlit run app.py
```

Without activation:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Open the local address printed in the terminal, usually
<http://localhost:8501>. Stop the app with `Ctrl+C`.

The first run reads the Excel file and checks its rows. A visible loading message
appears while this happens. Subsequent interactions reuse cached data. Replacing
the local workbook invalidates the cache through its modification timestamp.

### Dashboard pages and controls

| Page | What it does |
| --- | --- |
| Overview | Four KPIs, daily/weekly/monthly revenue with an aligned comparison, top products, countries, and computed period insights |
| Sales Analysis | Revenue trends, monthly revenue/orders/AOV, recorded credits, and observed sales less credits |
| Product Performance | Top ten products by revenue or units, detailed product totals, and CSV export |
| Geographic Analysis | Ranked country revenue, order/unit/share details, and CSV export |
| Data Explorer | Actual transaction rows, literal text search, transaction type filters, pagination, and full filtered CSV export |
| Data Quality Center | Full-source or filtered quality checks, business impact, metric reconciliation, and original-row evidence export |

Date, country, and product choices apply to every page. Empty country/product
selections mean all; **Reset filters** restores those choices and the default
dates. It leaves the explicitly chosen duplicate policy unchanged. Selecting a
new workbook resets the filters to that workbook's coverage. The Data Quality
Center defaults to an explicit entire-workbook audit, including undated rows,
before duplicate exclusions; choose Current filters to audit a dated selection.

Select one current-period revenue point, product bar, or country bar and use
**Inspect selected records** to open its positive-sales lines. The chart data
disclosures offer a keyboard-accessible **Record drilldown** selector. Back
restores the source page and analytical context. Sales Analysis separates usable
credits from review lines and adds country, item, and monthly credit breakdowns.

The [prioritized implementation checklist](docs/implementation-checklist.md)
records the audit and future phases. [Phase 1 analytical definitions](docs/phase1-analytics.md)
explain the formulas, data requirements, assumptions, and limitations; see
[Phase 1 verification](docs/phase1-verification.md) for the latest evidence.

Use **Dataset & methodology** in the sidebar to upload a workbook or toggle
**Exclude exact duplicate rows**. Uploads remain in memory and do not replace the
local file. They must contain all eight UCI columns and fit the 40 MB upload
limit. If no local workbook exists, the app provides download/upload guidance.
An invalid upload shows an error; removing it returns to the local workbook.

The explorer shows 25, 50, or 100 records at a time. Its CSV includes every row
matching the global filters, search, and transaction type selection, not just
the current page. Formula-like text cells are prefixed with an apostrophe for
spreadsheet exports; numeric quantities and credits keep their signs.

## Start JupyterLab

From the project root:

```powershell
.\.venv\Scripts\python.exe -m jupyterlab
```

Open a notebook under `notebooks/` and use its Python kernel. Starting JupyterLab
with the virtual environment's Python makes that environment available. VS Code
can also run these notebooks directly, without starting a separate JupyterLab
server. Stop a terminal-launched JupyterLab server with `Ctrl+C` and follow its
shutdown prompt.

## Run tests and verify the environment

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m pip --version
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -c "import sys; assert sys.prefix != sys.base_prefix; print(sys.executable)"
.\.venv\Scripts\python.exe -c "import pandas, numpy, matplotlib, seaborn, plotly, streamlit, openpyxl, jupyterlab, ipykernel, pytest; print('All ten packages import successfully')"
.\.venv\Scripts\python.exe -m jupyter kernelspec list
.\.venv\Scripts\python.exe -m pytest
git --version
git check-ignore -v .venv/Scripts/python.exe .env "data/raw/Online Retail.xlsx"
```

Tests cover positive-sales revenue, distinct invoices, AOV, credit composition,
duplicate policy, source quality evidence, metric validation, invalid inputs,
date boundaries, shared filters, drilldown targets and Back navigation, empty
results, CSV export, navigation, and explorer search. Their small artificial fixtures are
used only in tests. The application never substitutes them for real retail data.
VS Code's Testing panel discovers pytest tests under `tests/`.

### Dashboard verification

| Check | Observed result |
| --- | --- |
| Python and environment | Python 3.11.5; executable and prefix point to `.venv` |
| Package imports | All ten requested packages imported successfully |
| Dependency compatibility | `pip check`: no broken requirements |
| pytest | Focused analytical and Streamlit AppTest coverage; run the command above for the current test count |
| Real workbook calculations | Independently reconciled sales revenue, unique invoices, units, and product/country revenue totals |
| Streamlit behavior | Six pages, shared filters, duplicate policy, reset, explorer search, source auditing, and chart drilldowns; see Phase 1 verification |
| Streamlit server | Local health endpoint returned HTTP 200 / `ok`; homepage returned HTTP 200 |
| GitHub | Repository: [eilrahcdev/RetailPulse](https://github.com/eilrahcdev/RetailPulse); automated tests configured in GitHub Actions |
| Ignore rules | Environment, caches, secrets, temporary files, and datasets excluded; source and `.gitkeep` files retained |
| VS Code extensions | Python 2026.10.0 present; Jupyter 2025.9.1 installed and listed |
| Official dataset | All 541,909 source rows preserved; 5,268 exact repeats marked before normalization |

The original workbook and both learning notebooks are not modified by the
dashboard. Workspace interpreter and notebook kernel selection remain editor
settings you can check manually. Browser inspection and its limits are recorded
in `docs/validation.md`.

## Dataset

Use the **UCI Online Retail** dataset, not Online Retail II:

- Official source: <https://archive.ics.uci.edu/dataset/352/online+retail>
- Official archive: <https://archive.ics.uci.edu/static/public/352/online%2Bretail.zip>
- Required file after extracting the archive: `data/raw/Online Retail.xlsx`

The official workbook was downloaded during initial setup (23,715,344 bytes).
Its SHA-256 checksum is
`43465a06f2ccf7c8b5bd2892bc7defb52f97487934fe93b16ae4c3936424676d`.
It is ignored by Git, so a fresh checkout needs its own download.

To download manually, open the official source, click **Download**, open the ZIP,
and save `Online Retail.xlsx` under `data/raw/`. Keep this raw file unchanged.
Do not put it in `data/processed/`. The dashboard cleans a copy in memory.

The expected fields are `InvoiceNo`, `StockCode`, `Description`, `Quantity`,
`InvoiceDate`, `UnitPrice`, `CustomerID`, and `Country`.

Credit: Chen, D. (2015). Online Retail [Dataset]. UCI Machine Learning Repository.
<https://doi.org/10.24432/C5BW33>. License: CC BY 4.0. Retain this attribution in
future project reports.

### What each source column means

| Column | Meaning |
| --- | --- |
| InvoiceNo | Invoice identifier; a leading C indicates cancellation |
| StockCode | Product/item identifier, stored as text to retain leading zeros |
| Description | Item description; missing descriptions display as Unknown product |
| Quantity | Units on this invoice line; negative quantities can represent credits |
| InvoiceDate | Historical invoice date and time |
| UnitPrice | Price per unit in GBP; not product cost or margin |
| CustomerID | Customer identifier; missing IDs do not invalidate sales |
| Country | Customer's country of residence as recorded by UCI |

### Analytical definitions and limitations

- **Gross positive-sales revenue:** sum of `Quantity × UnitPrice` where the
  quantity and price are positive, identifiers/date are present, values are
  finite, and the invoice is not cancellation-prefixed. This is the main revenue
  KPI. Positive fees or non-merchandise lines remain if they meet those rules.
- **Orders:** distinct invoice numbers among matching valid sales. Invoice line
  count is not order count. **Units:** sum of matching sales quantities.
- **AOV:** selected positive-sales revenue divided by selected unique sales
  invoices. With a product filter, it describes the selected products' value per
  matching invoice, not the value of every item in those whole orders.
- **Returns/cancellations:** valid negative-quantity lines at positive unit prices
  form usable recorded credits. Positive-quantity cancellation invoices require
  review and do not enter positive sales or credit totals.
- **Observed sales less credits:** positive sales minus recorded credit value in
  the selected period. Credits may refer to sales outside the period. This is a
  signed dataset subtotal, not verified accounting net revenue or a return rate.
- **Invalid records:** missing invoice/stock identifiers, invalid dates,
  non-finite values, non-positive prices, and zero quantities stay in the explorer
  as review lines with a reason. Missing countries are labeled Unknown country.
- **Duplicates:** exact repeats across all eight original columns are marked
  before cleaning and retained by default. The optional exclusion keeps the
  first of each exact repeated row. Repeated invoice/product combinations with
  different values are never blindly removed.
- **Descriptions:** stock code defines a product; differing descriptions do not
  split it into separate products. Missing customer IDs and descriptions are
  reported and preserved rather than used to discard valid sales.
- **Comparison:** the immediately preceding equal number of inclusive calendar
  days, with the same country/product/duplicate policy. The full prior period
  must lie inside dataset coverage. A prior value of zero has no percentage
  change. For 1-30 November, comparison dates are 2-31 October, not all October.
- **Trends:** weeks start Monday. Edge weeks/months contain selected dates only.
  The prior trend is shifted forward by the selected number of days before
  aggregation so it aligns on the same chart. No-sales dates within coverage
  appear as zero; no historical comparison is invented outside coverage.
- **Unavailable facts:** this dataset has no supplied category or cost fields.
  The dashboard does not infer categories, gross margin, live sales, or reasons
  behind changes.

## Project files

```text
retailpulse/
|-- .venv/                         # Local Python and installed packages; ignored
|-- .vscode/
|   `-- settings.json              # Relative interpreter and pytest settings
|-- .streamlit/
|   `-- config.toml                # Light palette, telemetry, upload limit
|-- assets/
|   `-- styles.css                 # Scoped spacing and responsive refinements
|-- docs/
|   |-- validation.md              # Original verification evidence
|   |-- implementation-checklist.md # Audited priorities and future phases
|   |-- phase1-analytics.md         # Formulas, scope, and business interpretation
|   `-- phase1-verification.md      # Current tests and rendered verification
|-- data/
|   |-- raw/
|   |   |-- .gitkeep               # Keeps the empty directory in Git
|   |   `-- Online Retail.xlsx     # Official download; ignored when present
|   `-- processed/
|       `-- .gitkeep
|-- notebooks/
|   |-- 01_data_cleaning.ipynb      # Starter notebook, import check only
|   `-- 02_exploratory_analysis.ipynb
|-- src/
|   |-- __init__.py                # Makes src an importable Python package
|   |-- data_processing.py         # Workbook loading, classification, filters, CSV
|   |-- metrics.py                 # Revenue, orders, AOV, credits, aggregations
|   |-- charts.py                  # Shared Plotly figure builders
|   |-- utils.py                   # Number/date formatting and default period
|   |-- data_quality.py            # Source findings and reconciliation
|   |-- drilldowns.py              # Bounded record-selection targets
|   |-- returns_analysis.py        # Observed credit breakdowns
|   |-- quality_views.py           # Data Quality Center presentation
|   |-- drilldown_views.py         # Selection and context restoration
|   `-- views.py                   # Reusable Streamlit page sections
|-- tests/
|   |-- conftest.py                # Clearly artificial analytical test fixtures
|   |-- test_data_processing.py    # Classification, quality, filters, CSV
|   |-- test_metrics.py            # Business calculations and reconciliation
|   `-- test_app.py                # Navigation, filters, and explorer behavior
|-- app.py                         # Cached data, navigation, shared filters
|-- pyproject.toml                 # Editable package and pytest configuration
|-- requirements.txt               # Pinned environment and local editable package
|-- README.md
`-- .gitignore                     # Excludes environments, datasets, caches, secrets
```

The `.gitkeep` files retain the data directories even though dataset contents
are ignored. Environments, secrets, local agent tooling, caches, and packaging
outputs are also excluded from Git.

## GitHub workflow

The repository is hosted at
[eilrahcdev/RetailPulse](https://github.com/eilrahcdev/RetailPulse).
GitHub Actions installs the pinned Windows/Python 3.11 environment, checks
dependency compatibility, and runs pytest on pushes and pull requests to `main`.
Tests use artificial fixtures and do not require the UCI workbook or credentials.

For subsequent changes:

```powershell
git switch -c your-change
.\.venv\Scripts\python.exe -m pytest -q
git add <files-you-changed>
git commit -m "Describe your change"
git push -u origin your-change
```

Open a pull request into `main` and review the automated checks before merging.

## Day 1: Dataset exploration

When you are ready to begin analysis:

1. Confirm the file and its official column definitions.
2. Load the workbook in a notebook and inspect a few rows, shape, and data types.
3. Count missing values and duplicate rows before deciding what they mean.
4. Inspect cancellation identifiers, negative quantities, and zero prices.
5. Write down revenue, order, and return definitions before calculating KPIs.

Use your notebooks to practice these steps independently and compare your
calculations with the documented dashboard rules. Do not overwrite the raw
workbook. Dashboard implementation leaves these notebook exercises to you.
