import csv
import sys
from collections import deque
import difflib


# --- DEFINIÇÃO DAS ESTRUTURAS DE DADOS ---

class Filme:
    """Classe para armazenar os dados de um filme."""

    def __init__(self, id, titulo, ano, genero, nota):
        self.id = int(id)
        self.titulo = str(titulo)
        self.ano = int(ano)
        self.genero = str(genero)
        self.nota = float(nota)

    def __str__(self):
        """Representação em string para fácil impressão."""
        return f'ID: {self.id:03d} | Título: "{self.titulo}" | Ano: {self.ano} | Gênero: {self.genero} | Nota: {self.nota:.1f}'


class NoAVL:
    """Nó da Árvore AVL."""

    def __init__(self, filme):
        self.filme = filme
        self.chave = filme.titulo.lower().strip()
        self.esquerda = None
        self.direita = None
        self.altura = 1


class ArvoreAVL:
    """
    Implementação da Árvore AVL (sem bibliotecas externas).
    Armazena o catálogo de filmes ordenado pelo TÍTULO.
    """

    def _get_altura(self, no):
        """Retorna a altura de um nó (0 se for None)."""
        if not no:
            return 0
        return no.altura

    def _get_balanco(self, no):
        """Calcula o fator de balanceamento de um nó."""
        if not no:
            return 0
        return self._get_altura(no.esquerda) - self._get_altura(no.direita)

    def _rotacao_direita(self, z):
        """Executa uma rotação simples à direita."""
        y = z.esquerda
        T3 = y.direita

        # Realiza a rotação
        y.direita = z
        z.esquerda = T3

        # Atualiza alturas
        z.altura = 1 + max(self._get_altura(z.esquerda), self._get_altura(z.direita))
        y.altura = 1 + max(self._get_altura(y.esquerda), self._get_altura(y.direita))

        return y

    def _rotacao_esquerda(self, y):
        """Executa uma rotação simples à esquerda."""
        x = y.direita
        T2 = x.esquerda

        # Realiza a rotação
        x.esquerda = y
        y.direita = T2

        # Atualiza alturas
        y.altura = 1 + max(self._get_altura(y.esquerda), self._get_altura(y.direita))
        x.altura = 1 + max(self._get_altura(x.esquerda), self._get_altura(x.direita))

        return x

    def inserir(self, root, filme):
        """Insere um nó na árvore e realiza o balanceamento."""
        # 1. Inserção normal da BST
        if not root:
            return NoAVL(filme)

        chave_nova = filme.titulo.lower().strip()

        # Comparações usando a chave nova vs a chave do nó
        if chave_nova < root.chave:
            root.esquerda = self.inserir(root.esquerda, filme)
        elif chave_nova > root.chave:
            root.direita = self.inserir(root.direita, filme)
        else:
            # Título duplicado! Ignora e retorna o nó atual.
            # Isso impede que o mesmo filme entre duas vezes.
            return root

        # 2. Atualiza a altura do nó ancestral
        root.altura = 1 + max(self._get_altura(root.esquerda), self._get_altura(root.direita))

        # 3. Obtém o fator de balanceamento
        balanco = self._get_balanco(root)

        # 4. Verifica os 4 casos de desbalanceamento

        # Caso Esquerda-Esquerda (LL)
        if balanco > 1 and self._get_balanco(root.esquerda) >= 0:
            return self._rotacao_direita(root)

        if balanco > 1 and self._get_balanco(root.esquerda) < 0:
            root.esquerda = self._rotacao_esquerda(root.esquerda)
            return self._rotacao_direita(root)

        if balanco < -1 and self._get_balanco(root.direita) <= 0:
            return self._rotacao_esquerda(root)

        if balanco < -1 and self._get_balanco(root.direita) > 0:
            root.direita = self._rotacao_direita(root.direita)
            return self._rotacao_esquerda(root)

        return root

    def _get_no_minimo(self, root):
        """Retorna o nó com a menor chave (o mais à esquerda)."""
        if root is None or root.esquerda is None:
            return root
        return self._get_no_minimo(root.esquerda)

    def remover(self, root, titulo):
        """Remove um nó da árvore e realiza o balanceamento."""
        if not root:
            return root, None

        titulo_lower = titulo.lower().strip()
        filme_removido = None
        
        # 1. Remoção normal da BST
        if titulo_lower < root.chave:
            root.esquerda, filme_removido = self.remover(root.esquerda, titulo)
        elif titulo_lower > root.chave:
            root.direita, filme_removido = self.remover(root.direita, titulo)
        else:
            # Nó encontrado
            filme_removido = root.filme  # Guarda o filme para retornar

            # Caso 1: Nó com 0 ou 1 filho
            if root.esquerda is None:
                temp = root.direita
                root = None
                return temp, filme_removido
            elif root.direita is None:
                temp = root.esquerda
                root = None
                return temp, filme_removido

            # Caso 2: Nó com 2 filhos
            temp = self._get_no_minimo(root.direita)
            root.filme = temp.filme
            root.chave = temp.chave
            # Remove o sucessor em-ordem
            root.direita, _ = self.remover(root.direita, temp.chave)

        # Se a árvore ficou vazia (só tinha 1 nó)
        if root is None:
            return root, filme_removido

        # 2. Atualiza altura
        root.altura = 1 + max(self._get_altura(root.esquerda), self._get_altura(root.direita))

        # 3. Obtém balanceamento
        balanco = self._get_balanco(root)

        # 4. Rebalanceia (4 casos)

        # Caso Esquerda-Esquerda (LL)
        if balanco > 1 and self._get_balanco(root.esquerda) >= 0:
            return self._rotacao_direita(root), filme_removido

        # Caso Direita-Direita (RR)
        if balanco < -1 and self._get_balanco(root.direita) <= 0:
            return self._rotacao_esquerda(root), filme_removido

        # Caso Esquerda-Direita (LR)
        if balanco > 1 and self._get_balanco(root.esquerda) < 0:
            root.esquerda = self._rotacao_esquerda(root.esquerda)
            return self._rotacao_direita(root), filme_removido

        # Caso Direita-Esquerda (RL)
        if balanco < -1 and self._get_balanco(root.direita) > 0:
            root.direita = self._rotacao_direita(root.direita)
            return self._rotacao_esquerda(root), filme_removido

        return root, filme_removido

    def buscar(self, root, titulo):
        """Busca um filme pelo título (chave). Busca é case-insensitive."""
        if not root:
            return None

        titulo_lower = titulo.lower().strip()
        if titulo_lower < root.chave:
            return self.buscar(root.esquerda, titulo)
        elif titulo_lower > root.chave:
            return self.buscar(root.direita, titulo)
        else:
            # Encontrou!
            return root.filme

    def travessia_em_ordem(self, root):
        """Retorna uma lista de filmes em ordem alfabética de título."""
        filmes = []
        if root:
            filmes.extend(self.travessia_em_ordem(root.esquerda))
            filmes.append(root.filme)
            filmes.extend(self.travessia_em_ordem(root.direita))
        return filmes


