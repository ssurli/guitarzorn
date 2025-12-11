# Soluzione Problema Firma Digitale - Java Applet

## Problema Identificato

❌ **Il sistema di firma usa Java Applet (tecnologia obsoleta dal 2017)**

### Dettagli Tecnici
- **Sistema firma**: PkNet di Intesi Group
- **Componente**: `com.intesi.pknet.applet.PkNetApplet.class`
- **JAR files**: pknetjappl.jar, pknetj.jar, itext-1.4.jar
- **Algoritmo**: SHA-256
- **URL applet**: https://protocollo.ssr.uslnordovest.toscana.it:443/adweb/applet/

### Perché Non Funziona
Edge (come Chrome, Firefox, Safari) ha **rimosso il supporto per Java Applet**:
- Chrome: rimosso nel 2015
- Firefox: rimosso nel 2016
- Edge: mai supportato nativamente
- Internet Explorer 11: ultimo browser a supportarlo (con Java installato)

## ✅ Soluzioni Possibili

### Soluzione 1: Usare Internet Explorer 11 (CONSIGLIATO)

**Passaggi:**

1. **Verifica se IE11 è disponibile:**
   - Apri menu Start
   - Cerca "Internet Explorer"
   - Se presente, aprilo

2. **Installa Java Runtime Environment (JRE):**
   - Vai su: https://www.java.com/it/download/
   - Scarica e installa Java (versione 8 Update 391 o superiore)
   - Durante installazione, assicurati di abilitare il plugin per browser

3. **Configura IE11:**
   - Apri IE11
   - Menu Strumenti → Opzioni Internet → Sicurezza
   - Seleziona "Intranet locale"
   - Click su "Siti" → "Avanzate"
   - Aggiungi: `https://protocollo.ssr.uslnordovest.toscana.it`
   - Click OK

4. **Configura Java:**
   - Apri "Configura Java" dal Pannello di Controllo
   - Tab "Sicurezza"
   - Click "Modifica elenco siti"
   - Aggiungi: `https://protocollo.ssr.uslnordovest.toscana.it`
   - Click OK

5. **Apri l'applicazione con IE11:**
   - Usa IE11 per accedere all'applicazione
   - La firma dovrebbe funzionare

⚠️ **Nota:** Microsoft ha disabilitato IE11 in Windows 11. Se usi Windows 11, questa soluzione potrebbe non essere disponibile.

### Soluzione 2: Richiedere Aggiornamento Software (SOLUZIONE A LUNGO TERMINE)

Contattare il fornitore del sistema (Intesi Group o USL Nord Ovest Toscana IT) per:

1. **Versione aggiornata** che usa tecnologie moderne:
   - Firma digitale tramite applicazione nativa (non browser)
   - Integrazione con middleware di firma (es. Dike, Aruba Key)
   - Web extension moderna invece di Java Applet

2. **Alternative già disponibili:**
   - Verificare se esiste un'applicazione desktop per la firma
   - Verificare se esiste un modulo di firma alternativo

### Soluzione 3: Usare Applicazione Desktop (se disponibile)

Alcuni sistemi PkNet hanno anche:
- Client desktop per firma documenti
- Integrazione con software di firma di terze parti (Dike, ArubaSign, ecc.)

Chiedere all'amministratore IT se disponibili.

### Soluzione 4: Macchina Virtuale con Windows 7/IE11 (Solo per emergenze)

Se assolutamente necessario e nessuna altra soluzione funziona:
- Creare VM con Windows 7
- Installare IE11 + Java
- Usare solo per firma documenti

⚠️ **Non consigliato**: Windows 7 non è più supportato, rischi di sicurezza.

## 🔧 Procedura Consigliata

### Per Utente Singolo:
1. Prova **Soluzione 1** (IE11) se disponibile
2. Contatta IT aziendale per **Soluzione 2** (software aggiornato)
3. Chiedi alternative disponibili (**Soluzione 3**)

### Per IT Aziendale:
1. **Immediato**: Fornire workstation con IE11 + Java per firme urgenti
2. **Breve termine**: Contattare Intesi Group per upgrade
3. **Lungo termine**: Migrare a soluzione firma moderna (es. integrazione Dike/Aruba)

## 📋 Informazioni per Supporto IT

Quando contatti il supporto IT o Intesi Group, fornisci:

```
Sistema: PkNet firma digitale
URL: https://protocollo.ssr.uslnordovest.toscana.it/adweb/
Componente: com.intesi.pknet.applet.PkNetApplet.class
Problema: Java Applet non supportato in Edge 143.0.3650.75
Browser testati: Edge con modalità IE (non funziona)
Richiesta: Upgrade a tecnologia moderna o alternativa a Java Applet
```

## ⚠️ Importante

**Non è un problema di configurazione Edge** - è un limite tecnologico:
- Edge modalità IE NON supporta Java Applet
- Popup sono già autorizzati correttamente
- Configurazione Edge corretta

Il problema è che l'applicazione usa tecnologia obsoleta che nessun browser moderno supporta più.

## Link Utili

- Java download: https://www.java.com/it/download/
- Intesi Group (produttore PkNet): https://www.intesigroup.com/
- Microsoft IE11 info: https://support.microsoft.com/windows/internet-explorer-help
