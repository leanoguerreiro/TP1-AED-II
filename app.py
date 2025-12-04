from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os

try:
    from sistema_filmes import Filme, NoAVL, ArvoreAVL, Grafo, SistemaRecomendacao

    print("✅ Classes importadas de sistema_filmes.py")
except ImportError:
    print("⚠️  AVISO: Não foi possível importar de sistema_filmes.py")
    print("   Cole as classes diretamente neste arquivo")
    sys.exit(1)

# Importa as classes do seu sistema
# (Assumindo que o script original está salvo como 'sistema_filmes.py')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Cole aqui todas as classes do seu script original
# (Filme, NoAVL, ArvoreAVL, Grafo, SistemaRecomendacao)

app = Flask(__name__)
CORS(app)  # Permite requisições do frontend


def encontrar_csv():
    """
    Tenta encontrar o arquivo data.csv em vários locais possíveis
    """
    # Obtém o diretório do script atual
    dir_atual = os.path.dirname(os.path.abspath(__file__))

    # Lista de caminhos possíveis (do mais provável ao menos)
    caminhos_possiveis = [
        os.path.join(dir_atual, 'db', 'data.csv'),  # backend/db/data.csv
        os.path.join(dir_atual, '..', 'db', 'data.csv'),  # db/data.csv (um nível acima)
        os.path.join(dir_atual, 'data.csv'),  # backend/data.csv
        os.path.join(dir_atual, '..', 'data.csv'),  # data.csv (raiz)
        './db/data.csv',  # relativo atual
        'db/data.csv',
        'data.csv'
    ]

    print("\n🔍 Procurando arquivo data.csv...")
    for caminho in caminhos_possiveis:
        caminho_normalizado = os.path.normpath(caminho)
        print(f"   Testando: {caminho_normalizado}")
        if os.path.exists(caminho_normalizado):
            print(f"   ✅ ENCONTRADO: {caminho_normalizado}\n")
            return caminho_normalizado

    # Se não encontrou, mostra erro detalhado
    print(f"\n❌ ERRO: Arquivo data.csv não encontrado!")
    print(f"📁 Diretório atual: {os.getcwd()}")
    print(f"📂 Arquivos disponíveis:")

    # Lista arquivos .csv disponíveis
    for root, dirs, files in os.walk('.', topdown=True):
        if root.count(os.sep) < 3:  # Limita profundidade
            for file in files:
                if file.endswith('.csv'):
                    print(f"   - {os.path.join(root, file)}")

    print("\n💡 SOLUÇÃO:")
    print("   1. Certifique-se de ter um arquivo CSV com seus filmes")
    print("   2. Coloque-o em: backend/db/data.csv")
    print("   3. Ou edite a variável ARQUIVO_DADOS no código")

    return None


# Inicializa o sistema
ARQUIVO_DADOS = encontrar_csv()
sistema = None


def inicializar_sistema(dados):
    """Carrega o sistema de recomendação na primeira requisição"""
    global sistema
    if sistema is None:
        print("🎬 Inicializando sistema de recomendação...")
        sistema = SistemaRecomendacao(dados)
        sistema.carregar_dados()
        print("✅ Sistema pronto!")
    return sistema


# ==================== ENDPOINTS DA API ====================

