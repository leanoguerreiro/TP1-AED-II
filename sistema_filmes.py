import csv
import sys
from collections import deque
import difflib

# imagens 
def create_poster_placeholder(title):
    safe = "".join(c if c.isalnum() or c == ' ' else '' for c in (title or "")).strip().replace(' ', '+')
    if not safe:
        safe = "PopScreen"
    return f"https://placehold.co/500x750/1e0730/a855f7?text={safe}"

# Mapa (inglês -> português). 
GENRE_MAP_PT = {
    "Action": "Ação",
    "Adventure": "Aventura",
    "Comedy": "Comédia",
    "Drama": "Drama",
    "Animation": "Animação",
    "Fantasy": "Fantasia",
    "Horror": "Terror",
    "Science Fiction": "Ficção Científica",
    "Foreign": "Estrangeiro",
    "Crime": "Crime",
    "Thriller": "Suspense",
    "Mystery": "Mistério",
    "Romance": "Romance",
    "Documentary": "Documentário",
    "Family": "Família",
    "Western": "Faroeste",
    "History": "História",
    "Music": "Música",
    "War": "Guerra"
}

# --- DEFINIÇÃO DAS ESTRUTURAS DE DADOS ---

class Filme:
    """Classe para armazenar os dados de um filme."""

    def __init__(self, id, titulo, ano, genero, nota, img=None):
        self.id = int(id)
        self.titulo = str(titulo)
        try:
            self.ano = int(str(ano)[:4])  # ano = primeiros 4 dígitos
        except:
            self.ano = 0
        # Normaliza e traduz gêneros caso estejam em inglês (aceita '|' como separador)
        if isinstance(genero, str):
            # separa por pipe ou vírgula
            parts = [g.strip() for g in genero.replace(',', '|').split('|') if g.strip()]
            parts_pt = []
            for p in parts:
                parts_pt.append(GENRE_MAP_PT.get(p, p))  # traduz se houver
            self.genero = "|".join(parts_pt)
        else:
            self.genero = str(genero)

        try:
            self.nota = float(nota)
        except:
            self.nota = 0.0

        # imagem (url). Se não fornecida, gera placeholder
        self.img = img or create_poster_placeholder(self.titulo)


class NoAVL:
    """Nó da Árvore AVL."""

    def __init__(self, filme):
        self.filme = filme
        self.chave = filme.titulo.lower().strip()
        self.esquerda = None
        self.direita = None
        self.altura = 1


class ArvoreAVL:
    """Implementação da Árvore AVL (Catálogo ordenado por TÍTULO)."""

    def _get_altura(self, no):
        if not no: return 0
        return no.altura

    def _get_balanco(self, no):
        if not no: return 0
        return self._get_altura(no.esquerda) - self._get_altura(no.direita)

    def _rotacao_direita(self, z):
        y = z.esquerda
        T3 = y.direita
        y.direita = z
        z.esquerda = T3
        z.altura = 1 + max(self._get_altura(z.esquerda), self._get_altura(z.direita))
        y.altura = 1 + max(self._get_altura(y.esquerda), self._get_altura(y.direita))
        return y

    def _rotacao_esquerda(self, y):
        x = y.direita
        T2 = x.esquerda
        x.esquerda = y
        y.direita = T2
        y.altura = 1 + max(self._get_altura(y.esquerda), self._get_altura(y.direita))
        x.altura = 1 + max(self._get_altura(x.esquerda), self._get_altura(x.direita))
        return x

    def inserir(self, root, filme):
        if not root:
            return NoAVL(filme)

        chave_nova = filme.titulo.lower().strip()

        if chave_nova < root.chave:
            root.esquerda = self.inserir(root.esquerda, filme)
        elif chave_nova > root.chave:
            root.direita = self.inserir(root.direita, filme)
        else:
            return root  # Duplicado

        root.altura = 1 + max(self._get_altura(root.esquerda), self._get_altura(root.direita))
        balanco = self._get_balanco(root)

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
        if root is None or root.esquerda is None:
            return root
        return self._get_no_minimo(root.esquerda)

    def remover(self, root, titulo):
        if not root:
            return root, None

        titulo_lower = titulo.lower().strip()
        filme_removido = None

        if titulo_lower < root.chave:
            root.esquerda, filme_removido = self.remover(root.esquerda, titulo)
        elif titulo_lower > root.chave:
            root.direita, filme_removido = self.remover(root.direita, titulo)
        else:
            filme_removido = root.filme
            if root.esquerda is None:
                temp = root.direita
                root = None
                return temp, filme_removido
            elif root.direita is None:
                temp = root.esquerda
                root = None
                return temp, filme_removido

            temp = self._get_no_minimo(root.direita)
            root.filme = temp.filme
            root.chave = temp.chave
            root.direita, _ = self.remover(root.direita, temp.chave)

        if root is None:
            return root, filme_removido

        root.altura = 1 + max(self._get_altura(root.esquerda), self._get_altura(root.direita))
        balanco = self._get_balanco(root)

        if balanco > 1 and self._get_balanco(root.esquerda) >= 0:
            return self._rotacao_direita(root), filme_removido
        if balanco < -1 and self._get_balanco(root.direita) <= 0:
            return self._rotacao_esquerda(root), filme_removido
        if balanco > 1 and self._get_balanco(root.esquerda) < 0:
            root.esquerda = self._rotacao_esquerda(root.esquerda)
            return self._rotacao_direita(root), filme_removido
        if balanco < -1 and self._get_balanco(root.direita) > 0:
            root.direita = self._rotacao_direita(root.direita)
            return self._rotacao_esquerda(root), filme_removido

        return root, filme_removido

    def buscar_exato(self, root, titulo):
        """Busca binária exata por título."""
        if not root:
            return None
        titulo_lower = titulo.lower().strip()
        if titulo_lower < root.chave:
            return self.buscar_exato(root.esquerda, titulo)
        elif titulo_lower > root.chave:
            return self.buscar_exato(root.direita, titulo)
        else:
            return root.filme

    def travessia_em_ordem(self, root):
        filmes = []
        if root:
            filmes.extend(self.travessia_em_ordem(root.esquerda))
            filmes.append(root.filme)
            filmes.extend(self.travessia_em_ordem(root.direita))
        return filmes


