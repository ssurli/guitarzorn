# 🎯 GUIDA INSTALLAZIONE PkNet - Patch Firma Digitale Windows 11

**Autore**: Patch da collega funzionante
**Data**: 12 Dicembre 2025
**Sistema**: Windows 11 Pro ver. 24H2
**Obiettivo**: Far funzionare firma digitale PkNet senza Internet Explorer 11

---

## ✅ Prerequisiti

Prima di iniziare, verifica di avere:

- [x] **Java JRE installato** (già installato e configurato)
- [x] **Smart card o token USB** funzionante
- [x] **Lettore smart card** collegato al PC
- [x] **File patch dal repository** (già disponibili)

---

## 📦 File della Patch

I seguenti file sono stati recuperati dal PC del collega:

```
JSCCryptoki.dll          (187 KB) - Driver smart card 32-bit
JSCCryptoki64.dll        (227 KB) - Driver smart card 64-bit
OCFPCSC1.DLL             (28 KB)  - PC/SC driver 32-bit
OCFPCSC1_64.DLL          (21 KB)  - PC/SC driver 64-bit
cacerts                  (202 KB) - Certificati CA
cacerts.zip              (105 KB) - Certificati CA compressi
pknet.properties         (4 righe) - Configurazione PkNet
usercerts                (32 bytes) - Certificati utente
```

---

## 🚀 Procedura Installazione

### **Step 1: Crea Cartella PkNet**

1. Apri **Esplora File**
2. Vai su: `C:\Users\<TUO_USERNAME>\`
3. Crea nuova cartella: `pknetj.1.9`
4. Dentro `pknetj.1.9` crea sottocartella: `pknetj`

**Percorso finale**: `C:\Users\<TUO_USERNAME>\pknetj.1.9\pknetj\`

**Sostituisci `<TUO_USERNAME>` con il tuo nome utente Windows!**

### **Step 2: Copia File DLL**

Copia i seguenti file nella cartella `C:\Users\<TUO_USERNAME>\pknetj.1.9\pknetj\`:

```
✓ JSCCryptoki.dll
✓ JSCCryptoki64.dll
✓ OCFPCSC1.DLL
✓ OCFPCSC1_64.DLL
```

### **Step 3: Copia Certificati**

Copia i file certificati nella stessa cartella:

```
✓ cacerts
✓ usercerts
```

(Puoi saltare cacerts.zip se vuoi)

### **Step 4: Configura pknet.properties**

1. Copia il file `pknet.properties` in: `C:\Users\<TUO_USERNAME>\pknetj.1.9\pknetj\`

2. **IMPORTANTE**: Modifica il file con il tuo username!

**Apri** `pknet.properties` con Blocco Note e modifica così:

```properties
#Fri Feb 23 15:27:05 CET 2024
WrapperLibraryPath=C:\\Users\\<TUO_USERNAME>\\pknetj.1.9\\pknetj\\JSCCryptoki.dll
WrapperLibraryVersion=1.0.5.22
WrapperLibraryPath64=C:\\Users\\<TUO_USERNAME>\\pknetj.1.9\\pknetj\\JSCCryptoki64.dll
```

⚠️ **ATTENZIONE**:
- Sostituisci `<TUO_USERNAME>` con il tuo username Windows
- Usa `\\` doppi backslash (non singoli!)
- Esempio: Se il tuo username è "stefano", scrivi:
  ```
  WrapperLibraryPath=C:\\Users\\stefano\\pknetj.1.9\\pknetj\\JSCCryptoki.dll
  ```

### **Step 5: Verifica Struttura**

La struttura finale deve essere:

```
C:\Users\<TUO_USERNAME>\
└── pknetj.1.9\
    └── pknetj\
        ├── JSCCryptoki.dll
        ├── JSCCryptoki64.dll
        ├── OCFPCSC1.DLL
        ├── OCFPCSC1_64.DLL
        ├── cacerts
        ├── usercerts
        └── pknet.properties
