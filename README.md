# Finance Analysis

This project automates the analysis of private finance data by processing monthly account statements, writing the extracted data into Google Sheets and sending a status notification by e-mail.

## Features

- Process monthly bank account statements from *Volksbank* (pdf-format)
- Extract financial transactions
- Write processed data into a Google Sheet for easy tracking and manual additions
- Visualize data in Google Looker Studio


## Architecture and Workflow

| Step                                                      | Who        | Where                 | When
|:--------------------------------------------------------- |---------   |-----------------------|-----------------------------------   |
| 1. Download account statement from bank                   | Manual     | PC (local) or mobile  | As soon as available (1st or 2nd day of the month) |
| 2. Upload account statement to designated GDrive folder   | Manual     | PC (local) or mobile  | After download                       |
| 3. Analyze account statement and write data to GSheet     | Script     | GCP                   | 0 7 3 * *                            |
| 4. Visualize data in Looker Studio                        | Script     | GCP                   | 24/7 available                       |


## Getting Started

- tbd.

## Usage

- tbd.


## Deployment

- The app/ main script is deployed on GCP
- Execution status: 0 7 3 * * (Every third day of a month at 7am.)
- tbd.


### Deploy changes

1. docker build -t gcr.io/cool-plasma-452619-v4/finance-analysis:latest .
2. docker push gcr.io/cool-plasma-452619-v4/finance-analysis:latest
3. gcloud run jobs update finance-analysis-job --image gcr.io/cool-plasma-452619-v4/finance-analysis:latest --region europe-west3
-> Cloud Trigger startet automatisch mit der neuesten Version

---

## ⚠️ Security Notice: pip vulnerability (GHSA-4xh5-x5gv-qwph)

This project uses `pip` for dependency management.  
At the moment, `pip-audit` reports the following known vulnerability:

- **Package:** pip  
- **Version:** 25.2  
- **Advisory:** [GHSA-4xh5-x5gv-qwph](https://github.com/advisories/GHSA-4xh5-x5gv-qwph)  
- **Status:** No fixed version is available yet (latest release 25.2 is still affected).  

### Why is this ignored?
- The vulnerability only affects `pip` when installing **malicious or untrusted source distributions (sdists)**.  
- In this project, packages are only installed from **trusted sources (PyPI wheels / pinned dependencies)**.  
- Blocking merges until a fixed pip release exists would prevent other critical updates.

### Mitigation
- The advisory is temporarily ignored in `pip-audit` runs using the ID `GHSA-4xh5-x5gv-qwph`.  
- We will upgrade to the first non-vulnerable release of `pip` (expected > 25.2) as soon as it becomes available.  
- Until then, all installs are limited to trusted sources to minimize risk.

➡️ **Action Item:** Keep track of pip releases and remove this ignore rule once a patched version is published.

---

## Future Enhancements

- Create AI/ML model to add categories automatically
