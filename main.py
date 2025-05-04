from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, Dict, List
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI()

# Carregar e preparar dados
df = pd.read_csv("top50MusicFrom2010-2019.csv", encoding="ISO-8859-1")

df.rename(columns={
    'title': 'Title',
    'artist': 'Artist',
    'the genre of the track': 'Genre',
    'Beats.Per.Minute -The tempo of the song': 'BPM',
    'Energy- The energy of a song - the higher the value, the more energtic': 'Energy',
    'Danceability - The higher the value, the easier it is to dance to this song': 'Danceability',
    'Loudness/dB - The higher the value, the louder the song': 'Loudness/dB',
    'Liveness - The higher the value, the more likely the song is a live recording': 'Liveness',
    'Valence - The higher the value, the more positive mood for the song': 'Valence',
    'Length - The duration of the song': 'Length',
    'Acousticness - The higher the value the more acoustic the song is': 'Acousticness',
    'Speechiness - The higher the value the more spoken word the song contains': 'Speechiness',
    'Popularity- The higher the value the more popular the song is': 'Popularity'
}, inplace=True)

features = ['BPM', 'Energy', 'Danceability', 'Loudness/dB', 'Liveness',
            'Valence', 'Length', 'Acousticness', 'Speechiness', 'Popularity']

scaler = MinMaxScaler()
df[features] = scaler.fit_transform(df[features])

similarity_matrix = cosine_similarity(df[features])

# Simulação: o que cada usuário "curtiu"
user_likes = {
    "1": ["Memories", "Lose You To Love Me", "Someone You Loved", "Señorita", "How Do You Sleep?", "Trampoline (with ZAYN)"],
    "2": ["Someone You Loved", "Señorita", "How Do You Sleep?", "Trampoline (with ZAYN)", "South of the Border (feat. Camila Cabello & Cardi B)", "Truth Hurts"],
    "3": ["How Do You Sleep?", "Trampoline (with ZAYN)", "South of the Border (feat. Camila Cabello & Cardi B)", "Truth Hurts", "Good as Hell (feat. Ariana Grande) - Remix", "Happier"],
    "4": ["Lose You To Love Me", "Someone You Loved", "Señorita", "How Do You Sleep?", "Trampoline (with ZAYN)", "South of the Border (feat. Camila Cabello & Cardi B)"],
    "5": ["Señorita", "How Do You Sleep?", "Trampoline (with ZAYN)", "South of the Border (feat. Camila Cabello & Cardi B)", "Truth Hurts", "Good as Hell (feat. Ariana Grande) - Remix"],
    "6": ["Trampoline (with ZAYN)", "South of the Border (feat. Camila Cabello & Cardi B)", "Truth Hurts", "Good as Hell (feat. Ariana Grande) - Remix", "Happier", "Higher Love"],
    "7": ["Memories", "Lose You To Love Me", "Someone You Loved", "South of the Border (feat. Camila Cabello & Cardi B)", "Truth Hurts", "Good as Hell (feat. Ariana Grande) - Remix"],
    "8": ["Someone You Loved", "Señorita", "How Do You Sleep?", "Truth Hurts", "Good as Hell (feat. Ariana Grande) - Remix", "Happier"],
    "9": ["Lose You To Love Me", "Someone You Loved", "Señorita", "Trampoline (with ZAYN)", "South of the Border (feat. Camila Cabello & Cardi B)", "Truth Hurts"],
    "10": ["Memories", "Lose You To Love Me", "How Do You Sleep?", "Trampoline (with ZAYN)", "South of the Border (feat. Camila Cabello & Cardi B)", "Truth Hurts"]
}

# Modelos de requisição 

class GenreArtistRequest(BaseModel):
    genre: Optional[str] = None
    artist: Optional[str] = None
    limit: int = 5

class HybridRequest(BaseModel):
    song_title: str
    user_id: str
    content_weight: float = 0.7
    collab_weight: float = 0.3
    limit: int = 5

# Endpoints da aplicação

