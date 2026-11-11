# Collegamento desktop GioOver25

Su ogni PC Windows, dopo aver scaricato il repository, fai doppio clic su
`Crea_collegamento.bat` nella cartella principale.

Il collegamento `GioOver25.lnk` viene creato sul desktop dell'utente corrente,
compreso il desktop reindirizzato a OneDrive. Avvia `Avvia_GioOver25.bat` e usa
`assets/icons/GioOver25.ico`. L'icona deve restare nel repository.

Puoi ripetere l'operazione: aggiorna lo stesso collegamento senza aggiungere
copie. Se sposti o rinomini la cartella del repository, eseguila nuovamente.
I vecchi collegamenti con nomi diversi restano invariati.

Il collegamento e' locale al PC: non va aggiunto a Git. Icona e script invece
sono versionati. Python e le dipendenze del progetto devono essere installati.
Lo script non richiede privilegi amministrativi. Il wrapper usa la policy
Bypass soltanto per il processo PowerShell avviato, senza modificare le
impostazioni permanenti. Eventuali policy aziendali restano applicabili.
