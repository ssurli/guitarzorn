# 🚀 PkNet Patch - Installazione Rapida

## File dalla Patch del Collega

Questi file permettono a PkNet di comunicare con la smart card per la firma digitale.

## ⚡ Installazione Veloce

### Opzione 1: Script Automatico (CONSIGLIATO)

1. Scarica tutti i file in una cartella
2. Tasto destro su `installa-pknet.ps1`
3. Seleziona **"Esegui con PowerShell"**
4. Segui le istruzioni a schermo
5. Riavvia browser

### Opzione 2: Manuale

1. Crea cartella: `C:\Users\<TUO_USERNAME>\pknetj.1.9\pknetj\`
2. Copia dentro tutti i file .dll, cacerts, usercerts
3. Modifica `pknet.properties` con il tuo username
4. Copia `pknet.properties` nella stessa cartella
5. Riavvia PC

## 📋 File Inclusi

- `JSCCryptoki.dll` + `JSCCryptoki64.dll` - Driver smart card
- `OCFPCSC1.DLL` + `OCFPCSC1_64.DLL` - Driver PC/SC
- `cacerts` - Certificati CA
- `usercerts` - Certificati utente
- `pknet.properties` - Configurazione

## ⚠️ IMPORTANTE

**Questa patch funziona con Internet Explorer 11 + Java Applet**

Se hai Windows 11:
- IE11 NON è disponibile
- Edge modalità IE NON supporta Java Applet
- **Chiedi al collega come fa a usarla!**

Possibilità:
- Il collega usa Windows 10
- Il collega ha PkNet Web (versione moderna)
- Il collega ha altra configurazione

## ❓ Domande per il Collega

Prima di installare, chiedi:

1. **Windows 10 o 11?**
2. **Quale browser usi? IE11, Edge, altro?**
3. **Funziona in Edge su Windows 11?**
4. **Hai altri software installati?**
5. **Usi PkNet Web o Java Applet?**

## 📚 Documentazione Completa

Leggi `GUIDA-INSTALLAZIONE-PKNET-PATCH.md` per:
- Istruzioni dettagliate
- Troubleshooting
- Configurazioni avanzate

## 🆘 Supporto

Se non funziona:
1. Verifica percorsi in `pknet.properties`
2. Controlla che username sia corretto
3. Verifica smart card inserita
4. Chiedi supporto al collega o IT

---

**Creato**: 12/12/2025
**Repository**: guitarzorn - commit `pkjnet_files`
