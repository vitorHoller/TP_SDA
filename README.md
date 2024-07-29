# TP_SDA

Primeiramente é necessário inicializar as variáveis no servidor OPC/UA. Para facilitar existe um arquivo chamado `config.py`, no qual você pode colocar os respectivos valores de `ns` e `i` de cada uma das variáveis do seu servidor. Por padrão, os valores são os contidos na imagem abaixo.

![Screenshot](images/Screenshot from 2024-07-28 21-23-11.png)

Além disso, é necessário instalar as dependências necessárias para este projeto. Eu recomendo iniciar um ambiente virtual. Se estiver rodando no Linux, execute os códigos abaixo:

```bash
virtualenv TP_SDA_VITOR
source TP_SDA_VITOR/bin/activate
```

Após isso, você deve conferir se está na mesma pasta em que baixou os arquivos em Python do Moodle. Aqui está o link do GitHub para facilitar o clone:
https://github.com/vitorHoller/TP_SDA


```bash
git clone git@github.com:vitorHoller/TP_SDA.git
cd TP_SDA
python3 -m pip install -r requirements.txt
```

Agora abra 5 terminais diferentes e confira se os terminais estão dentro da pasta clonada do git:
```bash
python3 populate.py
python3 process.py
python3 MES.py
python3 CLP.py
python3 server_tcp_ip.py
```



Após fazer isso, basta colocar diferentes temperaturas de referência e ver como o sistema atua.

