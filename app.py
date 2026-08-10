import base64
import html
from pathlib import Path
import re
import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any

from movie_matcher.data_loader import load_dataset, clean_dataset
from movie_matcher.matching import resolve_title
from movie_matcher.recommender import recommend_by_genre, recommend_by_description
from movie_matcher.comparison import compare_recommendations

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Movie Matcher — Editorial Film Discovery",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS STYLING ---
css = """<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global Viewport & Background - NO PURE WHITE */
    html, body, .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: 'Inter', sans-serif;
        background-color: #F1EBDD !important;
        color: #292A35 !important;
    }
    
    /* Main Content Container Padding */
    .main .block-container {
        padding-top: 2rem !important;
        padding-bottom: 5rem !important;
        max-width: 1100px !important;
    }

    /* Sidebar Overrides */
    [data-testid="stSidebar"] {
        background-color: #E7DED0 !important;
        border-right: 1px solid #D3C7B6 !important;
        padding-top: 1rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {
        gap: 0.8rem !important;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Playfair Display', serif;
        color: #292A35;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    /* Horizontal Rules */
    hr {
        border: none;
        border-top: 1px solid #D3C7B6;
        margin: 2.5rem 0;
    }
    .thin-divider {
        border-top: 1px solid #D3C7B6;
        margin: 1.5rem 0;
    }
    .burgundy-divider {
        border-top: 2px solid #762B36;
        margin: 1.5rem 0;
    }

    /* Header Bar */
    .main-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 1rem;
        border-bottom: 1px solid #D3C7B6;
        margin-bottom: 2rem;
    }
    .header-logo {
        font-family: 'Playfair Display', serif;
        font-weight: 700;
        font-size: 1.3rem;
        letter-spacing: 1.5px;
        color: #762B36;
    }
    .header-nav {
        display: flex;
        gap: 2rem;
    }
    .header-nav a {
        text-decoration: none;
        color: #66615B;
        font-weight: 600;
        font-size: 0.85rem;
        letter-spacing: 1.5px;
        transition: color 0.2s ease;
    }
    .header-nav a:hover {
        color: #762B36;
    }

    /* Sidebar Branding & Navigation */
    .sidebar-brand {
        font-family: 'Playfair Display', serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: #762B36;
        letter-spacing: 1px;
        line-height: 1.2;
        margin-bottom: 0.2rem;
    }
    .sidebar-sub {
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        color: #66615B;
        text-transform: uppercase;
        margin-bottom: 1.5rem;
    }
    
    .sidebar-section-title {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        color: #762B36;
        text-transform: uppercase;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
    }

    .sidebar-info-box {
        background: #F8F4EA;
        border: 1px solid #D3C7B6;
        padding: 0.8rem 1rem;
        font-size: 0.8rem;
        color: #66615B;
        line-height: 1.5;
        border-radius: 4px;
    }

    .sidebar-info-box li {
        margin-bottom: 0.3rem;
    }

    /* Sidebar Radio Styling */
    [data-testid="stSidebar"] .stRadio > div {
        display: flex;
        flex-direction: column;
        gap: 0.4rem;
        background: transparent;
        border: none;
        padding: 0;
        margin: 0;
    }
    [data-testid="stSidebar"] .stRadio label {
        background: #F8F4EA !important;
        border: 1px solid #D3C7B6 !important;
        padding: 0.6rem 1rem !important;
        border-radius: 4px !important;
        color: #292A35 !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: #E7DED0 !important;
        border-color: #762B36 !important;
    }

    /* Hero Section */
    .hero-eyebrow {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 2.5px;
        color: #762B36;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }
    .hero-headline {
        font-family: 'Playfair Display', serif;
        font-size: 3.6rem;
        line-height: 1.1;
        color: #292A35;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    .hero-headline span {
        color: #762B36;
        font-style: italic;
    }
    .hero-support {
        font-size: 1.15rem;
        color: #66615B;
        font-weight: 300;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    .hero-deco-line {
        width: 60px;
        height: 2px;
        background-color: #B58A45;
        margin-bottom: 1.5rem;
    }

    /* Decorative Poster Stack Visual (Right Hero Column) */
    .poster-stack {
        position: relative;
        height: 240px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .stack-card {
        position: absolute;
        width: 140px;
        height: 200px;
        border-radius: 6px;
        border: 1px solid #D3C7B6;
        box-shadow: 0 8px 24px rgba(41,42,53,0.08);
        padding: 1rem;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .stack-card-1 {
        background: #762B36;
        color: #F8F4EA;
        transform: rotate(-8deg) translateX(-30px);
        z-index: 1;
    }
    .stack-card-2 {
        background: #F8F4EA;
        color: #292A35;
        transform: rotate(4deg) translateX(20px);
        z-index: 2;
    }
    .stack-card-3 {
        background: #5D202A;
        color: #F8F4EA;
        transform: rotate(-2deg);
        z-index: 3;
    }

    /* Search Component Container */
    .search-card {
        background: #F8F4EA;
        border: 1px solid #D3C7B6;
        padding: 2.2rem;
        border-radius: 6px;
        box-shadow: 0 4px 16px rgba(41,42,53,0.03);
        margin-bottom: 2.5rem;
    }
    .search-card-header {
        font-family: 'Playfair Display', serif;
        font-size: 1.4rem;
        font-weight: 700;
        color: #292A35;
        letter-spacing: 1px;
        margin-bottom: 0.3rem;
    }
    .search-card-sub {
        font-size: 0.9rem;
        color: #66615B;
        margin-bottom: 1.5rem;
    }
    .search-label-custom {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        color: #762B36;
        text-transform: uppercase;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }

    /* Input Customization */
    .stTextInput > div > div > input {
        border: 1px solid #D3C7B6 !important;
        background-color: #F1EBDD !important;
        border-radius: 4px !important;
        padding: 0.9rem 1.2rem !important;
        font-size: 1.1rem !important;
        color: #292A35 !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #762B36 !important;
        box-shadow: 0 0 0 1px #762B36 !important;
    }

    /* Segmented Controls (Radio under search) */
    .main .stRadio > div {
        background-color: #E7DED0;
        padding: 4px;
        border-radius: 6px;
        display: inline-flex;
        border: 1px solid #D3C7B6;
        margin-bottom: 1.2rem;
    }
    .main .stRadio label {
        background: transparent;
        padding: 0.5rem 1.2rem;
        border-radius: 4px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #292A35;
        cursor: pointer;
    }

    /* Buttons */
    .stButton > button {
        background-color: #762B36 !important;
        color: #F8F4EA !important;
        border: none !important;
        border-radius: 4px !important;
        padding: 0.75rem 2.2rem !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 1.5px !important;
        text-transform: uppercase !important;
        font-size: 0.85rem !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 4px 12px rgba(118,43,54,0.15) !important;
    }
    .stButton > button:hover {
        background-color: #5D202A !important;
        transform: translateY(-1px);
        box-shadow: 0 6px 16px rgba(118,43,54,0.25) !important;
    }

    .btn-secondary > div > div > .stButton > button {
        background-color: transparent !important;
        color: #762B36 !important;
        border: 1px solid #762B36 !important;
        box-shadow: none !important;
    }
    .btn-secondary > div > div > .stButton > button:hover {
        background-color: #E7DED0 !important;
    }

    /* Reference Film Card */
    .ref-film-card {
        background: #F8F4EA;
        border: 1px solid #B58A45;
        border-left: 5px solid #762B36;
        padding: 1.5rem 1.8rem;
        border-radius: 4px;
        margin-bottom: 2.5rem;
        box-shadow: 0 4px 16px rgba(41,42,53,0.03);
    }
    .ref-film-label {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 2px;
        color: #762B36;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }
    .ref-film-title {
        font-family: 'Playfair Display', serif;
        font-size: 2rem;
        font-weight: 700;
        color: #292A35;
        margin-bottom: 0.3rem;
    }
    .ref-film-genre {
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 1px;
        color: #B58A45;
        text-transform: uppercase;
    }

    /* Movie Result Cards */
    .movie-card {
        background: #F8F4EA;
        border: 1px solid #D3C7B6;
        border-radius: 6px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        display: flex;
        flex-direction: row;
        gap: 1.5rem;
        box-shadow: 0 4px 16px rgba(41,42,53,0.02);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .movie-card:hover {
        transform: translateY(-2px);
        border-color: #762B36;
    }

    /* Local Fallback Poster */
    .poster-box {
        width: 130px;
        min-width: 130px;
        height: 195px;
        background: linear-gradient(145deg, #5D202A, #762B36);
        border: 1px solid #D3C7B6;
        border-radius: 4px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 1rem 0.8rem;
        color: #F8F4EA;
        position: relative;
        overflow: hidden;
        box-shadow: inset 0 0 20px rgba(0,0,0,0.2);
    }
    .poster-box::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; bottom: 0;
        border: 1px solid rgba(181, 148, 69, 0.4);
        margin: 5px;
        pointer-events: none;
    }
    .poster-brand {
        font-size: 0.55rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        color: #B58A45;
        text-transform: uppercase;
    }
    .poster-initials {
        font-family: 'Playfair Display', serif;
        font-size: 2.8rem;
        font-weight: 700;
        color: #F8F4EA;
        line-height: 1;
        text-align: center;
        margin: 0.4rem 0;
    }
    .poster-title-small {
        font-family: 'Playfair Display', serif;
        font-size: 0.75rem;
        font-weight: 600;
        color: #F8F4EA;
        text-align: center;
        line-height: 1.2;
    }
    .poster-genre-tag {
        font-size: 0.55rem;
        font-weight: 600;
        letter-spacing: 1px;
        color: #B58A45;
        text-transform: uppercase;
        text-align: center;
    }

    /* Result Card Content */
    .card-content {
        flex-grow: 1;
        display: flex;
        flex-direction: column;
    }
    .card-rank-badge {
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 1.5px;
        color: #762B36;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }
    .card-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.7rem;
        font-weight: 700;
        color: #292A35;
        margin: 0 0 0.3rem 0;
        line-height: 1.2;
    }
    .card-meta {
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 1px;
        color: #B58A45;
        text-transform: uppercase;
        margin-bottom: 0.8rem;
    }
    .card-desc {
        font-size: 0.95rem;
        color: #66615B;
        line-height: 1.6;
        margin-bottom: auto;
    }
    .card-similarity {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 1px;
        color: #762B36;
        margin-top: 1rem;
        padding-top: 0.8rem;
        border-top: 1px solid #E7DED0;
    }
    .similarity-val {
        background: #E7DED0;
        padding: 0.2rem 0.6rem;
        border-radius: 3px;
        border: 1px solid #D3C7B6;
    }

    /* About Panel */
    .about-panel {
        background: #F8F4EA;
        border: 1px solid #D3C7B6;
        border-radius: 6px;
        padding: 2.2rem;
        margin-top: 2rem;
    }
    .about-num {
        font-family: 'Playfair Display', serif;
        font-size: 1.8rem;
        font-weight: 700;
        color: #762B36;
        margin-bottom: 0.2rem;
    }
    .about-title {
        font-weight: 700;
        font-size: 0.95rem;
        letter-spacing: 1px;
        color: #292A35;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    .about-desc {
        font-size: 0.9rem;
        color: #66615B;
        line-height: 1.5;
    }

    /* Message Cards */
    .message-card {
        background: #F8F4EA;
        border: 1px solid #D3C7B6;
        border-left: 5px solid #762B36;
        padding: 1.8rem;
        border-radius: 4px;
        margin: 1.5rem 0;
    }

    /* Footer */
    .footer-container {
        margin-top: 4rem;
        padding-top: 2.5rem;
        border-top: 1px solid #D3C7B6;
        color: #66615B;
        font-size: 0.85rem;
        line-height: 1.6;
    }
    .footer-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.2rem;
        font-weight: 700;
        color: #762B36;
        margin-bottom: 0.5rem;
    }
    .footer-bottom {
        margin-top: 2.5rem;
        padding-top: 1rem;
        border-top: 1px solid #E7DED0;
        text-align: center;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 1.5px;
        color: #66615B;
        text-transform: uppercase;
    }

    /* Section Decorative Label */
    .section-label {
        display: flex;
        align-items: center;
        gap: 1rem;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 2.5px;
        color: #762B36;
        text-transform: uppercase;
        margin: 2.5rem 0 1.5rem 0;
    }
    .section-label::before, .section-label::after {
        content: '';
        flex: 1;
        height: 1px;
        background-color: #D3C7B6;
    }
</style>"""
st.markdown(css, unsafe_allow_html=True)

