Jak uruchomić aplikacje:

DX-TORCHX-UI
1. Wejdz w katalog dx-torchx-ui
2. Zainstaluj biblioteki ```npm ci```
3. Zbuduj aplikacje aplikacje ```ng build --configuration production```

DX-TORCHX-AI-SERVER
1. Wejdz w katalog dx-torchx-ai-server
2. Zainstaluj biblioteki ```npm ci```
3. Do powstałego katalogu ```dist``` skopiuj katalog ```test_images```
4. W powstałym katalogu ```dist``` stworz katalog ```frontend```
5. Do katalogu ```frontend``` skopiuj zawartość katalogu ```dx-torchx-ui/dist/dx-torch-ui/browser```

DOCKER
1. Uruchom plik ```docker-compose.yaml```, aby uruchomić 3 procesy:
a. server-ml
b. web-server
c. baze danych

Aplikacje jest dostępna pod adresem: ```localhost:8080```



```
Web server
localhost:3000
exposed: 8080
```

```
ML engine
localhost:3001
exposed: 8081
```

Wersja Node JS:
v22.14.0