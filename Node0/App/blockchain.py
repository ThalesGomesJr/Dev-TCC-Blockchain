from urllib.parse import urlparse
import datetime, os, errno, glob 
import hashlib
import json
import requests

class Blockchain:
    def __init__(self, node_address):
        self.chain = []
        self.nodes = set()

        #cria o diretorio para salvar os dados em disco
        self.directory = os.path.expanduser('~') + '/Documentos/TCC/Dev-Blockchain/Node0/archives/'
        try:
            os.makedirs(self.directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        #verifica se existe dados da blockchain salvos em disco para ser carregado,caso não tenha, cria o bloco genesis.
        if not self.load_blockchain():
            if self.chain == []:
                #Frase no hash do bloco genesis: "Eu aprendi muito mais com meus erros do que com meus acertos" - Thomas Edison.
                self.create_block(proof = 0, hash = '95ac5b008aaffb00537f7a3cdc11eeec65dc2aa7db83bfcea26901f4ad7537c3',
                                previous_hash = '0', node_address = node_address, transactions = [])
                
        

    #Um bloco novo sera criado a cada 5 transações 
    def create_block(self, proof, hash, previous_hash, node_address, transactions):
        network = self.nodes
        block = {'index': len(self.chain) + 1,
                'hash': hash,
                'node_address': node_address,
                'timestamp': str(datetime.datetime.now()),
                'nonce': proof,
                'previous_hash': previous_hash,
                'transactions': transactions
                }
        self.chain.append(block)
        #propaga o bloco criado para toda a rede
        for node in network:
            requests.post(f'http://{node}/block_propagation', json = block)

    def get_previous_block(self):
        return self.chain[-1]

    #calcula a prova de trabalho.
    def proof_of_work(self, previous_proof):
        new_proof = 0
        check_proof = False
       
        while check_proof is False:
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()            
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1

        return new_proof

    #calcula o hash
    def hashs(self, index, proof, previous_hash, node_address, transactions):
        block = str(index) + str(proof) + previous_hash + node_address + str(transactions)
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    #verifica se o blockchain é valido
    def is_chain_valid(self, chain):
        previous_block = chain[0]
        block_index = 1
        #percorre o blockchain para encontrar erros, caso encontre retorna False
        while block_index < len(chain):
            block = chain[block_index]
            if block['previous_hash'] != previous_block['hash']:
                return False
            previous_proof = previous_block['nonce']
            proof = block['nonce']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()  
            if hash_operation[:4] != '0000':
                return False
            previous_block = block
            block_index += 1
        #caso não encontre retorna True
        return True
       
    #adiciona um novo nó na rede
    def add_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
    
    #mecanismo de atualização de blocos na rede.
    def verify_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        #Realiza a verificação em todos os nós da rede
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        #verifica se foi encontrado uma chain maior, caso encontre retorna True
        if longest_chain:
            self.chain = longest_chain
            #salvando a blockchain em disco
            response = {'Blockchain': self.chain,
                        'length': len(self.chain)
                        }
            file = open(self.directory+'blockchain.json','w')
            json.dump(response, file)
            file.close()
            return True

        #caso não encontre retorna False
        response = {'Blockchain': self.chain,
                    'length': len(self.chain)
                    }
        file = open(self.directory+'blockchain.json','w')
        json.dump(response, file)
        file.close()
        return False  
    
    #Carrega a blockhain salva em disco
    def load_blockchain(self):
        try:
            file = open(self.directory+'blockchain.json','r')
            json_file = json.loads(file.read())
            blockchain = []
            
            for blocks in json_file.get('Blockchain'):
                blockchain.append(blocks)
            
            if self.is_chain_valid(blockchain):
                self.chain = blockchain          
                return True
            else:
                return False
        except:
            return False