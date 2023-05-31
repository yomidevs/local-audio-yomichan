# Steps:
# 1. Clone the repository (git clone https://github.com/themoeway/local-audio-yomichan.git)
# 2. Run Powershell as an administrator (likely necessary for New-Item to work)
# 3. cd into local-audio-yomichan
# 4. Run the following commands (the first command allows executing powershell scripts for the session)
#     PS > Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process
#     PS > ./link.ps1

$PluginName = "LocalAudioDev"
$PluginPath = "~/AppData/Roaming/Anki2/addons21"

if (Test-Path -Path $PluginPath) {
    # Example: New-Item -Path C:\LinkDir -ItemType SymbolicLink -Value F:\RealDir
    $LinkDir = Join-Path $PluginPath $PluginName
    $SrcDir = Join-Path $pwd "plugin"
    New-Item -Path $LinkDir -ItemType SymbolicLink -Value $SrcDir 
}
