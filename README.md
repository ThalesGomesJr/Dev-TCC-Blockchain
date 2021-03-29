# Projeto TCC - Rede de testes de Blockchain para certificação de sistemas de gestão de processos e documentos eletrônicos.

Desenolvimento de uma rede Blockchain integrável a sistemas de gestão de processos e documentos eletrônicos, atráves de API REST.

## Começando

As instruções a seguir irão lhe proporcionar uma cópia deste projeto e de como rodar em sua máquina local para propósito de desenvolvimento e testes. 
### Pre-requisitos

Dependência necessária para se instalar a rede de testes.

- Python 3.7

### Instalação e execução

Clone o repositório.
```
> git clone git@github.com:ThalesGomesJr/Dev-TCC-Blockchain.git
```

Navegue para o diretório do projeto
```
> cd Dev-Blockchain/
```

Crie e ative o ambiente virtual
```
> virtualenv venv
> source venv/bin/activate
```

Instale as dependências do Projeto
```
> pip install -r requirements.txt
```

Navegue até a pasta do socket e execute o comando
```
> pyhton socket_connect.py
```


Navegue até a pasta do Node0 e execute o comando
```
> python routes.py
```

Navegue até a pasta do Node1 e execute o comando
```
> python routes.py
```

Navegue até a pasta do Node2 e execute o comando
```
> python routes.py
```

Navegue até a pasta do Node3 e execute o comando
```
> python routes.py
```

### Ao fim destes passos a rede de testes estará em pleno funcionamento.


## Desenvolvido com
* [Python](https://www.python.org/) - Linguagem utilizada
* [Flask](https://flask.palletsprojects.com/en/1.1.x/) - Framework web utilizado.

## Autor

* **Thales Junior de Souza Gomes** - [@ThalesGomesJr](https://github.com/ThalesGomesJr)

## Orientador

* Prof. Dr. Ewerton Rodrigues Andrade
