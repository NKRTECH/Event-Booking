# PowerShell examples to test the Event Booking API
# Run from PowerShell

$base = 'http://127.0.0.1:8000'

Write-Host "GET /health"
Invoke-RestMethod -Method Get -Uri "$base/health" | ConvertTo-Json -Depth 4

Write-Host "GET /events"
Invoke-RestMethod -Method Get -Uri "$base/events" | ConvertTo-Json -Depth 4

Write-Host "POST /events (create a sample event)"
$body = @{
    title = 'PS Test Event'
    description = 'Created via PowerShell Invoke-RestMethod'
    start_time = (Get-Date).AddHours(1).ToString('s')
    end_time = (Get-Date).AddHours(2).ToString('s')
    capacity = 5
} | ConvertTo-Json

Invoke-RestMethod -Method Post -Uri "$base/events" -Body $body -ContentType 'application/json' | ConvertTo-Json -Depth 4

Write-Host "GET /events (after create)"
Invoke-RestMethod -Method Get -Uri "$base/events" | ConvertTo-Json -Depth 4
