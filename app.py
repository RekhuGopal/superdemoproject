import streamlit as st
import json
import os
from datetime import datetime

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TechBlog",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .blog-card {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        border-left: 4px solid #7c3aed;
        transition: transform 0.2s;
    }
    .blog-card:hover { transform: translateX(4px); }
    .blog-title { font-size: 1.3rem; font-weight: 700; color: #e2e8f0; }
    .blog-meta  { font-size: 0.82rem; color: #94a3b8; margin: 0.3rem 0 0.7rem; }
    .tag {
        display: inline-block;
        background: #7c3aed22;
        color: #a78bfa;
        border: 1px solid #7c3aed55;
        border-radius: 999px;
        padding: 2px 10px;
        font-size: 0.75rem;
        margin-right: 4px;
    }
    .blog-excerpt { color: #cbd5e1; font-size: 0.95rem; line-height: 1.6; }
    .full-post    { color: #e2e8f0; font-size: 1rem;   line-height: 1.8; }
    .hero {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d1b69 100%);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    .hero h1 { font-size: 2.8rem; color: #a78bfa; margin-bottom: 0.3rem; }
    .hero p  { color: #94a3b8; font-size: 1.1rem; }
    .section-header {
        font-size: 1.4rem; font-weight: 700;
        color: #a78bfa; border-bottom: 2px solid #7c3aed44;
        padding-bottom: 0.4rem; margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Data persistence ───────────────────────────────────────────────────────────
DATA_FILE = "posts.json"

SAMPLE_POSTS = [
    {
        "id": 1,
        "title": "Getting Started with Streamlit: Build Apps in Pure Python",
        "author": "Alex Chen",
        "date": "2024-05-15",
        "tags": ["Python", "Streamlit", "Web Dev"],
        "excerpt": "Streamlit turns data scripts into shareable web apps in minutes. No front-end experience needed.",
        "content": """Streamlit is an open-source Python library that makes it incredibly easy to create beautiful, interactive web applications for machine learning and data science projects.

**Why Streamlit?**
- Zero front-end knowledge required
- Hot-reload during development
- Rich widget library (sliders, charts, file uploaders)
- One-command deployment via Streamlit Cloud

**Installation**
```bash
pip install streamlit
streamlit hello   # see the demo
```

**Your first app**
```python
import streamlit as st
st.title("Hello, World!")
name = st.text_input("Your name")
if name:
    st.success(f"Welcome, {name}!")
```

Run with `streamlit run app.py` and you're live. The ecosystem around Streamlit has grown tremendously, with community components covering everything from AgGrid tables to Plotly 3-D charts.""",
    },
    {
        "id": 2,
        "title": "Docker for Developers: From Zero to Production",
        "author": "Priya Nair",
        "date": "2024-06-02",
        "tags": ["Docker", "DevOps", "Containers"],
        "excerpt": "Containers solve the classic 'it works on my machine' problem. Here's everything you need to know.",
        "content": """Docker packages your application and all its dependencies into a lightweight container, guaranteeing consistent behaviour across every environment.

**Core concepts**
- **Image** – read-only template (your app + OS layer)
- **Container** – a running instance of an image
- **Dockerfile** – recipe to build an image
- **Docker Compose** – orchestrate multi-container apps

**Minimal Python Dockerfile**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

**Build & run**
```bash
docker build -t myapp .
docker run -p 8080:8080 myapp
```

**Docker Compose example**
```yaml
version: "3.9"
services:
  web:
    build: .
    ports: ["8000:8000"]
  db:
    image: postgres:15
    environment:
      POSTGRES_PASSWORD: secret
```

Once you embrace containers, you'll never go back to "it works on my machine".""",
    },
    {
        "id": 3,
        "title": "LLMs Explained: How Large Language Models Actually Work",
        "author": "Sam Rivera",
        "date": "2024-06-20",
        "tags": ["AI", "LLM", "Machine Learning"],
        "excerpt": "Behind the magic of ChatGPT and Claude lies transformer architecture, attention, and massive compute.",
        "content": """Large Language Models (LLMs) are neural networks trained on vast corpora of text. They predict the next token given a context window — that simple objective, scaled up, produces surprisingly capable systems.

**Key ingredients**
1. **Transformer architecture** – self-attention lets every token attend to every other token
2. **Pre-training** – next-token prediction on trillions of tokens
3. **RLHF** – Reinforcement Learning from Human Feedback aligns outputs to human preferences
4. **Scale** – more parameters + more data = emergent capabilities

**Attention in one line**
```
Attention(Q, K, V) = softmax(QKᵀ / √d_k) · V
```
Queries, Keys and Values are learned projections of the input embeddings.

**Practical tips for prompting**
- Be specific; vague prompts yield vague answers
- Use chain-of-thought ("think step by step")
- Provide examples (few-shot)
- Set a persona in the system prompt

LLMs are tools. Understanding their internals helps you use them — and spot their failure modes — more effectively.""",
    },
]


def load_posts():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return SAMPLE_POSTS


def save_posts(posts):
    with open(DATA_FILE, "w") as f:
        json.dump(posts, f, indent=2)


def next_id(posts):
    return max((p["id"] for p in posts), default=0) + 1


# ── Session state ──────────────────────────────────────────────────────────────
if "posts" not in st.session_state:
    st.session_state.posts = load_posts()
if "view" not in st.session_state:
    st.session_state.view = "home"   # home | read | write
if "active_post" not in st.session_state:
    st.session_state.active_post = None

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💻 TechBlog")
    st.markdown("---")

    if st.button("🏠 Home", use_container_width=True):
        st.session_state.view = "home"
        st.session_state.active_post = None

    if st.button("✍️ Write a Post", use_container_width=True):
        st.session_state.view = "write"
        st.session_state.active_post = None

    st.markdown("---")
    st.markdown("### 🔍 Search")
    search = st.text_input("Search posts…", label_visibility="collapsed")

    st.markdown("### 🏷️ Filter by Tag")
    all_tags = sorted({tag for p in st.session_state.posts for tag in p["tags"]})
    selected_tag = st.selectbox("Tag", ["All"] + all_tags, label_visibility="collapsed")

    st.markdown("---")
    st.caption(f"📄 {len(st.session_state.posts)} posts published")

# ── Hero banner (home only) ────────────────────────────────────────────────────
if st.session_state.view == "home":
    st.markdown("""
    <div class="hero">
        <h1>💻 TechBlog</h1>
        <p>Deep-dives on Python · AI · DevOps · Cloud · Open Source</p>
    </div>
    """, unsafe_allow_html=True)

    # Filter posts
    posts = st.session_state.posts
    if search:
        q = search.lower()
        posts = [p for p in posts if q in p["title"].lower() or q in p["content"].lower()]
    if selected_tag != "All":
        posts = [p for p in posts if selected_tag in p["tags"]]

    if not posts:
        st.info("No posts match your search. Try a different query or tag.")
    else:
        st.markdown(f'<div class="section-header">📰 Latest Posts ({len(posts)})</div>', unsafe_allow_html=True)
        for post in reversed(posts):
            tags_html = " ".join(f'<span class="tag">{t}</span>' for t in post["tags"])
            st.markdown(f"""
            <div class="blog-card">
                <div class="blog-title">{post['title']}</div>
                <div class="blog-meta">✍️ {post['author']} &nbsp;·&nbsp; 📅 {post['date']}</div>
                <div style="margin-bottom:0.6rem">{tags_html}</div>
                <div class="blog-excerpt">{post['excerpt']}</div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Read more →", key=f"read_{post['id']}"):
                st.session_state.view = "read"
                st.session_state.active_post = post["id"]
                st.rerun()

# ── Read post ──────────────────────────────────────────────────────────────────
elif st.session_state.view == "read":
    post = next((p for p in st.session_state.posts if p["id"] == st.session_state.active_post), None)
    if post:
        tags_html = " ".join(f'<span class="tag">{t}</span>' for t in post["tags"])
        st.markdown(f"# {post['title']}")
        st.markdown(f'<div class="blog-meta">✍️ {post["author"]} &nbsp;·&nbsp; 📅 {post["date"]} &nbsp;·&nbsp; {tags_html}</div>', unsafe_allow_html=True)
        st.markdown("---")
        st.markdown(f'<div class="full-post">', unsafe_allow_html=True)
        st.markdown(post["content"])
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("---")
        if st.button("← Back to Home"):
            st.session_state.view = "home"
            st.session_state.active_post = None
            st.rerun()

# ── Write post ─────────────────────────────────────────────────────────────────
elif st.session_state.view == "write":
    st.markdown('<div class="section-header">✍️ Write a New Post</div>', unsafe_allow_html=True)

    with st.container():
        title   = st.text_input("Post Title *")
        author  = st.text_input("Author Name *")
        tags_in = st.text_input("Tags (comma-separated, e.g. Python, AI, DevOps)")
        excerpt = st.text_area("Short Excerpt *", height=80)
        content = st.text_area("Full Content (Markdown supported) *", height=300)

        col1, col2 = st.columns([1, 4])
        with col1:
            submit = st.button("🚀 Publish", use_container_width=True)
        with col2:
            cancel = st.button("✕ Cancel", use_container_width=True)

        if cancel:
            st.session_state.view = "home"
            st.rerun()

        if submit:
            if not all([title, author, excerpt, content]):
                st.error("Please fill in all required fields.")
            else:
                new_post = {
                    "id":      next_id(st.session_state.posts),
                    "title":   title,
                    "author":  author,
                    "date":    datetime.today().strftime("%Y-%m-%d"),
                    "tags":    [t.strip() for t in tags_in.split(",") if t.strip()],
                    "excerpt": excerpt,
                    "content": content,
                }
                st.session_state.posts.append(new_post)
                save_posts(st.session_state.posts)
                st.success("✅ Post published!")
                st.session_state.view = "home"
                st.rerun()
