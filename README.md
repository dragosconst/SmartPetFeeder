# SmartPetFeeder

SmartPetFeeder este o aplicație ```Flask``` ce simulează un device IoT care eliberează porții de mâncare pentru un animal de companie la ore prestabilite. Aplicația include și codul pentru telecomanda smart reprezentată de o interfață grafică. 
Aplicația dezvoltată acționează drept creierul dispozitivului, gestionând input-urile senzorilor simulați, comenzile emise de utilizator prin telecomandă și acționând mecanismele: dispenser, difuzor, încălzitor etc.


## Biblioteci utilizate
```click==8.0.3
dearpygui==1.3.0
eventlet==0.33.0
Flask==2.0.2
Flask_MQTT==1.1.1
Flask_SocketIO==5.1.1
requests==2.26.0
```

## Instalare
Este necesară instalarea ```python3``` și ```pip3``` pentru a rula programul.
1. Se clonează repo-ul proiectului executând următoarea comandă într-un terminal de lucru:  
```git clone https://github.com/dragosconst/SmartPetFeeder/```
2. Se instalează bibliotecile necesare rulând comanda:  
```pip install -r requirements.txt```
3. Se intalează broker-ul <a href="https://mosquitto.org/"> Mosquitto </a> necesar pentru operațiunile MQTT.

## Utilizare
Pentru rularea server-ului aplicației se rulează într-un terminal:  
    ```python ./app.py```  
La pornire utilizatorul are posibilitatea de a executa o simulare a senzorilor device-ului:
![image](https://user-images.githubusercontent.com/54775881/152224902-d78266f4-a19b-4498-af3a-f1491cc12625.png)


Pentru lansarea telecomenzii smart se execută în terminal:  
    ```python ./remote.py```
    
![image](https://user-images.githubusercontent.com/54775881/152223926-9f2e415d-18f7-44c9-9e77-01872a0c3647.png)

    

