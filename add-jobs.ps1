# ------------------ Config ------------------
$hostName = "http://localhost:1234"
$endpoint = "/jobs"
$url = "$hostName$endpoint"

# payloads
$jobPayloads = @(
    @{
        task = "resize-image"
        image_url = "https://example.com/image1.jpg"
        size = @(128, 128)
    },
    @{
        task = "convert-pdf"
        file_url = "https://example.com/document.pdf"
        output_format = "docx"
    },
    @{
        task = "send-email"
        to = "alice@example.com"
        subject = "Welcome!"
        body = "Thanks for signing up."
    }
)

# ------------------ Request Logic ------------------
foreach ($payload in $jobPayloads) {
    $jsonBody = $payload | ConvertTo-Json -Depth 5
    Write-Host "`nSending job:" -ForegroundColor Cyan
    Write-Host $jsonBody

    try {
        $response = Invoke-RestMethod -Method Post -Uri $url -Body $jsonBody -ContentType "application/json"
        Write-Host "Success: Job created with ID $($response.request_id)" -ForegroundColor Green
    } catch {
        Write-Host "Failed to create job: $_" -ForegroundColor Red
    }
}
