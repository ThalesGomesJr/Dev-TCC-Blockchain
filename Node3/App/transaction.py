from urllib.parse import urlparse
import datetime 
import requests


class Transaction:
    def __init__(self, node_address):
        self.transactions = []
        self.nodes = set()
        self.node_address = node_address
    
    #adiciona uma nova transação
    def add_transaction(self, document, process, sender, receiver, name, id):
        network = self.nodes
        transaction = {'index': len(self.transactions) + 1,
                        'document': document,
                        'process': process,
                        'sender': sender,
                        'receiver': receiver, 
                        'node_address': self.node_address,
                        'name': name,
                        'id': id,
                        'timestamp': str(datetime.datetime.now())
                        }
        self.transactions.append(transaction)
        #propaga o bloco criado para toda a rede
        for node in network:
            requests.post(f'http://{node}/transaction_propagation', json = transaction)
    
    #adiciona um novo nó na rede
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    #mecanismo de atualização de transações na rede.
    def verify_transactions(self):
        network = self.nodes
        longest_transactions = None
        max_length = len(self.transactions)
        #Realiza a verificação em todos os nós da rede
        for node in network:
            response = requests.get(f'http://{node}/get_transactions')
            if response.status_code == 200:
                length = response.json()['length']
                transactions = response.json()['transactions']
                if length > max_length:
                    max_length = length
                    longest_transactions = transactions
        #verifica se foi encontrado uma lista de transações maior, caso encontre retorna True
        if longest_transactions:
            self.transactions = longest_transactions
            return True
        #caso não encontre retorna False
        return False

    #limpa a lista de transações na rede quando um novo bloco for minerado
    def clear_transactions(self):
        network = self.nodes
        for node in network:
            requests.post(f'http://{node}/clear_transactions')

    #distribui os arquivos para os outros nós
    def file_propagation(self, filename, directory):
        network = self.nodes
        for node in network:
            file = {'file': open(directory + filename, 'rb')}
            requests.post(f'http://{node}/file_propagation', files = file)