class Grafo:
    """
    Implementação de um Grafo não-direcionado (sem bibliotecas).
    Usa lista de adjacência (dicionário) para modelar similaridade.
    Os vértices são os IDs dos filmes.
    """

    def __init__(self):
        self.adj = {}  # self.adj[id_filme] = {id_filme_vizinho1, id_filme_vizinho2, ...}

    def adicionar_vertice(self, id_filme):
        """Adiciona um vértice (filme) ao grafo."""
        if id_filme not in self.adj:
            self.adj[id_filme] = set()

    def adicionar_aresta(self, id_filme1, id_filme2):
        """Adiciona uma aresta (relação) entre dois filmes."""
        if id_filme1 in self.adj and id_filme2 in self.adj:
            self.adj[id_filme1].add(id_filme2)
            self.adj[id_filme2].add(id_filme1)

    def remover_vertice(self, id_filme):
        """Remove um vértice e todas as arestas conectadas a ele."""
        if id_filme in self.adj:
            # Remove arestas que apontam para este vértice
            for vizinho in self.adj[id_filme]:
                if vizinho in self.adj:
                    self.adj[vizinho].discard(id_filme)
            # Remove o próprio vértice
            del self.adj[id_filme]

    def bfs(self, id_inicio):
        """
        Realiza a Busca em Largura (BFS) para encontrar todos
        os filmes no mesmo componente conexo (mesmo gênero).
        Retorna uma lista de IDs, excluindo o próprio id_inicio.
        """
        if id_inicio not in self.adj:
            return []

        visitados = set()
        fila = deque([id_inicio])
        visitados.add(id_inicio)

        recomendacoes = []  # Lista de IDs relacionados

        max_recomendacoes = 50

        while fila and len(recomendacoes) < max_recomendacoes:
            v_atual = fila.popleft()
            if v_atual != id_inicio:
                recomendacoes.append(v_atual)

            for vizinho in self.adj[v_atual]:
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    fila.append(vizinho)
        return recomendacoes


