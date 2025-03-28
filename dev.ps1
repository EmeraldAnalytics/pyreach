[CmdletBinding()]
param(
    [Parameter(Position=0)]
    [string]$Command
)

# Function to check if container is running
function Test-ContainerRunning {
    return docker ps -q --filter "name=pyreach-dev" | Select-String -Quiet .
}

# Function to check if container exists but is stopped
function Test-ContainerExists {
    return docker ps -a -q --filter "name=pyreach-dev" | Select-String -Quiet .
}

# Function to build and start container
function Start-DevContainer {
    if (Test-ContainerRunning) {
        Write-Host "Development container is already running."
        return
    }

    if (Test-ContainerExists) {
        Write-Host "Found stopped container. Starting it..."
        docker start pyreach-dev
        return
    }

    Write-Host "Building development container..."
    try {
        docker build -t pyreach-dev -f Dockerfile .
    } catch {
        Write-Host "Error building container: $_"
        return
    }
    
    Write-Host "Starting development container..."
    try {
        docker run -d `
            --name pyreach-dev `
            -v "${PWD}:/workspace" `
            -w /workspace `
            pyreach-dev `
            tail -f /dev/null
        Write-Host "Container started successfully!"
    } catch {
        Write-Host "Error starting container: $_"
        return
    }
}

# Function to stop container
function Stop-DevContainer {
    if (-not (Test-ContainerExists)) {
        Write-Host "No development container found."
        return
    }

    if (-not (Test-ContainerRunning)) {
        Write-Host "Container is already stopped."
        return
    }

    Write-Host "Stopping development container..."
    try {
        docker stop pyreach-dev
        docker rm pyreach-dev
        Write-Host "Container stopped and removed successfully!"
    } catch {
        Write-Host "Error stopping container: $_"
    }
}

# Function to enter container
function Enter-DevContainer {
    if (-not (Test-ContainerRunning)) {
        Write-Host "Container is not running. Starting it..."
        Start-DevContainer
    }

    if (Test-ContainerRunning) {
        Write-Host "Connecting to container..."
        docker exec -it pyreach-dev bash
    } else {
        Write-Host "Failed to start container. Please check Docker is running and try again."
    }
}

# Function to show container status
function Show-ContainerStatus {
    if (Test-ContainerRunning) {
        Write-Host "Development container is running."
    } elseif (Test-ContainerExists) {
        Write-Host "Development container exists but is stopped."
    } else {
        Write-Host "No development container found."
    }
}

# Main script
switch ($Command) {
    "start" { Start-DevContainer }
    "stop" { Stop-DevContainer }
    "enter" { Enter-DevContainer }
    "status" { Show-ContainerStatus }
    default { 
        Write-Host "Usage: .\dev.ps1 {start|stop|enter|status}"
        Write-Host "  start  - Build and start the container"
        Write-Host "  stop   - Stop and remove the container"
        Write-Host "  enter  - Enter the container (starts it if needed)"
        Write-Host "  status - Show container status"
    }
} 