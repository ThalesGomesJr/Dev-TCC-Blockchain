from flask import jsonify, render_template, request, redirect, url_for, flash, current_app
from App import app
from App.blockchain import Blockchain
from App.transaction import Transaction
from werkzeug.utils import secure_filename
from uuid import uuid4
import os, errno
import hashlib
import json 
import PyPDF2
import socket

#cria o endereço do node
node_address = str(uuid4())

#instancia a classe blockchain
blockchain = Blockchain(node_address)
#instancia a classe transaction
transaction = Transaction(node_address)

@app.route('/', methods=['GET','POST'])
def home():
    #Conecta os todos nos nós da rede
    #Utilizando client socket
    HOST = '127.0.0.1'
    #HOST = '192.168.0.12'
    PORT = 12000

    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((HOST, PORT))

    cliente.sendall(str.encode("node2"))

    resp = cliente.recv(1024)
    nodes = resp.decode().replace(']', '').replace('[', '')
    nodes = nodes.replace("'",'').replace(" ", '').split(",")

    nodes.remove('http://127.0.0.1:5002')
    
    for ip in nodes:
        blockchain.add_node(ip)
        transaction.add_node(ip)
    
    if nodes != []:
        #Atualiza o nó do blockchain
        blockchain.verify_chain()
        transaction.verify_transactions()

    return render_template('index.html', actindex = 'active')

#Realiza o Uploud dos arquivos anexados
@app.route('/uploud', methods=['POST'])
def uploud():
    #upload do arquivo
    file = request.files.get('file')
    
    pdf = PyPDF2.PdfFileReader(file)
    pdf_write = PyPDF2.PdfFileWriter()
    for page in range(pdf.numPages):
        pdf_write.addPage(pdf.getPage(page))
    #cifrando pdf se ele for privado
    if request.form.get('tipo_documento') == "private":
        pdf_write.encrypt("password")
        resultPdf = open(blockchain.directory+file.filename, 'wb')
        pdf_write.write(resultPdf)
        resultPdf.close()
            
    else:
        resultPdf = open(blockchain.directory+file.filename, 'wb')
        pdf_write.write(resultPdf)
        resultPdf.close()
       
    #Cria hash de assinatura do documento, garantindo a integridade da informação.
    doc_hash = hashlib.sha256(str(file.read()).encode()).hexdigest()
    
    #busca os dados para adicionar ao bloco
    process = request.form.get('process')
    sender = 'DECIV - UNIR'
    receiver = request.form.get('receiver')
    name = request.form.get('name')
    id = request.form.get('id')
    
    #distribui os arquivos para os outros nós
    transaction.file_propagation(file.filename, blockchain.directory)
    return redirect(url_for('add_transactions', doc_hash=doc_hash, process=process, 
                            sender=sender, receiver=receiver, name=name, id=id))

@app.route('/add_transactions/<doc_hash>/<process>/<sender>/<receiver>/<name>/<id>', methods=['GET','POST'])
def add_transactions(doc_hash, process, sender, receiver, name, id):
    transaction.verify_transactions()
    transaction.add_transaction(doc_hash, process, sender, receiver, name, id)
    if len(transaction.transactions) == 2:        
        return redirect(url_for('mine_block'))

    flash('Transação do documento realizada com sucesso!', 'primary')
    return redirect(url_for('home'))
        
#adiciona o processo ao blockchain, realizando o processo de mineração
@app.route('/mine_block', methods = ['GET','POST'])
def mine_block():
    blockchain.verify_chain()
    if blockchain.is_chain_valid(blockchain.chain):
        previous_block = blockchain.get_previous_block()
        previous_proof = previous_block['nonce']
        proof = blockchain.proof_of_work(previous_proof)
        previous_hash = previous_block['hash']
        transactions = transaction.transactions
        hash_block = blockchain.hashs(previous_block['index']+1, proof, previous_hash, node_address, transactions)
        blockchain.create_block(proof, hash_block ,previous_hash, node_address, transactions)
        transaction.transactions = []

        #Salvando a blockchain no disco em formato json
        response = {'Blockchain': blockchain.chain,
                    'length': len(blockchain.chain)}
        file = open(blockchain.directory+'blockchain.json','w')
        json.dump(response, file)
        file.close()
            
        transaction.clear_transactions()
        flash('Um novo bloco foi minerado!', 'primary')
        return redirect(url_for('home'))

    flash('Blockchain não está validado, os dados estão corrompidos!', 'danger')
    return redirect(url_for('home'))

#============||rotas utilizadas pelo sistema para as funcionalidades de propagação na rede||============
#recebe a requisição para distribuir o documento enviado para blockchain
@app.route('/file_propagation', methods=['GET', 'POST'])
def file_propagation():
    file = request.files.get('file')

    pdf = PyPDF2.PdfFileReader(file)
    pdf_write = PyPDF2.PdfFileWriter()
    #verifica se o pdf é criptografado(privado)
    if pdf.isEncrypted:
        pdf.decrypt("password")
        for page in range(pdf.numPages):
            pdf_write.addPage(pdf.getPage(page))
        pdf_write.encrypt("password")
        resultPdf = open(blockchain.directory+file.filename, 'wb')
        pdf_write.write(resultPdf)
        resultPdf.close()
    else:
        for page in range(pdf.numPages):
            pdf_write.addPage(pdf.getPage(page))
        resultPdf = open(blockchain.directory+file.filename, 'wb')
        pdf_write.write(resultPdf)
        resultPdf.close()
     
#recebe a requisição para atualizar a lista de transações
@app.route('/transaction_propagation', methods=['GET', 'POST'])
def transaction_propagation():
    transaction_received = request.get_json()
    transaction.transactions.append(transaction_received)

#recebe a requisição para atualizar a blockchain
@app.route('/block_propagation', methods=['GET', 'POST'])
def block_propagation():
    block = request.get_json()
    blockchain.chain.append(block)
    
    #Salvando a blockchain no disco em formato json
    response = {'Blockchain': blockchain.chain,
                'length': len(blockchain.chain)}
    file = open(blockchain.directory+'blockchain.json','w')
    json.dump(response, file)
    file.close()
    
#Recebe a requisição para limpar a lista de transações, quando um novo bloco for minerado.
@app.route('/clear_transactions', methods=['GET', 'POST'])
def clear_transactions():
    transaction.transactions = []

#=========================================================================================================

@app.route('/get_chain', methods = ['GET','POST'])
def get_chain():
    
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

@app.route('/get_transactions', methods = ['GET','POST'])
def get_transactions():
    
    response = {'transactions': transaction.transactions,
                'length': len(transaction.transactions)}
    return jsonify(response), 200


#executando e definido host e porta.
app.run(debug=True, host='0.0.0.0', port = 5002)