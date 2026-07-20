# SKALA Day 1 Individual Assignment

## Assignment title

Data Collection Mini Pipeline (`데이터 수집 미니 파이프라인`)

## Objective

Build a small practical pipeline that collects external data, validates it, saves it in two formats, compares storage performance, and verifies code quality.

## Required APIs

Use all three instructor-specified APIs.

### 1. Open-Meteo

Seoul hourly temperature and precipitation probability for three days:

```text
https://api.open-meteo.com/v1/forecast?latitude=37.5665&longitude=126.9780&hourly=temperature_2m,precipitation_probability&forecast_days=3&timezone=Asia/Seoul
```

### 2. Countries.dev

South Korea country information:

```text
https://countries.dev/alpha/KOR
```

### 3. ip-api

IP-based location information:

```text
http://ip-api.com/json/8.8.8.8
```

Do not silently replace these APIs with alternatives.

## Mandatory requirements

### Environment

- Create and activate a Python virtual environment.
- Manage required packages with `requirements.txt`.
- The lecture environment is based on Python 3.11; use Python 3.11 when available.

### Concurrent collection

- Use `asyncio` and `httpx`.
- Collect all three APIs concurrently using `asyncio.gather()`.
- Confirm that all three responses are valid.
- Use finite timeouts and explicit HTTP error handling.

### Schema validation

- Extract only the fields needed for the output.
- Define Pydantic v2 models.
- Validate types and reasonable value ranges.
- Include exception handling for invalid types or invalid response data.

### Storage and benchmark

- Save only validated data.
- Save the data in both CSV and Parquet formats.
- Measure and print:
  - CSV write time
  - CSV read time
  - Parquet write time
  - Parquet read time
- Compare the same logical data in both formats.

### Testing, style, and Git

- Write at least one pytest schema-validation test.
- `ruff check .` must complete without errors.
- Keep meaningful Git commit history.
- Include comments that explain the important functions and processing flow; missing comments may reduce the score.

## Grading rubric

| Category | Points | Requirements |
|---|---:|---|
| Environment and concurrent collection | 35 | venv, requirements.txt, all three APIs collected concurrently with `asyncio.gather()`, valid responses |
| Schema validation and storage comparison | 45 | Pydantic v2, invalid-type exception handling, CSV and Parquet output, timing results |
| Tests and commits | 10 | At least one passing pytest test, no Ruff errors, Git commit history |
| Completeness | 10 | Sufficient comments and overall completion |

## Repository constraints

The Day 1 slides do **not** prescribe a specific GitHub repository name.
They also do not explicitly require the repository to be Public because the submitted artifact is a ZIP file.

Recommended repository name:

```text
skala-day1-data-pipeline
```

Other clear names are acceptable, for example:

```text
skala-day1-pipeline
skala-python-day1
```

Use lowercase letters and hyphens; avoid spaces and Korean characters in the repository name to reduce path and tooling issues.

## Submission artifacts

Submit both items below.

### 1. Full source-code ZIP

The required ZIP filename format is:

```text
캠퍼스명_반_이름_실습명.zip
```

Example:

```text
서울_1반_홍길동_day1종합실습.zip
```

The slides instruct students to connect the project to GitHub, download the repository folder structure as-is, and submit it as a ZIP.

Before creating the ZIP, exclude local-only files such as:

```text
.venv/
__pycache__/
.pytest_cache/
.ruff_cache/
.DS_Store
```

### 2. Execution-results PDF

Include:

- screenshots of actual execution results;
- evidence that all three APIs were collected;
- CSV and Parquet creation results;
- read/write timing results;
- pytest results;
- Ruff results;
- personal analysis of the code;
- additional opinions, improvement ideas, and code-quality improvements.

## Deadline stated in the slides

- First deadline: before the end of the Day 1 course
- Second deadline: one hour before the Day 2 course starts
- Late submission may be penalized

## Final acceptance checklist

- [ ] Virtual environment and `requirements.txt` are ready.
- [ ] All three specified APIs are used.
- [ ] Requests run concurrently through `asyncio.gather()`.
- [ ] Pydantic v2 validates types and ranges.
- [ ] Invalid data is handled.
- [ ] CSV and Parquet files are both generated.
- [ ] Four read/write timing values are printed.
- [ ] At least one pytest test passes.
- [ ] Ruff reports no errors.
- [ ] Git commit history exists.
- [ ] Important code is sufficiently commented.
- [ ] ZIP filename follows the required format.
- [ ] The PDF contains actual screenshots and personal analysis.
