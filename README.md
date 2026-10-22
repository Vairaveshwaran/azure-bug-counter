<<<<<<< HEAD
# Azure DevOps Bug Counter

A simple Flask web application that connects to Azure DevOps and calculates the unique number of bugs that entered Active/Doing or Reopened state within a selected date range.

## Features

- Select Bug - Proj 1, 2, 3, or 4
- Select start date and end date
- Fetch bug information from Azure DevOps
- Read work item revision history
- Count unique matching bugs
- Display the result on the web page

## Technologies

- Python
- Flask
- Requests
- Azure DevOps REST API
- HTML/CSS

## Project Structure

```text
azure-bug-counter/
│
├── app.py
├── requirements.txt
├── .env
├── .gitignore
├── README.md
│
└── templates/
    └── index.html

    Setup
1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

2. Install dependencies
pip install -r requirements.txt

3. Create .env
Create a .env file in the project root:

AZURE_ORG=rahul31
AZURE_PROJECT=itecApplication
AZURE_PAT=YOUR_PERSONAL_ACCESS_TOKEN

Replace YOUR_PERSONAL_ACCESS_TOKEN with the Azure DevOps PAT.

Do not commit or share the .env file.

4. Run the application
python app.py

Open:
http://127.0.0.1:5000/

Usage
1.Select a project.
2.Select the start date.
3.Select the end date.
4.Click Bug Count.
5.The application displays the unique bug count for the selected project and date range.
=======
# azure-bug-counter
A Python Flask-based web application that integrates with the Azure DevOps REST API to count unique bugs by project, date range, and status. Features include revision history analysis, date validation, duplicate prevention, and error handling to simplify bug tracking and improve reporting efficiency.
>>>>>>> 0a7fdb9c39ddafbd0456ed14b302387eceea4936
