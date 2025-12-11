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

## Informazioni Necessarie per Diagnosi Completa

1. **Pagina specifica del popup**: Serve il codice della pagina che contiene il bottone "Firma"
2. **Errori JavaScript**: Console browser (F12) quando si tenta di firmare
3. **Tipo di firma digitale**: È un controllo ActiveX? Un applet Java? Un plugin?
4. **URL completo**: Dell'applicazione per verificare configurazioni
5. **Versione Edge**: Versione corrente e target del downgrade

## Debugging Steps

1. Aprire F12 PRIMA di cliccare su "Firma"
2. Andare in tab "Console"
3. Cliccare su "Firma"
4. Catturare eventuali errori rossi
5. Verificare tab "Network" per richieste fallite
6. Controllare se appare icona IE nella barra indirizzi (conferma modalità IE attiva)

## File da Analizzare

Per una soluzione completa servono:
- [ ] login.jsp (frame work)
- [ ] Pagina con bottone "Firma"
- [ ] File JavaScript collegati
- [ ] DLBServletMain (servlet principale)
- [ ] Eventuali file .cab o .ocx (controlli ActiveX)