class Grafo:
    """Implementação de Grafo (Lista de Adjacência)."""

    def __init__(self):
        self.adj = {}

    def adicionar_vertice(self, id_filme):
        if id_filme not in self.adj:
            self.adj[id_filme] = set()

    def adicionar_aresta(self, id_filme1, id_filme2):
        if id_filme1 in self.adj and id_filme2 in self.adj:
            self.adj[id_filme1].add(id_filme2)
            self.adj[id_filme2].add(id_filme1)

    def remover_vertice(self, id_filme):
        if id_filme in self.adj:
            for vizinho in self.adj[id_filme]:
                if vizinho in self.adj:
                    self.adj[vizinho].discard(id_filme)
            del self.adj[id_filme]

    def bfs(self, id_inicio, limite=50):
        if id_inicio not in self.adj:
            return []
        visitados = set()
        fila = deque([id_inicio])
        visitados.add(id_inicio)
        recomendacoes = []

        while fila and len(recomendacoes) < limite:
            v_atual = fila.popleft()
            if v_atual != id_inicio:
                recomendacoes.append(v_atual)

            for vizinho in self.adj[v_atual]:
                if vizinho not in visitados:
                    visitados.add(vizinho)
                    fila.append(vizinho)
        return recomendacoes


# --- CLASSE PRINCIPAL (LÓGICA) ---

