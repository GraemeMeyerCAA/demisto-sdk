$ErrorActionPreference = 'Continue'
$env:Path = 'C:\Users\robert\AppData\Roaming\Python\Python314\Scripts;' + $env:Path
$env:DEMISTO_SDK_IGNORE_CONTENT_WARNING = '1'
$env:PYTHONUTF8 = '1'

$xmlDir = 'C:\Users\robert\Code\demisto-sdk\windows_test_xml'

# Final-pass rerun: chunks whose remaining failures have post-commit fixes.
$dirs = @('common','run_cmd','update_release_notes','validate')

$wallTimeoutSec = 1500
foreach ($d in $dirs) {
    $target = "demisto_sdk/commands/$d"
    $xml = Join-Path $xmlDir "$d.xml"
    if (Test-Path $xml) { Remove-Item $xml -Force }
    $stdout = Join-Path $xmlDir "$d.log"
    Write-Host "==> $d"
    $p = Start-Process -FilePath 'poetry' -ArgumentList @(
        'run','pytest',$target,
        '--timeout=60','--timeout-method=thread',
        '--tb=line','-q','-p','no:sugar',
        "--junit-xml=$xml",'-o','junit_logging=no'
    ) -NoNewWindow -PassThru -RedirectStandardOutput $stdout -RedirectStandardError "$stdout.err"
    if (-not $p.WaitForExit($wallTimeoutSec * 1000)) {
        Write-Host "  TIMEOUT after ${wallTimeoutSec}s, killing"
        try { Stop-Process -Id $p.Id -Force -ErrorAction Stop } catch {}
        Get-CimInstance Win32_Process -Filter "ParentProcessId = $($p.Id)" | ForEach-Object {
            try { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue } catch {}
        }
    } else {
        Write-Host "  exit=$($p.ExitCode)"
    }
}
Write-Host "DONE"