# --- DATA CACHING ---
@st.cache_data
def get_data() -> pd.DataFrame:
    raw_df = load_dataset("data/imdb_movie_data.csv")
    df = clean_dataset(raw_df)
    return df

try:
    df = get_data()
except Exception as e:
    st.error(f"Could not load dataset: {e}")
    st.stop()

# --- SESSION STATE ---
if "search_query" not in st.session_state:
    st.session_state.search_query = ""
if "confirmed_title" not in st.session_state:
    st.session_state.confirmed_title = None
if "resolution" not in st.session_state:
    st.session_state.resolution = None
if "mode" not in st.session_state:
    st.session_state.mode = "GENRE"
if "active_nav" not in st.session_state:
    st.session_state.active_nav = "DISCOVER"

# --- HELPERS: SANITIZATION & POSTER RENDERER ---
def sanitize_text(text: Any) -> str:
    if not text or pd.isna(text):
        return ""
    # Strip any raw HTML markup tags
    clean_text = re.sub(r'<[^>]+>', '', str(text)).strip()
    # Escape HTML special characters for safe insertion into HTML templates
    return html.escape(clean_text)

def format_description(desc_raw: Any, max_len: int = 170) -> str:
    if not desc_raw or pd.isna(desc_raw):
        return ""
    # Strip HTML tags first
    clean_text = re.sub(r'<[^>]+>', '', str(desc_raw)).strip()
    # Truncate clean plain text
    if len(clean_text) > max_len:
        clean_text = clean_text[:max_len].rsplit(' ', 1)[0] + "..."
    # Escape special characters
    return html.escape(clean_text)

