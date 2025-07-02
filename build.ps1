# run-compose.ps1

# Ensure script stops on error
$ErrorActionPreference = "Stop"

function Check-EmptyVars {
    param (
        [string[]]$vars
    )
    foreach ($var in $vars) {
        if ([string]::IsNullOrWhiteSpace((Get-Variable -Name $var -ValueOnly))) {
            Write-Host "ERROR: Environment variable '$var' is missing or empty!" -ForegroundColor Red
            exit 1
        }
    }
}

Write-Host "Checking if Docker is installed..."

if (!(Get-Command "docker" -ErrorAction SilentlyContinue)) {
    Write-Error "Docker is not installed or not available in PATH. Please install Docker Desktop."
    exit 1
}

if (!(Get-Command "docker-compose" -ErrorAction SilentlyContinue)) {
    Write-Error "docker-compose is not installed. Please ensure Docker Compose v1 or v2 is available."
    exit 1
}

Write-Host "Docker is installed..."

Get-Content .env | ForEach-Object {
    if ($_ -match "^(.*)=(.*)$") {
        $envName = $matches[1].Trim()
        $envValue = $matches[2].Trim()
        [System.Environment]::SetEnvironmentVariable($envName, $envValue, "Process")
    }
}

# URIs for both MongoDB and RabbitMQ are hardcoded in the compose file. 

$MONGO_DB_NAME = $env:MONGO_DB_NAME
$MONGO_COLLECTION_NAME = $env:MONGO_COLLECTION_NAME
$RABBITMQ_QUEUE_NAME=$env:RABBITMQ_QUEUE_NAME

Check-EmptyVars @(
    "MONGO_DB_NAME"
    "MONGO_COLLECTION_NAME"
    "RABBITMQ_QUEUE_NAME"
)


Write-Host "Starting docker-compose build and up..."
# Export environment variables so docker-compose picks them up automatically
$env:MONGO_DB_NAME = $MONGO_DB_NAME
$env:MONGO_COLLECTION_NAME = $MONGO_COLLECTION_NAME
$env:RABBITMQ_QUEUE_NAME = $RABBITMQ_QUEUE_NAME

docker-compose up --build
