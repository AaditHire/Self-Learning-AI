$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$source = Join-Path $root "vendor\goco\6a029b8030f0701fd6d5f7f84c68d4e0c5cb790e\goco-compiler\src\main\java"
$javaHome = Join-Path $root ".tools\jdk-25.0.1+8"
$classes = Join-Path $root ".artifacts\compiler\classes"
$jar = Join-Path $root ".artifacts\compiler\goco-compiler-6a029b8-deterministic.jar"

if (-not (Test-Path -LiteralPath $source)) { throw "Pinned source snapshot is missing" }
if (-not (Test-Path -LiteralPath (Join-Path $javaHome "bin\javac.exe"))) { throw "Pinned JDK is missing" }
New-Item -ItemType Directory -Force -Path $classes | Out-Null
$sources = Get-ChildItem -LiteralPath $source -Recurse -File -Filter "*.java" | ForEach-Object FullName
& (Join-Path $javaHome "bin\javac.exe") -encoding UTF-8 -d $classes $sources
if ($LASTEXITCODE -ne 0) { throw "javac failed" }
python (Join-Path $PSScriptRoot "build_deterministic_jar.py") $classes $jar
if ($LASTEXITCODE -ne 0) { throw "deterministic JAR packaging failed" }
Get-FileHash -Algorithm SHA256 -LiteralPath $jar
