# PowerShell script para manejar Docker Compose
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("start", "stop", "restart", "logs", "status", "test", "port")]
    [string]$Command,
    
    [Parameter(Mandatory=$false)]
    [string]$Port = "8083"
)

$ComposeFile = "docker-compose.yml"
$EnvFile = ".env.docker-compose"

function Start-MCP {
    Write-Host "🐳 Starting MCP-Odoo with Docker Compose..." -ForegroundColor Green
    docker-compose --env-file $EnvFile up --build -d
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Container started successfully!" -ForegroundColor Green
        docker-compose ps
    }
}

function Stop-MCP {
    Write-Host "⏹️  Stopping MCP-Odoo container..." -ForegroundColor Yellow
    docker-compose down
}

function Restart-MCP {
    Write-Host "🔄 Restarting MCP-Odoo container..." -ForegroundColor Blue
    Stop-MCP
    Start-Sleep 2
    Start-MCP
}

function Show-Logs {
    Write-Host "📋 Container logs:" -ForegroundColor Cyan
    docker-compose logs -f --tail=50 mcp-odoo
}

function Show-Status {
    Write-Host "📊 Container status:" -ForegroundColor Cyan
    docker-compose ps
    
    # Test health endpoint
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8083/health" -TimeoutSec 5
        Write-Host "✅ Health check: $($response.status)" -ForegroundColor Green
        Write-Host "🛠️  Service: $($response.service)" -ForegroundColor Green
        Write-Host "🔧 Tools: $($response.tools_count)" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Test-Connection {
    Write-Host "🧪 Testing connection..." -ForegroundColor Magenta
    
    $endpoints = @(
        @{ Name = "Health"; Url = "http://localhost:8083/health" },
        @{ Name = "SSE"; Url = "http://localhost:8083/sse" },
        @{ Name = "Root"; Url = "http://localhost:8083/" }
    )
    
    foreach ($endpoint in $endpoints) {
        try {
            $response = Invoke-WebRequest -Uri $endpoint.Url -TimeoutSec 10
            $icon = if ($response.StatusCode -in @(200, 404)) { "✅" } else { "❌" }
            Write-Host "$icon $($endpoint.Name): $($response.StatusCode)" -ForegroundColor $(if ($response.StatusCode -in @(200, 404)) { "Green" } else { "Red" })
        }
        catch {
            Write-Host "❌ $($endpoint.Name): ERROR - $($_.Exception.Message)" -ForegroundColor Red
        }
    }
}

function Change-Port {
    param([string]$NewPort)
    
    Write-Host "🔧 Changing external port to $NewPort..." -ForegroundColor Blue
    
    if (Test-Path $ComposeFile) {
        $content = Get-Content $ComposeFile -Raw
        $content = $content -replace '- "\d+:8083"', "- `"$NewPort:8083`""
        Set-Content $ComposeFile -Value $content
        Write-Host "✅ Port changed to $NewPort. Run 'restart' to apply changes." -ForegroundColor Green
    }
    else {
        Write-Host "❌ docker-compose.yml not found!" -ForegroundColor Red
    }
}

# Main command execution
switch ($Command) {
    "start" { Start-MCP }
    "stop" { Stop-MCP }
    "restart" { Restart-MCP }
    "logs" { Show-Logs }
    "status" { Show-Status }
    "test" { Test-Connection }
    "port" { Change-Port -NewPort $Port }
    default { Write-Host "❌ Unknown command: $Command" -ForegroundColor Red }
}
