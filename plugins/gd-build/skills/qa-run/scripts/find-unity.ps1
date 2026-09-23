# Copied from unity-kit scripts/find-unity.ps1 (MIT (c) 2026 Benjamin Curlier) - see ATTRIBUTION.md. Unchanged except this header.
# Lists installed Unity editors as JSON: [{version, channel, exe}], newest first.
# Channel: stable (f), beta (b), alpha (a).
# -Modules also reports build-support modules per editor (dedicated server, il2cpp, platforms)
# by inspecting PlaybackEngines — needed by netcode/dedicated-server preflights.
param(
    [string]$SearchRoot = "C:\Program Files\Unity\Hub\Editor",
    [switch]$Modules
)

# Unity version directories are 6000.0.58f1 — dotted numbers with the channel letter and its build
# fused to the last component. A string sort puts 6000.0.9f1 ahead of 6000.0.58f1, and a bare
# [version] cast chokes on "58f1", so the key is the numeric core, then the channel (stable > beta >
# alpha), then the channel build.
$channelOrder = @{ "f" = 3; "b" = 2; "a" = 1 }
function Get-VersionKey([string]$v) {
    if ($v -match '^(\d+(?:\.\d+)+)(?:([abf])(\d+))?') {
        $suffix = [string]$matches[2]
        $rank = 0
        if ($channelOrder.ContainsKey($suffix)) { $rank = $channelOrder[$suffix] }
        $build = 0
        if ($matches[3]) { $build = [int]$matches[3] }
        return [pscustomobject]@{ core = [version]$matches[1]; rank = $rank; build = $build }
    }
    # A directory name that is not a Unity version sorts last instead of throwing.
    [pscustomobject]@{ core = [version]"0.0"; rank = -1; build = 0 }
}

$editors = @(Get-ChildItem -Path $SearchRoot -Directory -ErrorAction SilentlyContinue | ForEach-Object {
    $exe = Join-Path $_.FullName "Editor\Unity.exe"
    if (Test-Path $exe) {
        $v = $_.Name
        $channel = if ($v -match "f\d") { "stable" }
                   elseif ($v -match "b\d") { "beta" }
                   elseif ($v -match "a\d") { "alpha" }
                   else { "unknown" }
        $entry = [pscustomobject]@{ version = $v; channel = $channel; exe = $exe }
        if ($Modules) {
            $pe = Join-Path $_.FullName "Editor\Data\PlaybackEngines"
            $winVariations = Join-Path $pe "WindowsStandaloneSupport\Variations"
            $mods = [pscustomobject]@{
                "windows-server" = (Test-Path $winVariations) -and
                    @(Get-ChildItem $winVariations -Directory -ErrorAction SilentlyContinue |
                      Where-Object Name -like "*server*").Count -gt 0
                "windows-il2cpp" = (Test-Path $winVariations) -and
                    @(Get-ChildItem $winVariations -Directory -ErrorAction SilentlyContinue |
                      Where-Object Name -like "*il2cpp*").Count -gt 0
                "linux"          = Test-Path (Join-Path $pe "LinuxStandaloneSupport")
                "linux-server"   = (Test-Path (Join-Path $pe "LinuxStandaloneSupport\Variations")) -and
                    @(Get-ChildItem (Join-Path $pe "LinuxStandaloneSupport\Variations") -Directory -ErrorAction SilentlyContinue |
                      Where-Object Name -like "*server*").Count -gt 0
                "android"        = Test-Path (Join-Path $pe "AndroidPlayer")
                "webgl"          = Test-Path (Join-Path $pe "WebGLSupport")
                "ios"            = Test-Path (Join-Path $pe "iOSSupport")
            }
            $entry | Add-Member -NotePropertyName modules -NotePropertyValue $mods
        }
        $entry
    }
})

if ($editors.Count -eq 0) {
    Write-Error "No Unity editors found under $SearchRoot. Install one via Unity Hub, or pass -SearchRoot if Hub uses a custom install location."
    exit 1
}

$sorted = $editors | Sort-Object -Descending -Property @(
    { (Get-VersionKey $_.version).core },
    { (Get-VersionKey $_.version).rank },
    { (Get-VersionKey $_.version).build }
)

# -InputObject with @() keeps single-element results as a JSON array on both PS 5.1 and 7+
ConvertTo-Json -InputObject @($sorted)
