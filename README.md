# spv_dash_trading

Jednoduchá simulovaná burza umožňujúca nakupovať a predávať akcie, centrálne updatovať kurzy a sledovať vývoj potrfólií hráčov. Použitá na sústredení pre vedúcich 2021 v Novoti. 

Aplikácia je nakódená kompletne v Pythone s pomocou knižnice dash. Ako databáza slúži Redis. Aktuálne podporuje len Windows, ale nie je ťažké doplniť podporu aj pre posix systémy.

### Používanie aplikácie

Súbor `conda_env.yml` obsahuje zoznam potrebných Python balíčkov. Pre správne vykreslenie treba tiež nainštalovať dash-design-kit priložený v priečinku `dependencies`. Ako databáza sa využíva redis, na windowse treba rozbaliť priložený archív z `dependencies` do priečinku `redis`.

Hra samotná sa spúšťa z konzolovej aplikácie `run_game.py`. Najprv treba spustiť redis databázu príkazom `run -db` (otvorí sa nové okno). Ak ešte v db nie je žiadna hra,
príkazom `init` sa pripraví v db všetko potrebné podľa súboru `init_state.json`. Vygeneruje sa tiež história 20 transakcií za posledných 20 minút. Následne je možné
príkazmi `run -web` a `run -game` lokálne spustiť dash web server a state_updater (v minútových intervaloch generuje nové ceny a ukladá hodnoty portfólií jednotlivých hráčov.
Po prihlásení do aplikácie s účtom `veduci` ukazuje stránka /values v jednom grafe vývoj hodnoty portfólií všetkých hráčov.