@app.get("/recommendations/content-based/{song_title}")
async def content_based_recommendations(song_title: str,limit: int = 5,bpm: Optional[float] = 1.0,energy: Optional[float] = 1.0,danceability: Optional[float] = 1.0,loudness: Optional[float] = 1.0,liveness: Optional[float] = 1.0,valence: Optional[float] = 1.0,length: Optional[float] = 1.0,acousticness: Optional[float] = 1.0,speechiness: Optional[float] = 1.0,popularity: Optional[float] = 1.0,
):
    """
    Gera recomendações de músicas com base nas características da música fornecida,
    utilizando similaridade de conteúdo com pesos ajustáveis para cada atributo.

    Parâmetros de URL:
    - song_title (str): Título da música de referência.
    - limit (int): Quantidade máxima de recomendações a retornar (padrão = 5).
    - bpm, energy, danceability, loudness, liveness, valence, length,
      acousticness, speechiness, popularity (float): Pesos opcionais (0 a 1) para
      ajustar a importância de cada característica na recomendação.

    Exemplo de requisição:
        GET /recommendations/content-based/Shape%20of%20You?limit=3&bpm=0.8&energy=1.0

    Exemplo de resposta:
    {
        "input_song": "Shape of You",
        "recommendations": [
            {
                "Title": "Photograph",
                "Artist": "Ed Sheeran",
                "Genre": "Pop",
                "year": 2015,
                "Popularity": 85
            },
            ...
        ]
    }
    """
    weights = {
        'BPM': bpm,
        'Energy': energy,
        'Danceability': danceability,
        'Loudness/dB': loudness,
        'Liveness': liveness,
        'Valence': valence,
        'Length': length,
        'Acousticness': acousticness,
        'Speechiness': speechiness,
        'Popularity': popularity
    }

    # Encontrar o índice da música
    matched = df[df['Title'].str.lower() == song_title.lower()]
    if matched.empty:
        raise HTTPException(status_code=404, detail="Música não encontrada.")
    index = matched.index[0]

    # Aplicar os pesos nas features
    custom_features = df[features].copy()
    for f in features:
        custom_features[f] *= weights.get(f, 1.0)

    # Calcular similaridade com pesos aplicados
    sim_matrix = cosine_similarity([custom_features.iloc[index]], custom_features).flatten()
    indices = np.argsort(sim_matrix)[::-1]
    similar_indices = [i for i in indices if i != index][:limit]

    recommendations = df.iloc[similar_indices][['Title', 'Artist', 'Genre', 'year', 'Popularity']].to_dict(orient="records")
    return {"input_song": song_title, "recommendations": recommendations}


@app.post("/recommendations/genre-artist")
async def genre_artist_recommendations(request: GenreArtistRequest):
    """
    Recomendação por gênero e/ou artista.
    Exemplo de requisição:
        POST /recommendations/genre-artist
        {
            "genre": "Pop",
            "artist": "Ed Sheeran",
            "limit": 5
        }
    """
    filtered = df.copy()
    if request.genre:
        filtered = filtered[filtered['Genre'].str.lower() == request.genre.lower()]
    if request.artist:
        filtered = filtered[filtered['Artist'].str.lower() == request.artist.lower()]

    if filtered.empty:
        raise HTTPException(status_code=404, detail="Nenhuma música encontrada com os critérios fornecidos.")

    result = filtered.sort_values(by="Popularity", ascending=False).head(request.limit)
    return result[['Title', 'Artist', 'Genre', 'year', 'Popularity']].to_dict(orient="records")


@app.get("/recommendations/collaborative/{user_id}")
async def collaborative_recommendations(user_id: str):
    """
    Recomendação colaborativa baseada em outros usuários.
    Exemplo de requisição:
        GET /recommendations/collaborative/1
    """
    if user_id not in user_likes:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    user_songs = set(user_likes[user_id])
    recommendations = {}

    for other_user, songs in user_likes.items():
        if other_user == user_id:
            continue
        for song in songs:
            if song not in user_songs:
                recommendations[song] = recommendations.get(song, 0) + 1

    if not recommendations:
        raise HTTPException(status_code=404, detail="Nenhuma recomendação encontrada.")

    sorted_songs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
    top_titles = [s for s, _ in sorted_songs[:5]]
    return df[df['Title'].isin(top_titles)][['Title', 'Artist', 'Genre', 'year', 'Popularity']].to_dict(orient="records")


@app.post("/recommendations/hybrid")
async def hybrid_recommendations(request: HybridRequest):
    """
    Recomendação híbrida combinando conteúdo e filtro colaborativo.
    Exemplo de requisição:
        POST /recommendations/hybrid
        {
            "song_title": "Memories",
            "user_id": "1",
            "content_weight": 0.6,
            "collab_weight": 0.4,
            "limit": 5
        }
    """
    if request.user_id not in user_likes:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    song_row = df[df['Title'].str.lower() == request.song_title.lower()]
    if song_row.empty:
        raise HTTPException(status_code=404, detail="Música não encontrada.")

    content_vec = song_row[features].values[0]
    liked_rows = df[df['Title'].isin(user_likes[request.user_id])]
    collab_vec = liked_rows[features].mean().values

    hybrid_vec = request.content_weight * content_vec + request.collab_weight * collab_vec

    similarities = cosine_similarity([hybrid_vec], df[features])[0]
    sorted_indices = similarities.argsort()[::-1]
    excluidas = set(user_likes[request.user_id] + [request.song_title])
    result_indices = [i for i in sorted_indices if df.iloc[i]['Title'] not in excluidas][:request.limit]

    return df.iloc[result_indices][['Title', 'Artist', 'Genre', 'year', 'Popularity']].to_dict(orient="records")


@app.get("/recommendations/popular")
async def popular_recommendations(year: Optional[int] = None, genre: Optional[str] = None, limit: int = 5):
    """
    Recomendação baseada em popularidade, filtrável por ano e gênero.
    Exemplo de requisição:
        GET /recommendations/popular?year=2019&genre=pop&limit=5
    """
    filtered = df.copy()
    if year is not None:
        filtered = filtered[filtered['year'] == year]
    if genre is not None:
        filtered = filtered[filtered['Genre'].str.contains(genre, case=False, na=False)]

    if filtered.empty:
        raise HTTPException(status_code=404, detail="Nenhuma música encontrada com os filtros fornecidos.")

    result = filtered.sort_values(by="Popularity", ascending=False).head(limit)
    return result[['Title', 'Artist', 'Genre', 'year', 'Popularity']].to_dict(orient="records")
