# 🎧 Sistema de Recomendação Musical com FastAPI

Este projeto é uma API desenvolvida com FastAPI que fornece recomendações de músicas utilizando diferentes estratégias, como:

- 🔍 Recomendação baseada em conteúdo
- 🎯 Recomendação por gênero/artista
- 👥 Recomendação colaborativa
- ⚖️ Recomendação híbrida
- 📈 Recomendação por popularidade/ano

## 🚀 Como executar o projeto

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/endpoints_sistema_recomendacao.git
cd endpoints_sistema_recomendacao
```

### 2. Crie um ambiente virtual
```bash
python -m venv venv
```

### 3. Ative o ambiente virtual
- No Windows:
```bash
venv\Scripts\activate
```
- No Linux/Mac:
```bash
source venv/bin/activate
```

### 4. Instale as dependências
```bash
pip install -r requirements.txt
```

### 5. Execute o servidor
```bash
uvicorn main:app --reload
```

Acesse a documentação interativa em:
```
http://127.0.0.1:8000/docs
```

## 📄 Estrutura do Projeto

```
endpoints_sistema_recomendacao/
│
├── main.py                     # Código principal da API
├── requirements.txt            # Dependências do projeto
├── top50MusicFrom2010-2019.csv  # Dataset utilizado
├── .gitignore                  # Ignora venv e pycache
└── README.md                   # Este arquivo
```

## 📦 Endpoints Disponíveis

### 1. Recomendação Baseada em Conteúdo
`GET /recommendations/content-based/{song_title}`  
Parâmetros de query opcionais: `bpm`, `energy`, etc.

### 2. Recomendação por Gênero/Artista
`POST /recommendations/genre-artist`  
Corpo: `{ "genre": "Pop", "artist": "Ed Sheeran", "limit": 5 }`

### 3. Recomendação Colaborativa
`GET /recommendations/collaborative/{user_id}`

### 4. Recomendação Híbrida
`POST /recommendations/hybrid`  
Corpo: `{ "song_title": "Memories", "user_id": "1", "content_weight": 0.7, "collab_weight": 0.3, "limit": 5 }`

### 5. Recomendação por Popularidade/Ano
`GET /recommendations/popular?year=2019&genre=pop&limit=5`

## 🧪 Exemplo de Execução

```bash
curl -X GET "http://127.0.0.1:8000/recommendations/content-based/Memories?limit=3"
```

## 📚 Requisitos

Veja o arquivo `requirements.txt` para as dependências necessárias.

## 👨‍💻 Autor

Desenvolvido por Lucca Codeço. Projeto acadêmico de recomendação com IA.