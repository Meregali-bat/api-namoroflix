from flask import Flask, jsonify, request

app = Flask(__name__)

usuarios = [
    {
        'id': 1,
        'nome': 'Manuel Gomes',
        'idade': 23,
        'genero': 'Masculino',
        'sexualidade': 'Heterossexual',
        'bio': 'Sou um rapaz que gosta de jogar futebol e de sair com os amigos.'
    },
    {
        'id': 2,
        'nome': 'Maria Silva',
        'idade': 25,
        'genero': 'Feminino',
        'sexualidade': 'bissexual',
        'bio': 'Sou uma pessoa que gosta de dançar e de sair com os amigos.'
    },
    {
        'id': 3,
        'nome': 'João Santos',
        'idade': 27,
        'genero': 'Masculino',
        'sexualidade': 'Homossexual',
        'bio': 'Não sou uma pessoa.'
    },
    {
        'id': 4,
        'nome': 'Ana Sousa',
        'idade': 30,
        'genero': 'Feminino',
        'sexualidade': 'bissexual',
        'bio': 'Sou uma pessoa.'
    }
]

@app.route('/usuarios', methods=['GET'])
def obter_usuarios():
    return jsonify(usuarios)

@app.route('/usuario/<int:id>', methods=['GET'])
def obter_usuario_id(id):
    for usuario in usuarios:
        if usuario['id'] == id:
            return jsonify(usuario)

@app.route('/usuario/<int:id>', methods=['PUT'])
def editar_usuario(id):
    usuario_editado = request.get_json()
    for indice, usuario in enumerate(usuarios):
        if usuario.get('id') == id:
            usuarios[indice].update(usuario_editado)
            return jsonify(usuarios[indice])

@app.route('/usuarios', methods=['POST'])   
def adicionar_usuario():
    novo_usuario = request.get_json()
    usuarios.append(novo_usuario)
    return jsonify(usuarios)
    
@app.route('/usuario/<int:id>', methods=['DELETE'])    
def excluir_usuario(id):
    for indice, usuario in enumerate(usuarios):
        if usuario.get('id') == id:
            del usuarios[indice]
            return jsonify(usuarios)
    
app.run(port=5000, host="localhost", debug=True)