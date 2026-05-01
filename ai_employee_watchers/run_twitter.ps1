# Run Twitter Poster from Windows PowerShell
# Execute with: powershell -ExecutionPolicy Bypass -File run_twitter.ps1

Set-Location "E:\Full-Time-Equivalent-Hackathon-0\Full-Time-Equivalent-0\ai_employee_watchers"

# Check if uv is available
if (Get-Command uv -ErrorAction SilentlyContinue) {
    uv run python src/ai_employee_watchers/twitter_poster.py --message "AI Employee Gold Tier - Automated posting test! #AIEmployee #ClaudeCode #Automation"
} else {
    Write-Host "uv not found. Trying python directly..."
    python src/ai_employee_watchers/twitter_poster.py --message "AI Employee Gold Tier - Automated posting test! #AIEmployee #ClaudeCode #Automation"
}
