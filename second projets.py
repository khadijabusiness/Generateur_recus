import streamlit as st
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime
import io

# --- FONCTION DE GÉNÉRATION DU PDF CONFIGURABLE ---
def generer_pdf(infos_entreprise, nom_client, articles, numero_recu):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle(f"Reçu {numero_recu}")
    
    # En-tête personnalisé par le businessman
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, 750, infos_entreprise["nom_biz"])
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 735, f"Contact: {infos_entreprise['email_biz']} | Tél: {infos_entreprise['tel_biz']}")
    pdf.drawString(50, 720, f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    pdf.drawString(50, 705, f"Reçu N°: {numero_recu}")
    
    # Client
    pdf.drawString(400, 735, f"Client: {nom_client}")
    pdf.line(50, 690, 550, 690)
    
    # Tableau
    pdf.setFont("Helvetica-Bold", 11)
    pdf.drawString(50, 670, "Description")
    pdf.drawString(300, 670, "Qté")
    pdf.drawString(380, 670, "Prix Unitaire")
    pdf.drawString(480, 670, "Total")
    pdf.line(50, 660, 550, 660)
    
    pdf.setFont("Helvetica", 11)
    y = 640
    total_general = 0
    
    for item in articles:
        if item["nom"]: 
            total_article = item["qte"] * item["prix"]
            total_general += total_article
            
            pdf.drawString(50, y, item["nom"])
            pdf.drawString(300, y, str(item["qte"]))
            pdf.drawString(380, y, f"{item['prix']} FCFA")
            pdf.drawString(480, y, f"{total_article} FCFA")
            y -= 20
            
    pdf.line(50, y + 10, 550, y + 10)
    
    # Total
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(380, y - 10, "TOTAL À PAYER :")
    pdf.drawString(480, y - 10, f"{total_general} FCFA")
    
    pdf.setFont("Helvetica-Oblique", 10)
    pdf.drawString(50, y - 50, "Merci pour votre confiance !")
    
    pdf.save()
    buffer.seek(0)
    return buffer, total_general

# --- INTERFACE GRAPHIQUE STREAMLIT ---
st.set_page_config(page_title="Générateur de Reçus Pro", page_icon="🧾", layout="centered")

st.title("🧾 Générateur de Reçus Professionnels")
st.write("Configure ton entreprise et génère tes reçus clients instantanément.")

# NOUVEAU : Section de configuration pour le businessman
with st.sidebar:
    st.header("⚙️ Configuration de ton Business")
    nom_biz = st.text_input("Nom de ton entreprise", value="Mon Business")
    tel_biz = st.text_input("Numéro de Téléphone", value="+221 ")
    email_biz = st.text_input("Adresse Email", value="contact@monbusiness.com")
    st.info("Ces informations apparaîtront en haut de tes reçus PDF.")

infos_entreprise = {"nom_biz": nom_biz, "tel_biz": tel_biz, "email_biz": email_biz}

# Formulaire d'informations générales de la vente
st.subheader("1. Informations de la vente")
col1, col2 = st.columns(2)
with col1:
    nom_client = st.text_input("Nom du Client", value="Client Anonyme")
with col2:
    numero_recu = st.text_input("Numéro de Reçu", value=datetime.now().strftime("%Y%m%d-%H%M"))

# Gestion dynamique des articles
st.subheader("2. Articles vendus")
if "nb_articles" not in st.session_state:
    st.session_state.nb_articles = 1

liste_articles = []

for i in range(st.session_state.nb_articles):
    st.markdown(f"**Article {i+1}**")
    c1, c2, c3 = st.columns([2, 1, 1.5])
    with c1:
        nom = st.text_input(f"Nom de l'article", key=f"nom_{i}", label_visibility="collapsed", placeholder="Nom de l'article")
    with c2:
        qte = st.number_input(f"Quantité", min_value=1, value=1, step=1, key=f"qte_{i}", label_visibility="collapsed")
    with c3:
        prix = st.number_input(f"Prix (FCFA)", min_value=0, value=0, step=100, key=f"prix_{i}", label_visibility="collapsed")
    liste_articles.append({"nom": nom, "qte": qte, "prix": prix})

cb1, cb2 = st.columns(2)
with cb1:
    if st.button("➕ Ajouter un article"):
        st.session_state.nb_articles += 1
        st.rerun()
with cb2:
    if st.button("➖ Supprimer le dernier") and st.session_state.nb_articles > 1:
        st.session_state.nb_articles -= 1
        st.rerun()

st.markdown("---")

# Génération et téléchargement
if st.button("🚀 Calculer et Préparer le Reçu", type="primary"):
    pdf_data, total = generer_pdf(infos_entreprise, nom_client, liste_articles, numero_recu)
    
    st.success(f"Calcul terminé ! Total Général : **{total} FCFA**")
    
    st.download_button(
        label="📥 Télécharger le Reçu PDF",
        data=pdf_data,
        file_name=f"Recu_{numero_recu}.pdf",
        mime="application/pdf"
    )