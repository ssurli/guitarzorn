# ========================================
# SCRIPT INSTALLAZIONE PKNET PATCH
# Per Windows 11 - Firma Digitale
# ========================================

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  INSTALLAZIONE PKNET PATCH" -ForegroundColor Cyan
Write-Host "  Firma Digitale - Windows 11" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Ottieni username corrente
$username = $env:USERNAME
Write-Host "Username rilevato: $username" -ForegroundColor Green

# Definisci percorso installazione
$pknetPath = "C:\Users\$username\pknetj.1.9\pknetj"
Write-Host "Percorso installazione: $pknetPath" -ForegroundColor Green
Write-Host ""

# Verifica se i file sorgente esistono
$requiredFiles = @(
    "JSCCryptoki.dll",
    "JSCCryptoki64.dll",
    "OCFPCSC1.DLL",
    "OCFPCSC1_64.DLL",
    "cacerts",
    "usercerts"
)

Write-Host "Verifica file richiesti..." -ForegroundColor Yellow
$missingFiles = @()
foreach ($file in $requiredFiles) {
    if (!(Test-Path $file)) {
        $missingFiles += $file
        Write-Host "  [X] $file - MANCANTE" -ForegroundColor Red
    } else {
        Write-Host "  [OK] $file" -ForegroundColor Green
    }
}

if ($missingFiles.Count -gt 0) {
    Write-Host ""
    Write-Host "ERRORE: File mancanti!" -ForegroundColor Red
    Write-Host "Assicurati di eseguire lo script dalla cartella contenente i file della patch." -ForegroundColor Red
    Write-Host ""
    Write-Host "File mancanti:" -ForegroundColor Red
    foreach ($file in $missingFiles) {
        Write-Host "  - $file" -ForegroundColor Red
    }
    Write-Host ""
    Write-Host "Premi un tasto per uscire..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
    exit 1
}

Write-Host ""
Write-Host "Tutti i file sono presenti!" -ForegroundColor Green
Write-Host ""

# Chiedi conferma
Write-Host "Procedere con l'installazione? (S/N): " -ForegroundColor Yellow -NoNewline
$conferma = Read-Host
if ($conferma -ne "S" -and $conferma -ne "s") {
    Write-Host "Installazione annullata." -ForegroundColor Red
    exit 0
}

Write-Host ""
Write-Host "Inizio installazione..." -ForegroundColor Cyan
Write-Host ""

# Crea cartelle
Write-Host "Creazione cartelle..." -ForegroundColor Yellow
try {
    New-Item -ItemType Directory -Force -Path $pknetPath | Out-Null
    Write-Host "  [OK] Cartelle create: $pknetPath" -ForegroundColor Green
} catch {
    Write-Host "  [ERRORE] Impossibile creare cartelle: $_" -ForegroundColor Red
    exit 1
}

# Copia file DLL
Write-Host ""
Write-Host "Copia file DLL..." -ForegroundColor Yellow
foreach ($file in $requiredFiles) {
    try {
        Copy-Item $file -Destination $pknetPath -Force
        Write-Host "  [OK] Copiato: $file" -ForegroundColor Green
    } catch {
        Write-Host "  [ERRORE] Impossibile copiare $file : $_" -ForegroundColor Red
    }
}

# Crea pknet.properties con percorsi corretti
Write-Host ""
Write-Host "Creazione file pknet.properties..." -ForegroundColor Yellow

$propertiesContent = @"
#Generated $(Get-Date -Format "ddd MMM dd HH:mm:ss 'CET' yyyy")
WrapperLibraryPath=C:\\Users\\$username\\pknetj.1.9\\pknetj\\JSCCryptoki.dll
WrapperLibraryVersion=1.0.5.22
WrapperLibraryPath64=C:\\Users\\$username\\pknetj.1.9\\pknetj\\JSCCryptoki64.dll
"@

try {
    $propertiesContent | Out-File -FilePath "$pknetPath\pknet.properties" -Encoding ASCII -Force
    Write-Host "  [OK] File pknet.properties creato" -ForegroundColor Green
} catch {
    Write-Host "  [ERRORE] Impossibile creare pknet.properties: $_" -ForegroundColor Red
}

# Crea anche in .pknetj (alternativa)
$altPath = "C:\Users\$username\.pknetj"
Write-Host ""
Write-Host "Creazione backup in .pknetj..." -ForegroundColor Yellow
try {
    New-Item -ItemType Directory -Force -Path $altPath | Out-Null
    $propertiesContent | Out-File -FilePath "$altPath\pknet.properties" -Encoding ASCII -Force
    Write-Host "  [OK] Backup creato in: $altPath" -ForegroundColor Green
} catch {
    Write-Host "  [AVVISO] Impossibile creare backup: $_" -ForegroundColor Yellow
}

# Riepilogo
Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  INSTALLAZIONE COMPLETATA!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "File installati in:" -ForegroundColor White
Write-Host "  $pknetPath" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configurazione:" -ForegroundColor White
Write-Host "  - JSCCryptoki.dll (32-bit)" -ForegroundColor Cyan
Write-Host "  - JSCCryptoki64.dll (64-bit)" -ForegroundColor Cyan
Write-Host "  - OCFPCSC1.DLL (32-bit)" -ForegroundColor Cyan
Write-Host "  - OCFPCSC1_64.DLL (64-bit)" -ForegroundColor Cyan
Write-Host "  - cacerts (certificati CA)" -ForegroundColor Cyan
Write-Host "  - usercerts (certificati utente)" -ForegroundColor Cyan
Write-Host "  - pknet.properties (configurazione)" -ForegroundColor Cyan
Write-Host ""

# Mostra contenuto pknet.properties
Write-Host "Contenuto pknet.properties:" -ForegroundColor White
Write-Host "---------------------------------------" -ForegroundColor Gray
Get-Content "$pknetPath\pknet.properties" | ForEach-Object { Write-Host "  $_" -ForegroundColor Cyan }
Write-Host "---------------------------------------" -ForegroundColor Gray
Write-Host ""

# Istruzioni finali
Write-Host "PROSSIMI PASSI:" -ForegroundColor Yellow
Write-Host "  1. Riavvia il browser (chiudi completamente Edge)" -ForegroundColor White
Write-Host "  2. Inserisci la smart card nel lettore" -ForegroundColor White
Write-Host "  3. Apri l'applicazione OfficeWeb" -ForegroundColor White
Write-Host "  4. Prova a firmare un documento" -ForegroundColor White
Write-Host ""
Write-Host "NOTE IMPORTANTI:" -ForegroundColor Yellow
Write-Host "  - Questa patch potrebbe funzionare SOLO con IE11" -ForegroundColor Red
Write-Host "  - Edge (anche modalita IE) NON supporta Java Applet" -ForegroundColor Red
Write-Host "  - Se hai Windows 11, chiedi al collega come fa" -ForegroundColor Red
Write-Host ""

Write-Host "Premi un tasto per uscire..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
