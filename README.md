# Finance Analysis

This project automates the analysis of private finance data by processing monthly account statements, writing the extracted data into Google Sheets and sending a status notification by e-mail.

## Features

- Process monthly bank account statements from *Volksbank* (pdf-format)
- Extract and categorize financial transactions
- Write processed data into a Google Sheet for easy tracking and visualization
- Send an e-mail notification with script execution status (success/failure)


## Architecture and Workflow

| Step                                                      | Who        | Where                 | When
|:--------------------------------------------------------- |---------   |-----------------------|-----------------------------------   |
| 1. Download account statement from bank                   | Manual     | PC (local) or mobile  | As soon as available (1st or 2nd day of the month) |
| 2. Upload account statement to designated GDrive folder   | Manual     | PC (local) or mobile  | After download                       |
| 3. Analyze account statement and write data to GSheet     | Script     | GCP                   | At beginning of month                |
| 4. Send notification e-mail about script status           | Script     | GCP                   | Immediately after analysis           |

## Technischer Aufbau

- tbd.

## Getting Started

- tbd.

## Usage

- tbd.

## Security Considerations

- tbd.

## Future Enhancements