# --- CLASSE PRINCIPAL DO SISTEMA ---

class SistemaRecomendacao:
    """
    Classe que integra a AVL (catálogo) e o Grafo (similaridade)
    e gerencia a lógica da aplicação.
    """

    def __init__(self, arquivo_csv):
        self.avl_root = None  # Raiz da árvore de filmes (ordenada por TÍTULO)
        self.avl = ArvoreAVL()
        self.grafo_similaridade = Grafo()
        self.mapa_id_filme = {}  # Hash map para busca rápida por ID (O(1))
        self.arquivo_csv = arquivo_csv
        self.filmes_carregados = []  # Lista temporária para construir o grafo

    def carregar_dados(self):
        print(f"Lendo dados de '{self.arquivo_csv}'...")
        ids_vistos = set()  # CRUCIAL: Para não duplicar filmes

        try:
            with open(self.arquivo_csv, mode='r', encoding='utf-8') as f:
                leitor = csv.reader(f)
                header = next(leitor, None)  # Pula o cabeçalho: userId,movieId,rating,title,genre,vote_average

                # Mapeamento manual baseado no output do Polars
                # 0: userId, 1: movieId, 2: rating, 3: title, 4: genre, 5: vote_average, 7: year

                count = 0
                for linha in leitor:
                    try:
                        movie_id = int(linha[1])

                        # Se já carregamos esse filme, pula (pois é só outra avaliação do mesmo filme)
                        if movie_id in ids_vistos:
                            continue

                        ids_vistos.add(movie_id)

                        titulo = linha[3]
                        genero = linha[4]

                        # Tratamento da nota (vazio ou inválido vira 0.0)
                        try:
                            nota = float(linha[5])
                        except (ValueError, IndexError):
                            nota = 0.0

                        # Ano não temos mais, definimos padrão 0
                        ano = linha[7]

                        filme = Filme(movie_id, titulo, ano, genero, nota)

                        # Estruturas de Dados
                        self.avl_root = self.avl.inserir(self.avl_root, filme)
                        self.grafo_similaridade.adicionar_vertice(filme.id)
                        self.mapa_id_filme[filme.id] = filme
                        self.filmes_carregados.append(filme)

                        count += 1
                        if count % 5000 == 0:
                            print(f"{count} filmes únicos processados...")

                    except (IndexError, ValueError):
                        continue

            print("Construindo grafo de similaridade (pode demorar)...")
            self._construir_arestas_grafo()
            print(f"Sucesso: {len(self.filmes_carregados)} filmes únicos carregados.")

        except FileNotFoundError as e:
            print(f"ERRO: Arquivo '{self.arquivo_csv}' não encontrado. \nMOTIVO: {e}")
            sys.exit(1)

    def _construir_arestas_grafo(self):
        """
        Cria as arestas do grafo conectando filmes
        que pertencem ao mesmo gênero.
        """
        # Agrupa filmes por gênero
        generos_map = {}

        for filme in self.filmes_carregados:
            # Separa a string "Action|Adventure" em ["Action", "Adventure"]
            lista_generos = [g.strip() for g in filme.genero.split('|') if g.strip()]

            for g in lista_generos:
                if g not in generos_map:
                    generos_map[g] = []
                generos_map[g].append(filme)

        # Configurações de similaridade
        LIMITE_DIFERENCA_NOTA = 1.0
        JANELA_VIZINHOS = 10

        # 2. Processa cada grupo de gênero
        for genero, lista_filmes_genero in generos_map.items():

            lista_filmes_genero.sort(key=lambda x: x.nota)

            n = len(lista_filmes_genero)

            # Loop principal
            for i in range(n):
                filme_a = lista_filmes_genero[i]

                # Loop interno: olha apenas para frente, dentro da janela definida
                for j in range(i + 1, min(i + 1 + JANELA_VIZINHOS, n)):
                    filme_b = lista_filmes_genero[j]

                    # Verifica a diferença de nota
                    diferenca = abs(filme_a.nota - filme_b.nota)

                    if diferenca <= LIMITE_DIFERENCA_NOTA:
                        self.grafo_similaridade.adicionar_aresta(filme_a.id, filme_b.id)
                    else:
                        break

        self.filmes_carregados = []

    def salvar_dados(self):
        """Salva o catálogo (da AVL, em ordem) de volta no CSV."""
        arquivo_saida = "filmes_catalogo_processado.csv"
        print(f"Salvando dados em '{arquivo_saida}'...")
        filmes_ordenados = self.avl.travessia_em_ordem(self.avl_root)
        try:
            with open(arquivo_saida, mode='w', encoding='utf-8', newline='') as f:
                escritor = csv.writer(f)
                escritor.writerow(['id', 'title', 'year', 'genre', 'vote_average'])
                for filme in filmes_ordenados:
                    escritor.writerow([filme.id, filme.titulo, filme.ano, filme.genero, filme.nota])
            print("Dados salvos com sucesso.")
        except Exception as e:
            print(f"ERRO ao salvar dados: {e}")

    def _adicionar_filme(self):
        """Pede dados ao usuário e adiciona um novo filme."""
        try:
            id = int(input("ID: "))
            if id in self.mapa_id_filme:
                print("ERRO: ID já existe.")
                return
            titulo = input("Título: ")
            if self.avl.buscar(self.avl_root, titulo.lower().strip()):
                print("ERRO: Título já existe.")
                return
            ano = int(input("Ano: "))
            genero = input("Gênero: ")
            nota = float(input("Nota: "))

            filme = Filme(id, titulo, ano, genero, nota)

            # 1. Insere na AVL
            self.avl_root = self.avl.inserir(self.avl_root, filme)

            # 2. Insere no Grafo
            self.grafo_similaridade.adicionar_vertice(filme.id)

            # 3. Insere no Mapa de ID
            self.mapa_id_filme[filme.id] = filme

            # 4. Atualiza arestas do grafo para o novo filme
            for outro_id, outro_filme in self.mapa_id_filme.items():
                if outro_id != filme.id and outro_filme.genero == filme.genero:
                    self.grafo_similaridade.adicionar_aresta(filme.id, outro_id)

            print(f"\nFilme '{titulo}' adicionado com sucesso.")

        except ValueError:
            print("ERRO: Entrada inválida. ID e Ano devem ser números, Nota deve ser decimal.")

    def _remover_filme(self):
        """Remove um filme do sistema pelo título."""
        titulo = input("Título do filme a remover: ")

        # 1. Remove da AVL (e obtém o filme removido)
        nova_raiz, filme_removido = self.avl.remover(self.avl_root, titulo.lower().strip())

        if filme_removido is None:
            print(f"ERRO: Filme '{titulo}' não encontrado.")
            return

        self.avl_root = nova_raiz

        # 2. Remove do Grafo
        self.grafo_similaridade.remover_vertice(filme_removido.id)

        # 3. Remove do Mapa de ID
        if filme_removido.id in self.mapa_id_filme:
            del self.mapa_id_filme[filme_removido.id]

        print(f"Filme '{filme_removido.titulo}' removido com sucesso.")

    def _exibir_detalhes_filme(self, filme):
        """Método auxiliar para formatar a exibição de um filme."""
        if not filme:
            return

        print("\n" + "=" * 40)
        print(f"DETALHES DO FILME")
        print("=" * 40)
        print(f"ID:     {filme.id}")
        print(f"Título: {filme.titulo}")
        print(f"Ano:    {filme.ano}")
        print(f"Gênero: {filme.genero}")
        print(f"Nota:   {filme.nota:.1f}")  # Adicionei .1f para formatar decimal
        print("=" * 40)

    def _buscar_filme(self):
        """Busca detalhes de um filme usando a abordagem híbrida."""
        termo = input("Digite o nome (ou parte) do filme para buscar: ").strip()
        if not termo: return

        # Usa o seletor híbrido
        filme_selecionado = self._selecionar_filme_interativo(termo)

        self._exibir_detalhes_filme(filme_selecionado)


    def _listar_todos_filmes(self):
        """Lista todos os filmes em ordem alfabética."""
        filmes = self.avl.travessia_em_ordem(self.avl_root)
        print(f"\n--- Catálogo Completo ({len(filmes)} filmes) ---")
        if not filmes:
            print("Nenhum filme no catálogo.")
            return

        for filme in filmes[:20]:
            print(filme)
        if len(filmes) > 20: print("... e mais milhares de filmes.")

    def _recomendar_filmes(self):
        """
        Recomenda filmes (Desafio Extra):
        1. Busca filme na AVL pelo título (O(log n))
        2. Usa o ID para executar BFS no Grafo e achar similares (O(V+E))
        3. Usa o Mapa de ID para buscar os dados dos similares (O(1) cada)
        4. Classifica (rankeia) os resultados pela nota.
        """
        titulo = input("Recomendar filmes similares a (título e ano): ")


        # 1. Busca na AVL
        filme_base = self._selecionar_filme_interativo(titulo)

        print("\nBaseado neste filme:")
        self._exibir_detalhes_filme(filme_base)

        if not filme_base:
            return

        print(f"\nBuscando recomendações para: {filme_base.titulo} (Gênero: {filme_base.genero})")
        recomendacoes_unicas = {}
        generos_base = set(g.strip() for g in filme_base.genero.split('|') if g.strip())
        filmes = self.avl.travessia_em_ordem(self.avl_root)
        LIMIAR_SIMILARIDADE = 0.8

        for f in filmes:
            if f.id == filme_base.id: continue

            # --- NOVO: Validação de Gênero ---
            # Verifica se os filmes compartilham pelo menos 1 gênero
            generos_atual = set(g.strip() for g in f.genero.split('|') if g.strip())

            # .isdisjoint() retorna True se NÃO tem nada em comum.
            # Então 'not isdisjoint' significa que TEM algo em comum.
            tem_genero_em_comum = not generos_base.isdisjoint(generos_atual)

            if tem_genero_em_comum:
                # Só calcula similaridade de nome se o gênero bater
                ratio = difflib.SequenceMatcher(None, filme_base.titulo.lower(), f.titulo.lower()).ratio()

                # Verifica similaridade OU inclusão (ex: "Toy Story" in "Toy Story 3")
                if ratio >= LIMIAR_SIMILARIDADE or filme_base.titulo.lower() in f.titulo.lower():
                    recomendacoes_unicas[f.id] = (f, "[Franquia/Nome]")

        # 2. Executa BFS no Grafo
        ids_recomendados = self.grafo_similaridade.bfs(filme_base.id)

        if not ids_recomendados:
            print("Nenhum filme similar encontrado.")
            return

        # 3. Busca dados dos filmes recomendados no Mapa de ID
        for id_filme in ids_recomendados:
            filme = self.mapa_id_filme.get(id_filme)
            if filme:
                # Filtro de Qualidade: Só recomenda se nota for igual ou maior
                if filme.nota >= filme_base.nota:
                    # Se já existe (veio pelo nome), não sobrescreve, senão adiciona
                    if filme.id not in recomendacoes_unicas:
                        recomendacoes_unicas[filme.id] = (filme, "[Gênero/Estilo/Nota]")

        lista_final = list(recomendacoes_unicas.values())

        # 4. Classifica (rankeia) pela nota
        lista_final.sort(key=lambda item: (1 if item[1] == "[Franquia/Nome]" else 0, item[0].nota), reverse=True)
        print("\n--- Recomendações (por nota) ---")
        for i, (filme, motivo) in enumerate(lista_final):
            print(f"{i + 1}. {filme}, {motivo}")
        print("---------------------------------")

    def _selecionar_filme_interativo(self, termo_busca):
        """
        1. Usa a AVL para gerar a lista ordenada (O(n)).
        2. Filtra por substring (Abordagem de Lista).
        3. Se houver múltiplos resultados, pede para o usuário escolher um (Interativo).
        Retorna o objeto Filme escolhido ou None.
        """
        # 1. Pega todos os filmes da árvore (já vem ordenado por título)
        todos_filmes = self.avl.travessia_em_ordem(self.avl_root)

        # 2. Filtra quem tem o termo no título (Case Insensitive)
        candidatos = [f for f in todos_filmes if termo_busca.lower() in f.titulo.lower()]

        if not candidatos:
            print(f"Nenhum filme encontrado com o termo '{termo_busca}'.")
            return None

        # Cenário A: Só achou um filme (Ex: digitou o nome completo exato)
        if len(candidatos) == 1:
            return candidatos[0]

        # Cenário B: Achou vários (Ex: digitou "Star Wars") -> Menu de Escolha
        print(f"\nEncontramos {len(candidatos)} filmes com '{termo_busca}':")
        print("-" * 60)

        for i, filme in enumerate(candidatos):
            print(f"[{i + 1}] {filme.titulo} ({filme.ano})")

        while True:
            try:
                escolha = int(input(f"Digite o NÚMERO do filme desejado (1-{min(len(candidatos), len(candidatos) - 1)}): "))
                if 1 <= escolha <= min(len(candidatos), len(candidatos) - 1):
                    return candidatos[escolha - 1]
                else:
                    print("Número inválido.")
            except ValueError:
                print("Por favor, digite um número.")

    def executar(self):
        """Loop principal do menu interativo."""
        self.carregar_dados()

        while True:
            print("\n--- Sistema de Recomendação de Filmes (AVL + Grafo) ---")
            print("[1] Adicionar novo filme")
            print("[2] Remover filme (por título)")
            print("[3] Buscar detalhes de um filme (por título)")
            print("[4] Listar todos os filmes (em ordem alfabética)")
            print("[5] Recomendar filmes similares (Desafio Extra)")
            print("[6] Salvar dados e Sair")

            escolha = input("Escolha uma opção: ")

            if escolha == '1':
                self._adicionar_filme()
            elif escolha == '2':
                self._remover_filme()
            elif escolha == '3':
                self._buscar_filme()
            elif escolha == '4':
                self._listar_todos_filmes()
            elif escolha == '5':
                self._recomendar_filmes()
            elif escolha == '6':
                self.salvar_dados()
                print("Saindo do sistema. Até logo!")
                break
            else:
                print("Opção inválida. Tente novamente.")


# --- PONTO DE ENTRADA DO PROGRAMA ---

if __name__ == "__main__":
    ARQUIVO_DADOS = "./db/data.csv"
    sistema = SistemaRecomendacao(ARQUIVO_DADOS)
    sistema.executar()