```

### **Step 6: Riavvia Browser**

1. Chiudi **completamente** il browser (Edge)
2. Chiudi anche tutti i processi Java (se aperti)
3. Riavvia il PC (consigliato)

### **Step 7: Test Firma Digitale**

1. Inserisci **smart card** nel lettore
2. Apri **Edge** (o Chrome)
3. Vai all'applicazione OfficeWeb
4. Login
5. Prova a **firmare un documento**

---

## ⚠️ Importante: Quale Browser Usare?

**Domanda cruciale**: Il tuo collega usa:
- Internet Explorer 11? (su Windows 10)
- Edge con modalità IE?
- Altro browser?

**Questa patch potrebbe funzionare SOLO con IE11**, perché:
- I file DLL sono per Java Applet
- Java Applet funziona solo in IE11
- Edge (anche con modalità IE) NON supporta Java Applet

### **Se il collega usa Windows 10 + IE11:**

✅ La patch funziona perché:
1. IE11 carica Java Applet
2. Java Applet legge `pknet.properties`
3. `pknet.properties` punta alle DLL
4. DLL comunicano con smart card
5. Firma funziona!

### **Se il collega usa Windows 11:**

⚠️ Devi chiedere al collega:
- Come fa a firmare su Windows 11?
- Usa IE11 in qualche modo?
- Ha altri software installati?
- Usa PkNet Web (versione moderna)?

---

## 🔧 Troubleshooting

### **Problema: Firma non funziona dopo installazione**

**Verifica:**

1. **Username corretto nel file properties?**
   - Apri `pknet.properties`
   - Verifica che il percorso contenga il TUO username
   - Esempio: `C:\\Users\\TUONOME\\pknetj.1.9\\pknetj\\JSCCryptoki64.dll`

2. **File DLL presenti?**
   - Vai in `C:\Users\<TUO_USERNAME>\pknetj.1.9\pknetj\`
   - Verifica che ci siano tutte le 4 DLL

3. **Smart card inserita?**
   - Lettore smart card collegato?
   - Card inserita correttamente?
   - Driver lettore installati?

4. **Java configurato?**
   - Pannello di Controllo → Java
   - Tab "Sicurezza" → Eccezioni sito
   - URL applicazione presente?

### **Problema: File properties non viene letto**

Java cerca `pknet.properties` in diverse posizioni:

1. `C:\Users\<username>\pknetj.1.9\pknetj\`
2. `C:\Users\<username>\.pknetj\`
3. Directory corrente applicazione

**Prova a copiare** `pknet.properties` anche in:
- `C:\Users\<TUO_USERNAME>\.pknetj\pknet.properties`

---

## 📋 Checklist Installazione

- [ ] Creata cartella `C:\Users\<username>\pknetj.1.9\pknetj\`
- [ ] Copiate 4 DLL nella cartella
- [ ] Copiati file certificati (cacerts, usercerts)
- [ ] Copiato e modificato `pknet.properties` con username corretto
- [ ] Verificato percorsi con `\\` doppi backslash
- [ ] Riavviato PC
- [ ] Smart card inserita
- [ ] Lettore collegato
- [ ] Browser chiuso e riaperto
- [ ] Test firma eseguito

---

## ❓ Domande per il Collega

Prima di installare, chiedi al collega:

1. **Sistema operativo**: Windows 10 o Windows 11?
2. **Browser usato**: IE11, Edge, Chrome?
3. **Versione Java**: Quale versione JRE ha installato?
4. **Altri software**: Ha installato altro oltre a questi file?
5. **Funziona con Edge?**: La patch funziona in Edge o solo IE11?
6. **Configurazioni aggiuntive**: Ha fatto altre modifiche al sistema?

---

## 🎯 Script Automatico Installazione

Per facilitare l'installazione, ecco uno script PowerShell:

```powershell
# SCRIPT INSTALLAZIONE PKNET PATCH
# Esegui come Amministratore

$username = $env:USERNAME
$pknetPath = "C:\Users\$username\pknetj.1.9\pknetj"

# Crea cartelle
New-Item -ItemType Directory -Force -Path $pknetPath

# Copia file (assumendo che siano nella directory corrente)
Copy-Item "JSCCryptoki.dll" -Destination $pknetPath
Copy-Item "JSCCryptoki64.dll" -Destination $pknetPath
Copy-Item "OCFPCSC1.DLL" -Destination $pknetPath
Copy-Item "OCFPCSC1_64.DLL" -Destination $pknetPath
Copy-Item "cacerts" -Destination $pknetPath
Copy-Item "usercerts" -Destination $pknetPath

# Crea pknet.properties con percorsi corretti
$propertiesContent = @"
#Generated $(Get-Date)
WrapperLibraryPath=C:\\Users\\$username\\pknetj.1.9\\pknetj\\JSCCryptoki.dll
WrapperLibraryVersion=1.0.5.22
WrapperLibraryPath64=C:\\Users\\$username\\pknetj.1.9\\pknetj\\JSCCryptoki64.dll
"@

$propertiesContent | Out-File -FilePath "$pknetPath\pknet.properties" -Encoding ASCII

Write-Host "Installazione completata in: $pknetPath"
Write-Host "Riavvia il browser e prova a firmare un documento"
```

**Come usare lo script:**
1. Salva come `installa-pknet.ps1`
2. Metti lo script nella cartella con i file DLL
3. Tasto destro → "Esegui con PowerShell"
4. Riavvia browser

---

## ✅ Risultato Atteso

Se tutto funziona:

1. Apri applicazione OfficeWeb in Edge/IE11
2. Vai su documento da firmare
3. Click su "Firma"
4. **L'applet Java si carica** (vedi interfaccia PkNet)
5. Inserisci PIN smart card
6. Documento firmato con successo!

---

## 🆘 Se Non Funziona

**Contatta il collega e chiedi:**
- Screenshot della sua cartella pknetj
- Quale browser usa esattamente
- Se ha Windows 10 o 11
- Se ha fatto altre configurazioni

**Oppure contatta IT aziendale:**
- Mostra questa guida
- Spiega che un collega ha la soluzione
- Chiedi supporto per replicare la configurazione

---

**Ultimo aggiornamento**: 12/12/2025
**File sorgente**: Commit `pkjnet_files` in repository guitarzorn