@app.route('/api/status', methods=['GET'])
def status():
    """Verifica se a API está funcionando"""
    try:
        s = inicializar_sistema()
        total = len(s.mapa_id_filme)
        return jsonify({
            'status': 'online',
            'total_filmes': total,
            'message': f'Sistema carregado com {total} filmes'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/filmes', methods=['GET'])
def listar_filmes():
    """Lista todos os filmes (paginado)"""
    try:
        s = inicializar_sistema()

        # Parâmetros de paginação
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))

        # Busca todos os filmes ordenados
        filmes = s.avl.travessia_em_ordem(s.avl_root)

        # Paginação
        start = (page - 1) * per_page
        end = start + per_page
        filmes_pagina = filmes[start:end]

        # Converte para formato JSON
        resultado = []
        for f in filmes_pagina:
            resultado.append({
                'id': f.id,
                'titulo': f.titulo,
                'ano': f.ano,
                'genero': f.genero,
                'nota': f.nota,
                'img': f'https://placehold.co/220x330/1e0730/a855f7?text={f.titulo[:15].replace(" ", "+")}'
            })

        return jsonify({
            'filmes': resultado,
            'total': len(filmes),
            'page': page,
            'per_page': per_page,
            'total_pages': (len(filmes) + per_page - 1) // per_page
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/filmes/buscar', methods=['GET'])
def buscar_filme():
    """Busca filmes por título (substring)"""
    try:
        s = inicializar_sistema()
        termo = request.args.get('q', '').strip()

        if not termo:
            return jsonify({'error': 'Parâmetro "q" é obrigatório'}), 400

        # Busca todos e filtra por substring
        todos = s.avl.travessia_em_ordem(s.avl_root)
        candidatos = [f for f in todos if termo.lower() in f.titulo.lower()]

        resultado = []
        for f in candidatos[:50]:  # Limita a 50 resultados
            resultado.append({
                'id': f.id,
                'titulo': f.titulo,
                'ano': f.ano,
                'genero': f.genero,
                'nota': f.nota,
                'img': f'https://placehold.co/220x330/1e0730/a855f7?text={f.titulo[:15].replace(" ", "+")}'
            })

        return jsonify({
            'filmes': resultado,
            'total': len(candidatos),
            'termo_busca': termo
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/filmes/<int:filme_id>', methods=['GET'])
def detalhes_filme(filme_id):
    """Retorna detalhes de um filme específico"""
    try:
        s = inicializar_sistema()
        filme = s.mapa_id_filme.get(filme_id)

        if not filme:
            return jsonify({'error': 'Filme não encontrado'}), 404

        return jsonify({
            'id': filme.id,
            'titulo': filme.titulo,
            'ano': filme.ano,
            'genero': filme.genero,
            'nota': filme.nota,
            'img': f'https://placehold.co/220x330/1e0730/a855f7?text={filme.titulo[:15].replace(" ", "+")}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recomendacoes', methods=['GET'])
def recomendacoes_geral():
    """
    Retorna recomendações gerais ou filtradas por gênero
    Query params:
    - generos: filtra por gênero específico
    - limit: quantidade de filmes (padrão: 20)
    """
    try:
        s = inicializar_sistema()

        genero_filtro = request.args.get('generos', '').strip()
        limit = int(request.args.get('limit', 20))

        filmes = s.avl.travessia_em_ordem(s.avl_root)

        # Filtra por gênero se especificado
        if genero_filtro:
            filmes = [f for f in filmes if genero_filtro.lower() in f.genero.lower()]

        # Ordena por nota (melhores primeiro)
        filmes.sort(key=lambda x: x.nota, reverse=True)
        filmes = filmes[:limit]

        resultado = []
        for f in filmes:
            resultado.append({
                'id': f.id,
                'titulo': f.titulo,
                'ano': f.ano,
                'genero': f.genero,
                'nota': f.nota,
                'img': f'https://placehold.co/220x330/1e0730/a855f7?text={f.titulo[:15].replace(" ", "+")}'
            })

        return jsonify(resultado)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/recomendacoes/<int:filme_id>', methods=['GET'])
def recomendar_similares(filme_id):
    """
    Recomenda filmes similares usando o algoritmo BFS do grafo
    (Funcionalidade principal do seu sistema!)
    """
    try:
        s = inicializar_sistema()

        # 1. Busca o filme base
        filme_base = s.mapa_id_filme.get(filme_id)
        if not filme_base:
            return jsonify({'error': 'Filme não encontrado'}), 404

        # 2. Executa o algoritmo de recomendação (BFS no grafo)
        ids_recomendados = s.grafo_similaridade.bfs(filme_base.id)

        # 3. Busca dados completos dos filmes recomendados
        recomendacoes = []
        for id_filme in ids_recomendados:
            filme = s.mapa_id_filme.get(id_filme)
            if filme and filme.nota >= filme_base.nota:  # Filtro de qualidade
                recomendacoes.append({
                    'id': filme.id,
                    'titulo': filme.titulo,
                    'ano': filme.ano,
                    'genero': filme.genero,
                    'nota': filme.nota,
                    'img': f'https://placehold.co/220x330/1e0730/a855f7?text={filme.titulo[:15].replace(" ", "+")}'
                })

        # 4. Ordena por nota
        recomendacoes.sort(key=lambda x: x['nota'], reverse=True)

        return jsonify({
            'filme_base': {
                'id': filme_base.id,
                'titulo': filme_base.titulo,
                'genero': filme_base.genero
            },
            'recomendacoes': recomendacoes[:20],  # Limita a 20
            'total': len(recomendacoes)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/generos', methods=['GET'])
def listar_generos():
    """Lista todos os gêneros únicos disponíveis"""
    try:
        s = inicializar_sistema()
        filmes = s.avl.travessia_em_ordem(s.avl_root)

        generos = set()
        for f in filmes:
            # Separa gêneros compostos (ex: "Action|Adventure")
            for g in f.genero.split('|'):
                g = g.strip()
                if g:
                    generos.add(g)

        return jsonify({
            'generos': sorted(list(generos)),
            'total': len(generos)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/estatisticas', methods=['GET'])
def estatisticas():
    """Retorna estatísticas do catálogo"""
    try:
        s = inicializar_sistema()
        filmes = s.avl.travessia_em_ordem(s.avl_root)

        if not filmes:
            return jsonify({'error': 'Nenhum filme carregado'}), 500

        notas = [f.nota for f in filmes]

        return jsonify({
            'total_filmes': len(filmes),
            'nota_media': sum(notas) / len(notas),
            'nota_maxima': max(notas),
            'nota_minima': min(notas),
            'total_conexoes_grafo': sum(len(vizinhos) for vizinhos in s.grafo_similaridade.adj.values()) // 2
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== EXECUÇÃO ====================

if __name__ == '__main__':
    print("🎬 PopScreen API - Sistema de Recomendação de Filmes")
    print("📊 Estruturas: AVL Tree + Graph (BFS)")
    print("🚀 Iniciando servidor Flask...")
    print("-" * 50)

    dados = ARQUIVO_DADOS

    # Pré-carrega o sistema
    inicializar_sistema(dados)

    # Inicia o servidor
    app.run(
        host='0.0.0.0',  # Permite acesso externo
        port=5000,
        debug=True
    )