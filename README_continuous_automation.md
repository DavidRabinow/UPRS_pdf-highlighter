# Continuous Automation System

This document describes the new continuous automation functionality that tracks the last processed Payee Name and continues processing from where it left off.

## Overview

The continuous automation system automatically processes multiple Payee Names from a table by:

1. **Tracking Progress**: Stores the last processed Payee Name
2. **Resuming**: Continues from the next row after the last processed Payee Name
3. **Stopping Conditions**: Stops on 3 consecutive failures, max companies limit, or end of table
4. **Error Recovery**: Tracks consecutive failures and can resume from any point

## Key Features

### Tracking Variables

The system tracks several variables in the `SeleniumAutomation` class:

- `last_payee_name`: The last Payee Name that was successfully processed
- `consecutive_failures`: Number of consecutive processing failures
- `max_companies`: Maximum number of companies to process (default: 50)
- `companies_processed`: Counter for successfully processed companies

### Processing Flow

1. **Initial Setup**: Browser setup, login, navigation to Process Imported Files
2. **Table Population**: Perform initial search to populate the table with results
3. **Continuous Loop**:
   - Find next row to process based on `last_payee_name`
   - Double-click the row to open it
   - Process the Payee Name through BizFileOnline
   - Update tracking variables
   - Check stopping conditions
4. **Completion**: Stop when conditions are met

## Usage

### Basic Usage

```python
from automation import SeleniumAutomation

# Create automation instance
automation = SeleniumAutomation()

# Configure settings (optional)
automation.max_companies = 20  # Process up to 20 companies
automation.last_payee_name = None  # Start from beginning

# Run continuous automation
search_text = "your_search_criteria"
automation.run(search_text)
```

### Resume from Specific Point

```python
# Resume from a specific Payee Name
automation.last_payee_name = "EXAMPLE COMPANY LLC"
automation.max_companies = 10  # Process 10 more companies
automation.run(search_text)
```

### Test Script

Use the provided test script to try the functionality:

```bash
python test_continuous_automation.py
```

## Methods

### Core Methods

- `find_and_process_next_row()`: Finds and processes the next row based on `last_payee_name`
- `process_single_payee(payee_name)`: Processes a single Payee Name through BizFileOnline
- `should_stop_processing()`: Checks if processing should stop
- `reset_failure_count()`: Resets consecutive failure count after success

### Tracking Methods

- `find_and_process_next_row()`: Returns the Payee Name of the processed row
- `should_stop_processing()`: Returns True if stopping conditions are met
- `reset_failure_count()`: Resets failure count after successful processing

## Stopping Conditions

The automation stops when any of these conditions are met:

1. **3 Consecutive Failures**: If 3 Payee Names fail to process in a row
2. **Max Companies Reached**: If the number of processed companies reaches `max_companies`
3. **End of Table**: If there are no more rows to process

## Error Handling

- **Consecutive Failures**: Tracked and used as a stopping condition
- **Individual Failures**: Logged but don't stop the process unless they accumulate
- **Resume Capability**: Can resume from any point by setting `last_payee_name`

## Configuration

### Default Settings

```python
self.max_companies = 50  # Maximum companies to process
self.last_payee_name = None  # Start from beginning
self.consecutive_failures = 0  # Reset failure count
self.companies_processed = 0  # Reset processed count
```

### Customization

```python
# Set custom limits
automation.max_companies = 100

# Resume from specific point
automation.last_payee_name = "COMPANY NAME"

# Reset counters
automation.consecutive_failures = 0
automation.companies_processed = 0
```

## Logging

The system provides detailed logging for:

- Processing progress
- Payee Name tracking
- Success/failure status
- Stopping conditions
- Error details

Logs are written to both console and file (`continuous_automation.log`).

## Example Output

```
=== STARTING CONTINUOUS SELENIUM AUTOMATION ===
Initial search text provided: 'search_criteria'
Maximum companies to process: 10
=== PROCESSING ITERATION 1 ===
Companies processed so far: 0
Consecutive failures: 0
=== FINDING AND PROCESSING NEXT ROW ===
Last processed Payee Name: None
✅ Processing row 1 with Payee Name: 'COMPANY A LLC'
✅ Successfully processed Payee: 'COMPANY A LLC'
Total companies processed: 1
=== PROCESSING ITERATION 2 ===
Companies processed so far: 1
Consecutive failures: 0
=== FINDING AND PROCESSING NEXT ROW ===
Last processed Payee Name: COMPANY A LLC
✅ Processing row 2 with Payee Name: 'COMPANY B LLC'
✅ Successfully processed Payee: 'COMPANY B LLC'
Total companies processed: 2
...
=== CONTINUOUS AUTOMATION COMPLETED ===
✅ Total companies processed: 10
✅ Final consecutive failures: 0
✅ Automation completed - reached maximum limit of 10 companies
```

## Troubleshooting

### Common Issues

1. **Table Not Populated**: Ensure the initial search returns results
2. **Row Not Found**: Check if the Payee Name exists in the table
3. **BizFileOnline Issues**: Verify network connectivity and site availability
4. **Browser Issues**: Ensure Chrome is properly installed and accessible

### Debug Information

The system provides extensive debug output including:

- Row scanning details
- Payee Name matching
- Processing status
- Error details

Check the log files for detailed information about any issues.
