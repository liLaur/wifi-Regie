# WiFi Regie
Aplicatie pentru configurarea automata a datelor pentru routerele Tp-link 

___
## De ce ai nevoie?
1. Să te poți conecta la rețeaua de internet de pe laptop (dacă nu ai configurat pană acum urmeaza pasii de aici https://internet-campus.upb.ro/dot1x-windows10.html)
2. 2 cabluri de internet
3. Un switch
4. Un router

## Pași inițiali:
1. Conectează la priza de internet switch-ul
2. Conectează laptopul la switch
    - între timp bagă routerul in priză pentru a porni
    - dacă e prima dată când pornești routerul conectează-te prin cablu la el, intră in browser și cauta http://192.168.0.1, și fă pașii de acolo
    - apoi continuă cu 3.
3. Dacă apare "Unidentified Network" urmeaza pasii de aici https://internet-campus.upb.ro/dot1x-windows10.html
4. Rulezi `router_config.exe` (sau ii dai build from source) (https://github.com/liLaur/wifi-Regie/releases/download/beta/router_config.exe)
5. Urmează pașii de acolo.

## Următorii pași:
1. Rulează `router_config.exe` și urmează pașii de acolo

# 
În acest repository se găsește codul sursă și un executabil pentru Windows.
___
# Building/Obținerea programului
## Executabil gata făcut:
- descarcă `router_config.exe` (https://github.com/liLaur/wifi-Regie/releases/download/beta/router_config.exe)
- rulează-l (trebuie să dai "More info" și "Run anyway").

## Pentru build from source:
- clonează repository-ul
- rulează `pip install -r requirements.txt`
- apoi rulează `pyinstaller check_engine.spec` pentru a obține executabilul
- executabilul este localizat in folderul `dist`, restul folderelor pot fi ignorate.