def get_initials(title: str) -> str:
    clean_title = sanitize_text(title)
    words = [w for w in clean_title.split() if w.lower() not in ['the', 'a', 'an', 'of', 'and', 'in', 'on', 'at', 'to']]
    if not words:
        words = clean_title.split()
    if not words: return "MM"
    if len(words) == 1: return words[0][:2].upper()
    return (words[0][:1] + words[1][:1]).upper()

# --- LOCAL POSTER MAPPING & LOADERS ---
def get_local_poster_b64(movie_title: str) -> Optional[str]:
    title_key = movie_title.strip().lower()
    title_key = title_key.replace(" ", "_")
    safe_name = "".join(c for c in title_key if c.isalnum() or c == '_')
    filename = safe_name + ".jpg"
    
    p = Path("assets/posters") / filename
    if not p.is_file():
        return None
    try:
        with open(p, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("utf-8")
        return f"data:image/jpeg;base64,{encoded}"
    except Exception:
        return None

def render_poster(title: str, genre: str, poster_url: Optional[str] = None) -> str:
    clean_title = sanitize_text(title)
    clean_genre = sanitize_text(genre)
    
    # 1. Check for local poster file first
    b64_img = get_local_poster_b64(title)
    if b64_img:
        return f'<img src="{b64_img}" class="poster-box" style="object-fit: cover;" alt="{clean_title}">'
    
    # 2. Check for poster_url field
    if poster_url and isinstance(poster_url, str) and poster_url.startswith("http"):
        safe_url = html.escape(poster_url)
        return f'<img src="{safe_url}" class="poster-box" style="object-fit: cover;" alt="{clean_title}">'
    
    # 3. Graceful fallback to typographic placeholder
    initials = get_initials(clean_title)
    short_title = clean_title if len(clean_title) <= 22 else clean_title[:19] + "..."
    primary_genre = clean_genre.split(',')[0].strip() if clean_genre else "FILM"
    
    return f"""<div class="poster-box">
<div class="poster-brand">MOVIE MATCHER</div>
<div>
<div class="poster-initials">{initials}</div>
<div class="poster-title-small">{short_title}</div>
</div>
<div class="poster-genre-tag">{primary_genre}</div>
</div>"""

def render_movie_card(rank: int, movie: dict, description: str = "", poster_url: Optional[str] = None):
    clean_title = sanitize_text(movie['title'])
    clean_genre = sanitize_text(movie['genre']).replace(',', ' · ')
    clean_desc = format_description(description) if description else ""
    poster_html = render_poster(movie['title'], movie['genre'], poster_url)
    
    html_out = f"""<div class="movie-card">
{poster_html}
<div class="card-content">
<div class="card-rank-badge">#{rank:02d} MATCH</div>
<h3 class="card-title">{clean_title}</h3>
<div class="card-meta">{clean_genre}</div>
<div class="card-desc">{clean_desc}</div>
<div class="card-similarity">
<span>SIMILARITY SCORE</span>
<span class="similarity-val">{movie['similarity']:.4f}</span>
</div>
</div>
</div>"""
    st.markdown(html_out, unsafe_allow_html=True)

# --- SIDEBAR IMPLEMENTATION ---
with st.sidebar:
    st.markdown("""<div class="sidebar-brand">MOVIE MATCHER</div>
<div class="sidebar-sub">CONTENT-BASED FILM DISCOVERY</div>""", unsafe_allow_html=True)
    
    nav_choice = st.radio(
        "Navigation",
        ["DISCOVER", "COMPARE", "ABOUT"],
        index=["DISCOVER", "COMPARE", "ABOUT"].index(st.session_state.active_nav),
        label_visibility="collapsed"
    )
    st.session_state.active_nav = nav_choice
    
    st.markdown("""<div class="sidebar-section-title">HOW IT WORKS</div>
<div class="sidebar-info-box">
<ul style="padding-left: 1.2rem; margin: 0;">
<li><b>Genre Similarity:</b> Matches overlapping category vectors via CountVectorizer.</li>
<li><b>Description Similarity:</b> Compares plot themes using TF-IDF.</li>
<li><b>Fuzzy Title Matching:</b> Resolves misspelled or incomplete titles gracefully.</li>
</ul>
</div>
<br>
<div style="font-size: 0.7rem; color: #66615B; letter-spacing: 1px; font-weight: 600;">
MOVIE MATCHER<br>Content-based recommendation
</div>""", unsafe_allow_html=True)

# --- MAIN CONTENT HEADER ---
st.markdown("""<div class="main-header">
<div class="header-logo">MOVIE MATCHER</div>
<div class="header-nav">
<a href="#discover">DISCOVER</a>
<a href="#compare">COMPARE</a>
<a href="#about">ABOUT</a>
</div>
</div>""", unsafe_allow_html=True)

# --- MAIN CONTENT AREA ---

# 1. HERO SECTION
st.markdown("<div id='discover'></div>", unsafe_allow_html=True)
col_hero_left, col_hero_right = st.columns([3, 2], gap="large")

with col_hero_left:
    st.markdown("""<div class="hero-eyebrow">MOVIE MATCHER</div>
<h1 class="hero-headline">Find your next<br><span>favorite movie.</span></h1>
<div class="hero-support">Discover films with similar genres, descriptions, and themes from our curated collection.</div>
<div class="hero-deco-line"></div>""", unsafe_allow_html=True)

with col_hero_right:
    # Abstract decorative stack of movie posters on the right of the hero
    st.markdown("""<div class="poster-stack">
<div class="stack-card stack-card-1">
<div style="font-size: 0.6rem; letter-spacing: 1px; font-weight: 700; color: #B58A45;">CLASSIC</div>
<div style="font-family: 'Playfair Display'; font-size: 1.2rem; font-weight: 700;">CINEMA</div>
<div style="font-size: 0.55rem; opacity: 0.8;">GENRE MATCH</div>
</div>
<div class="stack-card stack-card-2">
<div style="font-size: 0.6rem; letter-spacing: 1px; font-weight: 700; color: #762B36;">FEATURED</div>
<div style="font-family: 'Playfair Display'; font-size: 1.2rem; font-weight: 700;">ARCHIVE</div>
<div style="font-size: 0.55rem; color: #66615B;">TF-IDF THEMES</div>
</div>
<div class="stack-card stack-card-3">
<div style="font-size: 0.6rem; letter-spacing: 1px; font-weight: 700; color: #B58A45;">DISCOVER</div>
<div style="font-family: 'Playfair Display'; font-size: 1.2rem; font-weight: 700;">FILM MATCH</div>
<div style="font-size: 0.55rem; opacity: 0.8;">COSINE VECTOR</div>
</div>
</div>""", unsafe_allow_html=True)

# 2. SEARCH CARD COMPONENT
st.markdown("""<div class="search-card">
<div class="search-card-header">SEARCH THE COLLECTION</div>
<div class="search-card-sub">Enter a movie title and choose how you want to find similar films.</div>
</div>""", unsafe_allow_html=True)

query = st.text_input(
    "Movie Title Query",
    value=st.session_state.search_query,
    label_visibility="collapsed",
    placeholder="Enter a movie title (e.g., The Dark Knight, Interstellar)..."
)

st.markdown('<div class="search-label-custom">MATCH BY METHOD</div>', unsafe_allow_html=True)
mode = st.radio(
    "Match Method",
    ["GENRE", "DESCRIPTION", "COMPARE BOTH"],
    horizontal=True,
    label_visibility="collapsed",
    index=["GENRE", "DESCRIPTION", "COMPARE BOTH"].index(st.session_state.mode)
)
st.session_state.mode = mode

if st.button("FIND RECOMMENDATIONS →"):
    normalized_input = " ".join(query.split())
    if normalized_input:
        st.session_state.search_query = query
        st.session_state.confirmed_title = None
        st.session_state.resolution = resolve_title(df, normalized_input)
    else:
        st.warning("Please enter a movie title to search.")

# 3. MATCHING RESOLUTION LOGIC (STRICT RETENTION OF EXACT VS FUZZY CONTRACT)
res = st.session_state.resolution

if res:
    if res["status"] == "exact":
        st.session_state.confirmed_title = res["title"]
    elif res["status"] == "fuzzy":
        if not st.session_state.confirmed_title:
            sugg = res["suggestions"][0] if res["suggestions"] else None
            if sugg:
                st.markdown(f"""<div class="message-card">
<div style="font-size: 0.75rem; font-weight: 700; letter-spacing: 1.5px; color: #762B36; margin-bottom: 0.3rem;">TITLE RESOLUTION</div>
<h3 style="margin-top:0; font-family: 'Playfair Display', serif;">Did you mean "{sugg}"?</h3>
<p style="margin-bottom: 1rem;">We couldn't find an exact match for "{st.session_state.search_query}", but found this close match in our database.</p>
</div>""", unsafe_allow_html=True)
                
                col_sugg1, col_sugg2, _ = st.columns([1.5, 1.5, 3])
                with col_sugg1:
                    if st.button(f'Use "{sugg}"', key="use_sugg_btn"):
                        st.session_state.confirmed_title = sugg
                        st.rerun()
                with col_sugg2:
                    st.markdown("<div class='btn-secondary'>", unsafe_allow_html=True)
                    if st.button("Search again", key="search_again_btn"):
                        st.session_state.resolution = None
                        st.session_state.confirmed_title = None
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class="message-card">
<h3 style="margin-top:0;">No movie found for "{st.session_state.search_query}".</h3>
<p>Try searching for another title, such as:<br>
<b>The Dark Knight</b> · <b>Interstellar</b> · <b>Doctor Strange</b></p>
</div>""", unsafe_allow_html=True)
    elif res["status"] == "not_found":
        st.markdown(f"""<div class="message-card">
<h3 style="margin-top:0;">No movie found for "{st.session_state.search_query}".</h3>
<p>Try searching for another title, such as:<br><br>
<b>The Dark Knight</b><br>
<b>Interstellar</b><br>
<b>Doctor Strange</b></p>
</div>""", unsafe_allow_html=True)

# 4. REFERENCE FILM & RESULTS DISPLAY
if st.session_state.confirmed_title:
    matched_row = df[df['Title'] == st.session_state.confirmed_title].iloc[0]
    matched_title = sanitize_text(matched_row['Title'])
    matched_genre = sanitize_text(matched_row['Genre']).replace(',', ' · ')
    
    # Reference Film Banner
    st.markdown(f"""<div class="ref-film-card">
<div class="ref-film-label">REFERENCE FILM</div>
<div class="ref-film-title">{matched_title}</div>
<div class="ref-film-genre">{matched_genre}</div>
</div>""", unsafe_allow_html=True)
    
    st.markdown("<div id='compare'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-label'>YOUR MATCHES</div>", unsafe_allow_html=True)
    
    if mode == "GENRE":
        st.markdown("<h3 style='font-family: Inter, sans-serif; font-size: 1.1rem; letter-spacing: 1.5px; color: #762B36; font-weight: 700; margin-bottom: 1.5rem;'>GENRE MATCH RECOMMENDATIONS</h3>", unsafe_allow_html=True)
        recs = recommend_by_genre(df, matched_title)
        if recs:
            for i, r in enumerate(recs, 1):
                r_row = df[df['Title'] == r['title']].iloc[0]
                desc = str(r_row['Description'])[:170] + "..." if len(str(r_row['Description'])) > 170 else str(r_row['Description'])
                p_url = r_row['poster_url'] if 'poster_url' in r_row and pd.notna(r_row['poster_url']) else None
                render_movie_card(i, r, desc, p_url)

    elif mode == "DESCRIPTION":
        st.markdown("<h3 style='font-family: Inter, sans-serif; font-size: 1.1rem; letter-spacing: 1.5px; color: #762B36; font-weight: 700; margin-bottom: 1.5rem;'>DESCRIPTION MATCH RECOMMENDATIONS</h3>", unsafe_allow_html=True)
        recs = recommend_by_description(df, matched_title)
        if recs:
            for i, r in enumerate(recs, 1):
                r_row = df[df['Title'] == r['title']].iloc[0]
                desc = str(r_row['Description'])[:170] + "..." if len(str(r_row['Description'])) > 170 else str(r_row['Description'])
                p_url = r_row['poster_url'] if 'poster_url' in r_row and pd.notna(r_row['poster_url']) else None
                render_movie_card(i, r, desc, p_url)

    elif mode == "COMPARE BOTH":
        comp = compare_recommendations(df, matched_title)
        if comp:
            st.markdown("<h3 style='font-family: Inter, sans-serif; font-size: 1.1rem; letter-spacing: 1.5px; color: #762B36; font-weight: 700; margin-bottom: 0.5rem;'>COMPARE THE TWO APPROACHES</h3>", unsafe_allow_html=True)
            st.markdown("<p style='color: #66615B; font-size: 0.95rem; margin-bottom: 2rem;'>Genre similarity focuses on shared category labels, whereas description similarity compares language and themes present in plot descriptions.</p>", unsafe_allow_html=True)
            
            col_genre, col_desc = st.columns(2, gap="large")
            with col_genre:
                st.markdown("<div style='font-weight: 700; font-size: 0.9rem; letter-spacing: 1.5px; color: #292A35; border-bottom: 2px solid #762B36; padding-bottom: 0.5rem; margin-bottom: 1.5rem;'>GENRE SIMILARITY</div>", unsafe_allow_html=True)
                for i, r in enumerate(comp["genre_recommendations"], 1):
                    r_row = df[df['Title'] == r['title']].iloc[0]
                    desc = str(r_row['Description'])[:100] + "..." if len(str(r_row['Description'])) > 100 else str(r_row['Description'])
                    p_url = r_row['poster_url'] if 'poster_url' in r_row and pd.notna(r_row['poster_url']) else None
                    render_movie_card(i, r, desc, p_url)
            with col_desc:
                st.markdown("<div style='font-weight: 700; font-size: 0.9rem; letter-spacing: 1.5px; color: #292A35; border-bottom: 2px solid #B58A45; padding-bottom: 0.5rem; margin-bottom: 1.5rem;'>DESCRIPTION SIMILARITY</div>", unsafe_allow_html=True)
                for i, r in enumerate(comp["description_recommendations"], 1):
                    r_row = df[df['Title'] == r['title']].iloc[0]
                    desc = str(r_row['Description'])[:100] + "..." if len(str(r_row['Description'])) > 100 else str(r_row['Description'])
                    p_url = r_row['poster_url'] if 'poster_url' in r_row and pd.notna(r_row['poster_url']) else None
                    render_movie_card(i, r, desc, p_url)

# 5. ABOUT SECTION
st.markdown("<div id='about'></div>", unsafe_allow_html=True)
st.markdown("<div class='section-label'>ABOUT THE SYSTEM</div>", unsafe_allow_html=True)

st.markdown("""<div class="about-panel">
<h2 style="font-family: 'Playfair Display', serif; font-size: 1.8rem; margin-bottom: 1.5rem;">HOW MOVIE MATCHER WORKS</h2>
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 1.8rem;">
<div>
<div class="about-num">01</div>
<div class="about-title">GENRE SIMILARITY</div>
<div class="about-desc">Uses <b>CountVectorizer</b> with a custom comma-separated tokenizer to transform genre labels into document-term vectors, measuring exact overlapping category alignment.</div>
</div>
<div>
<div class="about-num">02</div>
<div class="about-title">DESCRIPTION SIMILARITY</div>
<div class="about-desc">Uses <b>TF-IDF Vectorizer</b> with English stop-word filtering to vectorize plot synopses and evaluate deeper thematic and narrative parallels across films.</div>
</div>
<div>
<div class="about-num">03</div>
<div class="about-title">FUZZY TITLE MATCHING</div>
<div class="about-desc">Leverages <b>difflib string matching</b> to detect near-miss movie queries and present confirmation prompts for misspelled inputs before running recommendations.</div>
</div>
</div>
</div>""", unsafe_allow_html=True)

# 6. FOOTER SECTION
st.markdown("""<div class="footer-container">
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 2rem;">
<div>
<div class="footer-title">MOVIE MATCHER</div>
<div>Content-based film discovery platform for exploring thematic and structural movie parallels.</div>
</div>
<div>
<div style="font-weight: 700; letter-spacing: 1px; color: #292A35; margin-bottom: 0.5rem;">METHOD</div>
<div>Genre Vectorization (CountVectorizer)<br>Description Vectorization (TF-IDF)<br>Cosine Similarity Ranking</div>
</div>
<div>
<div style="font-weight: 700; letter-spacing: 1px; color: #292A35; margin-bottom: 0.5rem;">NAVIGATION</div>
<div><a href="#discover" style="color: #66615B; text-decoration: none;">Discover Films</a><br>
<a href="#compare" style="color: #66615B; text-decoration: none;">Compare Models</a><br>
<a href="#about" style="color: #66615B; text-decoration: none;">About System</a></div>
</div>
</div>
<div class="footer-bottom">
MOVIE MATCHER · CONTENT-BASED RECOMMENDATION ENGINE
</div>
</div>""", unsafe_allow_html=True)
