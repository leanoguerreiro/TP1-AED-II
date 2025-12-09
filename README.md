# Sistema de Recomendação de Filmes

Este projeto implementa um sistema de recomendação de filmes utilizando estruturas de dados clássicas. A Árvore AVL é responsável por armazenar o catálogo de forma ordenada. O Grafo de Similaridade modela relações entre filmes com base em gênero e proximidade de nota. O algoritmo BFS percorre essas conexões e gera recomendações relevantes.  

Além da lógica do sistema, o projeto conta com uma interface web construída com Flask, HTML e CSS, permitindo navegação entre páginas, visualização do catálogo e acesso às recomendações.

O dataset utilizado é uma versão reduzida do The Movies Dataset, processada previamente em um notebook dedicado.


---

## 📂 Estrutura do Projeto

O repositório possui a seguinte organização:

```bash
.
├── processing/
│   └── data_processing.ipynb
│
├── static/
│   └── style.css
│
├── templates/
│   ├── catalogo.html
│   ├── começo.html
│   ├── home.html
│   ├── index.html
│   └── lista.html
│
├── app.py
├── sistema_filmes.py
└── .gitignore
```

- **processing/data_processing.ipynb**  
  Notebook responsável pelo pré-processamento, limpeza e padronização do The Movies Dataset.

- **static/style.css**  
  Arquivo de estilização da interface web.

- **templates/**  
  Conjunto de páginas HTML que formam a interface gráfica do sistema.
  - **catalogo.html**: Exibe o catálogo de filmes.  
  - **começo.html**: Tela introdutória.  
  - **home.html**: Página principal da aplicação.  
  - **index.html**: Página inicial.  
  - **lista.html**: Página para visualização da lista personalizada do usuário.  

- **app.py**  
  Aplicação Flask que conecta a interface ao backend lógico.

- **sistema_filmes.py**  
  Implementação da Árvore AVL, do Grafo de Similaridade e do algoritmo BFS.

- **.gitignore**  
  Arquivo de configuração que define itens ignorados no versionamento.

---

### ⚙ Funcionalidades Principais

- Organização automática do catálogo de filmes utilizando Árvore AVL.  
- Busca eficiente por títulos em tempo O(log n).  
- Construção de grafo temático baseado em gênero e proximidade de nota.  
- Recomendações com BFS priorizando relevância e coerência.  
- Interface web inspirada em plataformas de streaming.  
- Visualização de catálogo, detalhes e lista personalizada.  
- Pré-processamento do dataset para padronização e limpeza.

---

### 📌 Tecnologias Utilizadas

- Python  
- Flask  
- HTML5  
- CSS3  
- Estruturas de Dados (AVL, Grafo e BFS)  
- Jupyter Notebook

---

### 👥 Equipe de Desenvolvimento

- Aila K. S. Moreira  
- Gustavo de O. Pena  
- Karen V. R. Pereira  
- Leano G. Baba  
- Sabrina M. Bezerra  
- Taíza P. de O. Lima

