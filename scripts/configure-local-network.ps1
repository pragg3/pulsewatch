$ErrorActionPreference = "Stop"

Write-Host "Detecting PulseWatch host network configuration..."

# Find the preferred IPv4 default route.
$route = Get-NetRoute -DestinationPrefix "0.0.0.0/0" |
    Where-Object {
        $_.State -eq "Alive"
    } |
    Sort-Object RouteMetric, InterfaceMetric |
    Select-Object -First 1

if (-not $route) {
    throw "Could not determine the active IPv4 default route."
}

# Determine the host IPv4 address belonging to that interface.
$hostIp = Get-NetIPAddress `
    -InterfaceIndex $route.InterfaceIndex `
    -AddressFamily IPv4 |
    Where-Object {
        $_.AddressState -eq "Preferred" -and
        $_.IPAddress -notlike "127.*" -and
        $_.IPAddress -notlike "169.254.*"
    } |
    Select-Object -First 1 -ExpandProperty IPAddress

if (-not $hostIp) {
    throw "Could not determine the host IPv4 address."
}

# Determine the DNS server configured for the same interface.
$dnsServer = Get-DnsClientServerAddress `
    -InterfaceIndex $route.InterfaceIndex `
    -AddressFamily IPv4 |
    Select-Object -ExpandProperty ServerAddresses |
    Where-Object {
        $_ -and
        $_ -notlike "127.*"
    } |
    Select-Object -First 1

if (-not $dnsServer) {
    throw "Could not determine the IPv4 DNS server."
}

Write-Host ""
Write-Host "Detected network configuration:"
Write-Host "  Interface:  $($route.InterfaceAlias)"
Write-Host "  Host IP:    $hostIp"
Write-Host "  DNS server: $dnsServer"
Write-Host ""

# Create or update installation-specific Kubernetes configuration.
#
# These values are deliberately generated locally and are not stored
# in the PulseWatch Git repository.
kubectl create configmap pulsewatch-installation-config `
    --from-literal="PULSEWATCH_HOST_IP=$hostIp" `
    --from-literal="NETWORK_DNS_SERVER=$dnsServer" `
    --dry-run=client `
    -o yaml |
    kubectl apply -f -

if ($LASTEXITCODE -ne 0) {
    throw "Failed to update pulsewatch-installation-config."
}

Write-Host ""
Write-Host "PulseWatch installation configuration updated."

# Environment variables populated through envFrom are read when the
# container starts, so recreate the backend pod when the Deployment exists.
$backendDeployment = kubectl get deployment pulsewatch-backend `
    --ignore-not-found `
    -o name

if ($LASTEXITCODE -ne 0) {
    throw "Failed to query the PulseWatch backend Deployment."
}

if ($backendDeployment) {
    Write-Host "Restarting PulseWatch backend..."

    kubectl rollout restart deployment/pulsewatch-backend

    if ($LASTEXITCODE -ne 0) {
        throw "Failed to restart the PulseWatch backend."
    }

    kubectl rollout status deployment/pulsewatch-backend

    if ($LASTEXITCODE -ne 0) {
        throw "PulseWatch backend rollout did not complete successfully."
    }

    Write-Host ""
    Write-Host "PulseWatch backend restarted successfully."
}

Write-Host ""
Write-Host "Configuration complete."
Write-Host "  PULSEWATCH_HOST_IP=$hostIp"
Write-Host "  NETWORK_DNS_SERVER=$dnsServer"