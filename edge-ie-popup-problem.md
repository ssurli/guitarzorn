# Problema Popup Firma Digitale - Edge IE Mode

## Descrizione Problema
Applicazione aziendale legacy (Office WEB - Atti Deliberativi) non apre popup per firma digitale in Edge modalità IE.

## Codice Analizzato
File: index.html (frameset principale)
- Usa frameset (tecnologia deprecata)
- Charset: iso-8859-1
- Frame principali:
  - topbar: servlet DLBServletMain
  - menu/esci: navigazione laterale
  - work: contenuto principale (login.jsp)
  - bottoni: pulsanti azione
  - nascosto/nascosto2/chiusura: frame nascosti

## Possibili Cause del Problema

### 1. Popup Bloccati da Edge
Edge in modalità IE potrebbe bloccare window.open() se:
- Non è attivato da un'azione utente diretta
- Usa parametri non supportati
- Ha problemi di sicurezza

### 2. ActiveX Disabilitato
Se la firma digitale usa controlli ActiveX:
- Edge non supporta nativamente ActiveX
- Serve configurazione specifica in modalità IE

### 3. JavaScript Legacy
Codice JavaScript obsoleto potrebbe non funzionare correttamente:
- document.all
- attachEvent invece di addEventListener
- Metodi deprecati

### 4. Problemi con Frameset
I frameset possono causare problemi di:
- Cross-frame scripting
- Referenze tra frame non funzionanti
- window.parent/top non accessibili

## Soluzioni Possibili

### Soluzione 1: Configurare Edge per Sito in Modalità IE
Aggiungere il sito alla lista di compatibilità IE:
1. Aprire Edge
2. edge://settings/defaultBrowser
3. Aggiungere URL a "Internet Explorer mode pages"
4. Riavviare Edge

### Soluzione 2: Abilitare Popup per il Sito
1. edge://settings/content/popups
2. Aggiungere eccezione per il dominio dell'applicazione

### Soluzione 3: Configurare Opzioni Modalità IE
In Group Policy o Registry:
- Abilitare ActiveX se necessario
- Configurare zone di sicurezza
- Disabilitare popup blocker per intranet

### Soluzione 4: Modificare Codice JavaScript (se possibile)
Correggere window.open() per essere compatibile:
```javascript
// Vecchio modo (potrebbe non funzionare)
window.open(url, name, features);

// Modo più compatibile
var popup = window.open(url, name, features);
if (!popup || popup.closed || typeof popup.closed == 'undefined') {
    alert('Popup bloccato! Abilita i popup per questo sito.');
}
```

## Configurazione Attuale Edge

**✅ Modalità IE Configurata Correttamente:**
- URL: https://protocollo.ssr.uslnordovest.toscana.it/adweb/jsp/index.htm
- Data aggiunta: 2025/11/17
- Scadenza: 2025/12/17
- Ricaricamento automatico in modalità IE: ATTIVO

**✅ Popup Autorizzati:**
- https://protocollo.ssr.uslnordovest.toscana.it (HTTPS)
- http://protocollo.ssr.uslnordovest.toscana.it:80 (HTTP)

**✅ Versione Edge:**
- 143.0.3650.75 (Build ufficiale) (64 bit)

**❌ PROBLEMA CRITICO: F12 Blocca l'Applicazione**
- Quando si preme F12, l'applicazione si blocca e non procede
- Possibile causa: Codice anti-debug o incompatibilità strumenti dev con modalità IE
- Soluzione: Analisi diretta del codice sorgente con Ctrl+U

**⚠️ Nota:** La configurazione modalità IE scade il 17/12/2025, verrà rinnovata automaticamente all'accesso

## Stato Diagnosi

1. ✅ **URL completo**: https://protocollo.ssr.uslnordovest.toscana.it/adweb/jsp/index.htm
2. ✅ **Modalità IE**: Configurata correttamente
3. ✅ **Versione Edge**: 143.0.3650.75 (64 bit)
4. ✅ **Configurazione popup**: Autorizzati per dominio (HTTP e HTTPS)
5. ❌ **Errori JavaScript**: F12 blocca applicazione - impossibile usare console
6. ✅ **Codice sorgente analizzato**: JFfirma.jsp - pagina firma digitale
7. ✅ **Tipo di firma digitale**: **Java Applet (PkNet di Intesi Group)**
8. ✅ **Causa del problema**: Edge NON supporta Java Applet (tecnologia obsoleta)

## 🎯 PROBLEMA IDENTIFICATO

**Il sistema NON usa popup, ma un Java Applet per la firma digitale.**

### Dettagli Tecnici:
- **Sistema**: PkNet di Intesi Group
- **Componente**: `com.intesi.pknet.applet.PkNetApplet.class`
- **JAR files**: pknetjappl.jar, pknetj.jar, itext-1.4.jar
- **Tag HTML**: `<object classid="clsid:8AD9C840-044E-11D1-B3E9-00805F499D93">`

### Perché Non Funziona:
- Java Applet è obsoleto dal 2017
- Edge (e tutti i browser moderni) NON supportano Java Applet
- Edge modalità IE NON è compatibile con Java Applet
- Serve Internet Explorer 11 nativo con Java installato

### Soluzione:
Vedere file: **soluzione-firma-java-applet.md** per procedure dettagliate.

## Debugging Steps (Aggiornati per problema F12)

**⚠️ F12 NON UTILIZZABILE** - blocca l'applicazione

**Metodo Alternativo:**
1. Sulla pagina della delibera (con bottone "Firma"), premere **Ctrl+U**
2. Si apre visualizzazione codice sorgente
3. Premere **Ctrl+F** e cercare: `firma`, `window.open`, `popup`, `showModalDialog`
4. Copiare tutto il codice JavaScript trovato vicino a questi termini
5. Analizzare il codice per identificare problemi di compatibilità
6. Applicare patch/fix al codice se possibile

**Informazioni da Raccogliere:**
- Tipo di dispositivo firma (smart card, token USB, software)
- Cosa succede ESATTAMENTE quando si clicca "Firma" (nessuna reazione, errore visibile, pagina si blocca?)
- Il popup si è mai aperto con versioni precedenti di Edge? Quale versione?

## File da Analizzare

Per una soluzione completa servono:
- [ ] login.jsp (frame work)
- [ ] Pagina con bottone "Firma"
- [ ] File JavaScript collegati
- [ ] DLBServletMain (servlet principale)
- [ ] Eventuali file .cab o .ocx (controlli ActiveX)
