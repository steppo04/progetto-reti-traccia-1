
Il progetto si pone come obiettivo di realizzare un server web che 
gestisce un sito web statico formato da 3 pagine HTML. 
Il server con protocollo HTTP si fonda su un unico socket in ascolto 
su tutte le interfacce di rete alla porta 8080. il 
server è basato sui protocolli AF_INET e il tipo SOCK_STREAM per 
garantire una comunicazione affidabile di tipo TCP. Al momento del bind, 
viene attivata l’opzione SO_REUSEADDR, che istruisce il sistema 
operativo a rilasciare immediatamente la porta non appena il processo 
termina, evitando errori di tipo “Address already in use” in fase di 
restart. 

Quando viene chiamato 'listen(1)', il sistema operativo prepara il 
socket per accettare connessioni e crea una piccola coda in cui mettere 
le richieste in arrivo. Quando un client si collega, quella richiesta 
resta in attesa in coda finché non eseguiamo 'accept()'. A quel punto 
'accept()' rimuove la richiesta dalla coda e restituisce un nuovo 
socket: questo nuovo socket è usato esclusivamente per scambiare dati 
con quel singolo client, mentre il socket originale continua a rimanere 
in ascolto sulla stessa porta, pronto a ricevere altre connessioni.

Il server legge dal socket i primi dati della richiesta HTTP e individua 
la 'request‑line', da cui ricava il metodo e il percorso richiesto. Se 
il percorso è “/”, lo trasformiamo in “/trails.html”. Altrimenti 
togliamo eventuali “..” o slash iniziali per impedire che si navighi 
fuori dalla cartella “www”. Infine controlliamo con commonpath che il 
file si trovi davvero dentro “www”: se non è così, blocchiamo la 
richiesta.

Una volta risolta la posizione del file, il server calcola il 
content‑type tramite la libreria mimetypes, che associa l’estensione a 
un tipo MIME standard (.html, .jpeg, .css, ecc.). Prima di inviare il 
contenuto, si costruisce l’header HTTP includendo lo status code (200 o 
404), l’intestazione Content-Type con charset UTF‑8 e Content-Length in 
byte, seguiti da una doppia CRLF che separa gli header dal body. Il 
corpo viene trasmesso in modalità raw‑binary con sendall(), assicurando 
che l’intero buffer sia effettivamente recapitato al client.

Parallelamente, ogni evento significativo — dall’avvio del listener, 
all’accettazione di una connessione, al dettaglio della request‑line, 
fino all’esito della risposta e alla chiusura del socket — viene 
annotato sincronicamente su file di log con timestamp ISO‑style e 
livello di gravità. Questo approccio fornisce riepilogo completo delle 
interazioni, agevolando il debugging e il monitoraggio in produzione. 

Terminato la comunicazione con il client chiudiamo lo scambio di dati e rilasciamo l'indirizzo della socket così che altri socket possano utilizzarlo.

