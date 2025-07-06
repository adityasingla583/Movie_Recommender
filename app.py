import streamlit as st
import pickle
import pandas as pd
import requests

# Load data
movies_df = pickle.load(open('movies.pkl', 'rb'))  # Ensure 'movie_id' column exists
similarity = pickle.load(open('similarity.pkl', 'rb'))

# Extract titles for selectbox
movie_titles = movies_df['title'].values

# Dummy poster if error occurs
DUMMY_POSTER = "https://upload.wikimedia.org/wikipedia/commons/6/65/No-Image-Placeholder.svg"

# Fetch poster from TMDb API
def poster_fetch(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=1f29badfa0769c4ca3c9f02a5804554a"
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers, timeout=20)

        response.raise_for_status()
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
        else:
            return DUMMY_POSTER
    except Exception as e:
        print(f"Poster fetch error: {e}")
        return DUMMY_POSTER

# Recommendation function
def recommend(movie):
    movie_index = movies_df[movies_df['title'] == movie].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:10]
    
    recommended_movies = []
    recommended_posters = []

    for i in movie_list:
        idx = i[0]
        try:
            movie_id = movies_df.iloc[idx]['movie_id']  # Must be TMDb ID
        except KeyError:
            movie_id = None
        title = movies_df.iloc[idx]['title']

        recommended_movies.append(title)
        poster_url = poster_fetch(movie_id) if movie_id else DUMMY_POSTER
        recommended_posters.append(poster_url)

    return recommended_movies, recommended_posters

# Streamlit App UI
st.title('🎬 Movie Recommender System')

selected_movie_name = st.selectbox(
    'Select a movie to get recommendations:',
    movie_titles
)

if st.button('Recommend'):
    names, posters = recommend(selected_movie_name)
    st.subheader("Top Recommended Movies:")

    # Layout: display in 3 columns
    cols = st.columns(3)
    for i in range(len(names)):
        with cols[i % 3]:
            html_code = f"""
                <div style="text-align: center;">
                    <img src="{posters[i]}" alt="{names[i]}" width="180" height="270" style="object-fit: cover; border-radius: 10px;"><br>
                    <p style="margin-top: 5px;">{names[i]}</p>
                </div>
            """
            st.markdown(html_code, unsafe_allow_html=True)

