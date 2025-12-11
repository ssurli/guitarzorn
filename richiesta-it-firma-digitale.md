# Richiesta Supporto IT - Impossibilità Firma Digitale su Windows 11

**Data**: 11 Dicembre 2025
**Utente**: Stefano Surlinelli
**Sistema**: Windows 11 Pro ver. 24H2
**Applicazione**: OfficeWeb - Sistema Firma Digitale PkNet

---

## Problema Riscontrato

**Non è possibile effettuare la firma digitale dei documenti su Windows 11.**

### Causa Identificata

Il sistema di firma digitale dell'applicazione OfficeWeb utilizza **Java Applet** (tecnologia PkNet di Intesi Group), che richiede:

1. ✅ **Java Runtime Environment** - Installato e configurato correttamente
2. ✅ **Browser Internet Explorer 11** - ❌ **NON DISPONIBILE su Windows 11**

### Analisi Tecnica

**Componenti analizzati:**
- Pagina firma: `JFfirma.jsp`
- Componente Java: `com.intesi.pknet.applet.PkNetApplet.class`
- JAR richiesti: `pknetjappl.jar`, `pknetj.jar`, `itext-1.4.jar`
- Tag HTML: `<object classid="clsid:8AD9C840-044E-11D1-B3E9-00805F499D93">`

**Configurazioni Edge testate:**
- ✅ Modalità Internet Explorer attiva per il sito
- ✅ Popup autorizzati (HTTP e HTTPS)
- ✅ Java installato con eccezioni sicurezza configurate
- ❌ **Edge modalità IE NON supporta Java Applet**

**Limitazione Microsoft:**
- Internet Explorer 11 è stato **definitivamente disabilitato** in Windows 11
- Edge modalità IE **non supporta** plugin Java Applet
- Nessun browser moderno supporta più Java Applet (deprecato dal 2017)

### Documentazione Fornitore

Le istruzioni originali Insiel specificano:

> "N.B. Per il corretto funzionamento del programma è richiesta la presenza del browser Microsoft Internet Explorer ver 6.0 S.P.1 o superiore."

**Conclusione**: L'applicazione NON è compatibile con Windows 11.

---

## Impatto Operativo

- ❌ Impossibile firmare delibere e decreti
- ❌ Blocco workflow approvazioni
- ❌ Necessario intervento manuale o cambio postazione

**Urgenza**: **ALTA**

---

## Soluzioni Richieste

### Soluzione Immediata (Temporanea)

Per continuare operatività:

1. **Accesso postazione Windows 10**
   - PC dedicato per firme digitali
   - Oppure notebook aziendale con Windows 10

2. **Accesso remoto/Citrix**
   - Se disponibile server terminal con Windows 10/Server + IE11

3. **Macchina virtuale**
   - VM Windows 10 su infrastruttura aziendale

### Soluzione Definitiva (Permanente)

Contattare **Insiel S.p.A.** (fornitore OfficeWeb) per:

1. **Versione aggiornata applicazione**
   - Eliminazione dipendenza Java Applet
   - Compatibilità Windows 11 e browser moderni

2. **Integrazione firma digitale moderna**
   - Client desktop (Dike, ArubaSign, InfoCert, ecc.)
   - Web extension moderna
   - API firma remota

3. **Applicazione nativa**
   - Client Windows standalone per firma documenti
   - Integrazione con smart card/token USB

### Alternative da Valutare

- **Altri utenti Windows 11**: Verificare se problema diffuso
- **Policy aziendale**: Mantenere postazioni Windows 10 per applicazioni legacy
- **Roadmap aggiornamento**: Piano migrazione da OfficeWeb legacy

---

## Informazioni Tecniche per Supporto

**Ambiente attuale:**
```
Sistema Operativo: Windows 11 Pro ver. 24H2
Browser: Microsoft Edge 143.0.3650.75 (64 bit)
Java: JRE installato e configurato
URL Applicazione: https://protocollo.ssr.uslnordovest.toscana.it/adweb/
```

**Fornitore Software:**
```
Insiel S.p.A.
Via S. Francesco d'Assisi, 43 - 34133 Trieste
Tel. 040/3737.3111 - Fax 040/3737.333
Prodotto: OfficeWeb
Componente: PkNet (firma digitale)
```

**Documentazione completa:**
- Analisi problema: `edge-ie-popup-problem.md`
- Soluzioni dettagliate: `soluzione-firma-java-applet.md`
- Codice sorgente analizzato: `JFfirma-source.html`

---

## Azioni Richieste

### Breve termine (1-2 giorni):
- [ ] Fornire accesso postazione Windows 10 per firme urgenti
- [ ] Verificare se esistono alternative software già disponibili

### Medio termine (1-2 settimane):
- [ ] Contattare Insiel per upgrade applicazione
- [ ] Verificare compatibilità con altri sistemi firma digitale

### Lungo termine (1-3 mesi):
- [ ] Piano migrazione da Java Applet a tecnologia moderna
- [ ] Valutare alternative a OfficeWeb se non aggiornabile

---

## Contatti

**Utente**: Stefano Surlinelli
**Email**: [inserire email]
**Telefono**: [inserire telefono]

**Disponibilità per test/supporto**: Immediata

---

*Documento generato in data 11/12/2025*
*Repository analisi tecnica: guitarzorn/claude/fix-signature-popup-edge-*
