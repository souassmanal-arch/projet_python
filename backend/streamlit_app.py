import streamlit as st
import pandas as pd
from app import create_app, db
from models.user import User
from models.schedule import Schedule, Group
from models.room import Room
from models.notification import Notification
from models.reservation import Reservation
from werkzeug.security import check_password_hash
import datetime
import time as time_lib

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="UniScheduler Pro | Future of Education",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Init Flask Context
flask_app = create_app()

# --- PREMIUM DESIGN SYSTEM (PURE PYTHON CSS INJECTION) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp {
        background: radial-gradient(circle at top right, #f0f9ff 0%, #ffffff 100%);
    }

    /* Modern Glassmorphism Card */
    .glass-card {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.4);
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.07);
        transition: transform 0.3s ease;
        margin-bottom: 20px;
    }
    .glass-card:hover {
        transform: translateY(-5px);
        background: rgba(255, 255, 255, 0.9);
    }

    /* Top-tier Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: none;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Buttons Customization */
    .stButton>button {
        background: linear-gradient(135deg, #2563eb 0%, #3b82f6 100%);
        color: white;
        border-radius: 12px;
        padding: 10px 24px;
        font-weight: 700;
        border: none;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        box-shadow: 0 10px 20px -10px rgba(37, 99, 235, 0.5);
        transform: scale(1.02);
    }

    /* Animated Birds background */
    .birds-container {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        z-index: -1; pointer-events: none;
    }
    .wing {
        position: absolute; width: 20px; height: 1px; background: #2563eb;
        opacity: 0.1; animation: fly 15s linear infinite;
    }
    @keyframes fly {
        0% { transform: translateX(-5vw) translateY(30vh) rotate(15deg); }
        50% { transform: translateX(50vw) translateY(60vh) rotate(-15deg); }
        100% { transform: translateX(110vw) translateY(30vh) rotate(15deg); }
    }

    /* Labels & Headings */
    h1, h2, h3 { color: #1e293b; font-weight: 800 !important; }
    .highlight { color: #2563eb; }

    /* Horizontal Scroll Layout */
    .h-list {
        display: flex; overflow-x: auto; gap: 20px; padding: 10px 0;
        scrollbar-width: none;
    }
    .h-list::-webkit-scrollbar { display: none; }
</style>
<div class="birds-container">
    <div class="wing" style="top: 10%; animation-duration: 20s;"></div>
    <div class="wing" style="top: 40%; animation-duration: 25s; animation-delay: 5s;"></div>
    <div class="wing" style="top: 70%; animation-duration: 18s; animation-delay: 2s;"></div>
</div>
""", unsafe_allow_html=True)

# --- SESSION STATE ---
if 'user' not in st.session_state:
    st.session_state.user = None

def login_logic(email, password):
    with flask_app.app_context():
        u = User.query.filter_by(email=email).first()
        if u and check_password_hash(u.password_hash, password):
            return {"id": u.id, "username": u.username, "role": u.role, "group_id": u.group_id}
    return None

# --- APP FLOW ---
if not st.session_state.user:
    # --- PREMIUM LOGIN SCREEN ---
    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])
    
    with c2:
        st.markdown("""
        <div style="text-align: center;">
            <p style="font-weight: 800; color: #2563eb; margin-bottom: 0;">UNI SCHEDULER PRO</p>
            <h1 style="margin-top: 5px;">Bienvenue sur votre <span class='highlight'>Espace</span></h1>
            <p style="color: #64748b;">Connectez-vous pour accéder à vos emplois du temps</p>
        </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            email = st.text_input("📧 Email Professionnel", value="admin@univ.ma")
            password = st.text_input("🔑 Mot de passe", type="password", value="pass123")
            
            if st.button("SE CONNECTER"):
                user = login_logic(email, password)
                if user:
                    st.session_state.user = user
                    st.success("Connexion réussie ! Chargement...")
                    time_lib.sleep(1)
                    st.rerun()
                else:
                    st.error("Identifiants incorrects.")
            
            st.markdown("<hr style='opacity:0.1'>", unsafe_allow_html=True)
            with st.expander("📋 Voir la liste des emails (MDP: pass123)"):
                with flask_app.app_context():
                    all_u = User.query.all()
                    for u in all_u:
                        st.code(f"{u.email} ({u.role})")
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("<br><p style='text-align:center; color:#94a3b8; font-size:0.8rem;'>© 2026 University Timetable Management System</p>", unsafe_allow_html=True)

else:
    user = st.session_state.user
    
    # --- MODERN SIDEBAR ---
    with st.sidebar:
        st.markdown(f"""
        <div style="padding: 20px 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px;">
            <p style="color: #94a3b8; font-size: 0.7rem; font-weight: 800; text-transform: uppercase;">Portail {user['role']}</p>
            <h2 style="color: white !important; font-size: 1.2rem; margin: 0;">{user['username']}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation logic can be tabs in main, or radio here
        nav = st.radio("NAVIGATION", ["📊 Tableau de bord", "📅 Emploi du temps", "🔔 Notifications", "⚙️ Paramètres"])
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("🚪 DÉCONNEXION"):
            st.session_state.user = None
            st.rerun()

    # --- MAIN DASHBOARD CONTENT ---
    if nav == "📊 Tableau de bord":
        st.markdown(f"<h1>Dashboard <span class='highlight'>Central</span></h1>", unsafe_allow_html=True)
        
        if user['role'] == 'admin':
            col1, col2, col3, col4 = st.columns(4)
            with flask_app.app_context():
                col1.metric("Enseignants", User.query.filter_by(role='teacher').count())
                col2.metric("Salles", Room.query.count())
                col3.metric("Groupes", Group.query.count())
                col4.metric("Demandes", Reservation.query.filter_by(status='pending').count())
            
            st.markdown("### 📝 Demandes de Salles Récentes")
            with flask_app.app_context():
                res = Reservation.query.filter_by(status='pending').all()
                if res:
                    for r in res:
                        with st.expander(f"Demande par Prof {r.teacher_id} - Salle {r.room_id}"):
                            st.write(f"Motif: {r.motif}")
                            if st.button(f"Approuver #{r.id}", type="primary"):
                                r.status = 'approved'
                                db.session.commit()
                                st.rerun()
                else:
                    st.info("Aucune demande en attente.")

        elif user['role'] == 'teacher':
            st.markdown("### 📅 Prochains Cours")
            with flask_app.app_context():
                scheds = Schedule.query.filter_by(teacher_id=user['id']).all()
                if scheds:
                    st.markdown('<div class="h-list">', unsafe_allow_html=True)
                    cols = st.columns(len(scheds))
                    for i, s in enumerate(scheds):
                        with cols[i]:
                            st.markdown(f"""
                            <div class="glass-card">
                                <p style='color: #2563eb; font-weight: 800; font-size: 0.7rem;'>{s.day_of_week.upper()}</p>
                                <h4 style='margin: 5px 0;'>{s.course_name}</h4>
                                <p style='font-size: 0.9rem; color: #64748b;'>📍 Salle {s.room_id}<br>⏰ {s.start_time.strftime('%H:%M')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("### ➕ Actions Rapides")
            c1, c2 = st.columns(2)
            with c1:
                with st.container():
                     st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
                     st.subheader("Réserver une Salle")
                     with flask_app.app_context():
                         rooms = Room.query.all()
                         r_names = [r.name for r in rooms]
                     sel_r = st.selectbox("Choisir la salle", r_names)
                     if st.button("Vérifier Disponibilité"):
                         st.success("Salle disponible !")
                     st.markdown("</div>", unsafe_allow_html=True)

        elif user['role'] == 'student':
            st.markdown("### 🎓 Votre Semaine d'Études")
            with flask_app.app_context():
                scheds = Schedule.query.filter_by(group_id=user['group_id']).all()
                if scheds:
                    st.markdown('<div class="h-list">', unsafe_allow_html=True)
                    cols = st.columns(len(scheds) if len(scheds) < 5 else 4)
                    for i, s in enumerate(scheds):
                        with cols[i % 4]:
                            st.markdown(f"""
                            <div class="glass-card">
                                <p style='color: #10b981; font-weight: 800; font-size: 0.7rem;'>{s.day_of_week.upper()}</p>
                                <h4 style='margin: 5px 0;'>{s.course_name}</h4>
                                <p style='font-size: 0.8rem; color: #64748b;'>📍 Salle {s.room_id}<br>⏰ {s.start_time.strftime('%H:%M')}</p>
                            </div>
                            """, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown("### 💡 Infos Utiles")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown("<div class='glass-card' style='text-align:center;'><h3>📚</h3><p>Accès Bibliothèque</p><small>Ouvert 8h-20h</small></div>", unsafe_allow_html=True)
            with c2:
                st.markdown("<div class='glass-card' style='text-align:center;'><h3>🌐</h3><p>Wifi Eduroam</p><small>Connecté</small></div>", unsafe_allow_html=True)
            with c3:
                st.markdown("<div class='glass-card' style='text-align:center;'><h3>🍔</h3><p>Menu Restaurant</p><small>Voir les plats</small></div>", unsafe_allow_html=True)

    elif nav == "📅 Emploi du temps":
        st.markdown("<h1>Mon <span class='highlight'>Planning</span></h1>", unsafe_allow_html=True)
        with flask_app.app_context():
            if user['role'] == 'student':
                data = Schedule.query.filter_by(group_id=user['group_id']).all()
            else:
                data = Schedule.query.filter_by(teacher_id=user['id']).all()
            
            if data:
                df = pd.DataFrame([{
                    "Jour": s.day_of_week,
                    "Heure": s.start_time.strftime('%H:%M'),
                    "Cours": s.course_name,
                    "Lieu": f"Salle {s.room_id}"
                } for s in data])
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Aucun cours trouvé pour votre planning.")

    elif nav == "🔔 Notifications":
        st.markdown("<h1>Flux de <span class='highlight'>Messages</span></h1>", unsafe_allow_html=True)
        with flask_app.app_context():
            notifs = Notification.query.filter_by(user_id=user['id']).order_by(Notification.created_at.desc()).all()
            if notifs:
                for n in notifs:
                    color = "#2563eb"
                    if n.type == "danger": color = "#ef4444"
                    elif n.type == "success": color = "#10b981"
                    
                    st.markdown(f"""
                    <div class="glass-card" style="border-left: 6px solid {color};">
                        <div style="display:flex; justify-content:space-between;">
                            <strong style="color:#0f172a;">{n.title}</strong>
                            <small style="color:#94a3b8;">{n.created_at.strftime('%D %H:%M')}</small>
                        </div>
                        <p style="margin-top:10px; color:#475569;">{n.message}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("Vous n'avez pas de nouvelles notifications.")
