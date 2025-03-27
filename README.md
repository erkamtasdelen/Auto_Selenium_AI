# WebSelector - Automated Web Interaction Using Selenium & Gemini AI

## Overview
WebSelector is a Python-based automation tool that leverages Selenium WebDriver and Google Gemini AI to interact with websites dynamically. It can perform automated login, navigate through web pages, and extract elements using AI-generated XPath selectors.

## Features
- **Automated Login:** Uses AI to identify login fields and interact with web elements.
- **Dynamic Web Navigation:** Handles navigation based on AI-generated actions.
- **AI-Powered XPath Selection:** Uses Google Gemini AI to generate optimal XPath selectors.
- **Handles Hidden Elements:** Detects and avoids hidden elements in web pages.
- **Interactive Action Execution:** Supports actions like clicks, text input, hovering, and pressing keys dynamically.
- **Error Handling and Learning:** Stores failed XPath attempts and adjusts future interactions accordingly.

## Dependencies
Make sure you have the following dependencies installed:

```bash
pip install selenium webdriver-manager beautifulsoup4 google-generativeai
```

## Setup and Usage

### 1. Configure API Key
Replace the placeholder `google_api="----"` with your actual Google Gemini API key in the script:

```python
X = WebSelector(google_api="YOUR_API_KEY")
```

### 2. Initialize WebSelector
Create an instance of `WebSelector` to start web automation.

```python
X = WebSelector(google_api="YOUR_API_KEY")
```

### 3. Perform Automated Login
Use the `LOGIN` function to log into a website by providing the URL, username, and password:

```python
X.LOGIN("https://example.com/login", "your_username", "your_password")
```

### 4. Execute Custom Actions
The `tryit` function can be used to automate other interactions, such as searching for a term on Google:

```python
X.tryit("Go to Twitter and perform actions")
```

## How It Works
1. **Loads the Web Page:** The `Goto(url)` function loads the specified webpage.
2. **Extracts HTML Content:** `TakeAHtml()` captures the page source.
3. **Generates Actions with AI:** The `AskToAI(question)` function queries Gemini AI to generate Selenium actions.
4. **Executes Actions:** Executes actions such as clicking, entering text, and handling popups.
5. **Handles Errors:** If an XPath fails, it is logged and AI attempts alternative selections.

## Example Workflow
1. **User provides a mission** (e.g., "Log in to Twitter").
2. **WebSelector fetches HTML source** and detects interactive elements.
3. **AI generates a JSON list of actions** including clicking, sending keys, and handling popups.
4. **The script executes the actions sequentially** until the mission is completed.
5. **If an error occurs**, the script logs failed XPaths and retries with new AI-generated ones.

## Important Considerations
- Ensure your **Google Gemini AI API key** is valid.
- Keep **ChromeDriver up to date** to avoid compatibility issues.
- Be mindful of **website policies** regarding automation and bot activity.
- This tool is for **educational purposes** and should not be used for unauthorized access.

## Author
Developed by erkamtasdelen.

## License
This project is licensed under the MIT License.