class SistemaRecomendacao:
    """
    Controlador lógico do sistema.
    Não possui prints nem inputs. Retorna dados e levanta exceções.
    """

    def __init__(self, arquivo_csv):
        self.avl_root = None
        self.avl = ArvoreAVL()
        self.grafo_similaridade = Grafo()
        self.mapa_id_filme = {}
        self.arquivo_csv = arquivo_csv
        self.filmes_carregados = []

    def carregar_dados(self):
        """Lê o CSV e constrói as estruturas. Lança exceção se falhar."""
        ids_vistos = set()

        with open(self.arquivo_csv, mode='r', encoding='utf-8') as f:
            leitor = csv.reader(f, delimiter=',', quotechar='"', escapechar='\\')
            next(leitor, None)  # Pula header
            linha_debug = next(leitor, None)
            print("Primeira linha processável:", linha_debug)

            for linha in leitor:
                try:
                    movie_id = int(linha[1])
                    if movie_id in ids_vistos: continue
                    ids_vistos.add(movie_id)

                    titulo = linha[3]
                    genero = linha[4] if len(linha) > 4 else ""
                    try:
                        nota = float(linha[5]) if len(linha) > 5 else 0.0
                    except:
                        nota = 0.0
                    ano = linha[6] if len(linha) > 6 else ""

                    # Se no seu CSV houver um campo de imagem, use-o; caso contrário, passe None
                    img_url = None
                    # Se houver uma coluna com poster_path no CSV, substitua img_url = linha[<index>]

                    filme = Filme(movie_id, titulo, ano, genero, nota, img=img_url)

                    # Popula estruturas
                    self.avl_root = self.avl.inserir(self.avl_root, filme)
                    self.grafo_similaridade.adicionar_vertice(filme.id)
                    self.mapa_id_filme[filme.id] = filme
                    self.filmes_carregados.append(filme)
                except (IndexError, ValueError):
                    continue

        # Constrói grafo após carregar tudo
        self._construir_arestas_grafo()

    def _construir_arestas_grafo(self):
        generos_map = {}
        for filme in self.filmes_carregados:
            lista_generos = [g.strip() for g in filme.genero.split('|') if g.strip()]
            for g in lista_generos:
                if g not in generos_map: generos_map[g] = []
                generos_map[g].append(filme)

        LIMITE_DIFERENCA_NOTA = 1.0
        JANELA_VIZINHOS = 10

        for lista_filmes in generos_map.values():
            lista_filmes.sort(key=lambda x: x.nota)
            n = len(lista_filmes)
            for i in range(n):
                filme_a = lista_filmes[i]
                for j in range(i + 1, min(i + 1 + JANELA_VIZINHOS, n)):
                    filme_b = lista_filmes[j]
                    if abs(filme_a.nota - filme_b.nota) <= LIMITE_DIFERENCA_NOTA:
                        self.grafo_similaridade.adicionar_aresta(filme_a.id, filme_b.id)
                    else:
                        break
        self.filmes_carregados = []  # Limpa memória auxiliar

    def salvar_dados(self, arquivo_saida="filmes_catalogo_processado.csv"):
        filmes_ordenados = self.avl.travessia_em_ordem(self.avl_root)
        with open(arquivo_saida, mode='w', encoding='utf-8', newline='') as f:
            escritor = csv.writer(f)
            escritor.writerow(['id', 'title', 'year', 'genre', 'vote_average'])
            for filme in filmes_ordenados:
                escritor.writerow([filme.id, filme.titulo, filme.ano, filme.genero, filme.nota])

    def adicionar_filme(self, id, titulo, ano, genero, nota):
        """Adiciona um filme. Lança ValueError se ID ou Título já existirem."""
        if id in self.mapa_id_filme:
            raise ValueError(f"ID {id} já existe.")

        if self.avl.buscar_exato(self.avl_root, titulo):
            raise ValueError(f"Título '{titulo}' já existe.")

        filme = Filme(id, titulo, ano, genero, nota)

        self.avl_root = self.avl.inserir(self.avl_root, filme)
        self.grafo_similaridade.adicionar_vertice(filme.id)
        self.mapa_id_filme[filme.id] = filme

        # Atualiza arestas do grafo para o novo filme
        for outro_id, outro_filme in self.mapa_id_filme.items():
            if outro_id != filme.id and outro_filme.genero == filme.genero:
                self.grafo_similaridade.adicionar_aresta(filme.id, outro_id)

        return filme

    def remover_filme(self, titulo):
        """Remove por título e retorna o objeto removido (ou None)."""
        nova_raiz, filme_removido = self.avl.remover(self.avl_root, titulo)

        if filme_removido:
            self.avl_root = nova_raiz
            self.grafo_similaridade.remover_vertice(filme_removido.id)
            if filme_removido.id in self.mapa_id_filme:
                del self.mapa_id_filme[filme_removido.id]

        return filme_removido

    def buscar_filmes(self, termo_busca):
        """Retorna lista de filmes que contêm o termo no título."""
        todos = self.avl.travessia_em_ordem(self.avl_root)
        return [f for f in todos if termo_busca.lower() in f.titulo.lower()]

    def listar_todos(self):
        """Retorna lista completa ordenada."""
        return self.avl.travessia_em_ordem(self.avl_root)

    def obter_filme_por_titulo_exato(self, titulo):
        """Atalho para busca exata na AVL."""
        return self.avl.buscar_exato(self.avl_root, titulo)

    def recomendar_similares(self, filme_base):
        """
        Gera recomendações baseadas no filme_base.
        Retorna lista de tuplas: (Filme, motivo_string).
        """
        if not filme_base: return []

        recomendacoes_unicas = {}
        generos_base = set(g.strip() for g in filme_base.genero.split('|') if g.strip())

        # 1. Varredura linear na AVL (O(n)) para similaridade de texto e gênero
        #    (Necessário pois o grafo só conecta por nota estrita)
        filmes = self.avl.travessia_em_ordem(self.avl_root)
        LIMIAR_SIMILARIDADE = 0.8

        for f in filmes:
            if f.id == filme_base.id: continue

            generos_atual = set(g.strip() for g in f.genero.split('|') if g.strip())
            tem_genero_comum = not generos_base.isdisjoint(generos_atual)

            if tem_genero_comum:
                ratio = difflib.SequenceMatcher(None, filme_base.titulo.lower(), f.titulo.lower()).ratio()
                if ratio >= LIMIAR_SIMILARIDADE or filme_base.titulo.lower() in f.titulo.lower():
                    recomendacoes_unicas[f.id] = (f, "Nome/Franquia")

        # 2. Busca em Largura (BFS) no Grafo para similaridade estrutural/nota
        ids_grafo = self.grafo_similaridade.bfs(filme_base.id)

        for id_filme in ids_grafo:
            filme = self.mapa_id_filme.get(id_filme)
            if filme and filme.nota >= filme_base.nota:
                if filme.id not in recomendacoes_unicas:
                    recomendacoes_unicas[filme.id] = (filme, "Gênero/Nota")

        # Ordenação final
        lista_final = list(recomendacoes_unicas.values())
        # Prioriza Nome/Franquia, depois a nota
        lista_final.sort(key=lambda item: (1 if item[1] == "Nome/Franquia" else 0, item[0].nota), reverse=True)

        return lista_final

# --- EXEMPLO DE USO ---
# Como a classe não imprime nada, você deve chamar os métodos e tratar o retorno.
# if __name__ == "__main__":
#     sis = SistemaRecomendacao("./db/data.csv")
#     sis.carregar_dados()
#     print(sis.buscar_filmes("Toy Story"))