import streamlit as st
from fpdf import FPDF
from unidecode import unidecode
import base64
from PyPDF2 import PdfMerger
from io import BytesIO
from get_mails import get_email
import re



def process_body(body_text : str):

    pattern = r"\*"
    cleaned_body = re.split(pattern, body_text, flags=re.IGNORECASE)
    
    if len(cleaned_body) < 2:
        st.write("motif non trouvé")
        # Si le motif n'est pas trouvé, retourner le texte original
        cleaned_body = [body_text]
    else:
        abstract_and_beginning_article = cleaned_body[0]  # Prendre la partie après le motif
        end_article = cleaned_body[1:]

    #cleaned_body = cleaned_body.strip()


    RIAseparator = "READ IN APP"

    abstract_and_beginning_article = re.split(RIAseparator, abstract_and_beginning_article, flags=re.IGNORECASE)
    if len(abstract_and_beginning_article) >= 2:
        abstract = abstract_and_beginning_article[0]
        beginning = abstract_and_beginning_article[1]
        end_article.insert(0,beginning)
        article = " ".join(end_article).strip()
    
    separator = "Forwarded this email\? Subscribe here"
    parts = re.split(separator, abstract, flags=re.IGNORECASE)[0].strip()
    return parts, article


# Fonction pour créer un PDF formaté pour une newsletter
def create_newsletter_pdf(title_json : str,email_json : str):
    pdf = FPDF()
    pdf.set_margins(left=25, top=20, right=25)
    pdf.add_page()

    # Nettoyer le texte pour éviter les problèmes d'encodage
    clean_body = unidecode(email_json)
    clear_title = unidecode(title_json)

    # Traiter le "body" pour obtenir l'abstract et l'article
    abstract, clean_article = process_body(clean_body)

    # Configurer la police
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 0, 0)  # Noir
    pdf.multi_cell(0, 10, clear_title.upper(), align='L')

    pdf.ln(5)  # Ajouter un espace

    # Ajouter l'Abstract
    if abstract:
        abstract = abstract.replace('\r\n', ' ')
        pdf.set_font("Arial",'B', size=12)
        pdf.set_text_color(50, 50, 50)  # Dark grey
        pdf.multi_cell(0, 6, abstract, align='L')
        pdf.ln(9)  # Ajouter un espace

    # Ajouter l'Article
    if clean_article:
        clean_article = clean_article.replace('\r\n\r\n', 'BREAK')
        clean_article = clean_article.replace('\r\n', ' ')
        clean_article = clean_article.replace('BREAK', '\r\n\r\n')

        # pdf.set_font("Arial", 'B', 14)
        # pdf.set_text_color(50, 50, 50)  # Dark grey
        # pdf.cell(0, 10, "Article", ln=True, align='L')
        pdf.set_font("Arial", size=12)
        pdf.set_text_color(0, 0, 0)  # Black
        pdf.multi_cell(0, 6, clean_article)

    return pdf


# Streamlit app title
st.title("Générateur de PDF pour Newsletter")


# Initialiser l'état de session pour les newsletters
if 'newsletters' not in st.session_state:
    st.session_state['newsletters'] = []
if 'title' not in st.session_state:
    st.session_state['title'] = []

# Bouton pour récupérer les emails et les traiter
if st.button("Mail"):
    mails = get_email()
    #st.write(mails)  # Optionnel : Afficher les mails récupérés pour le débogage
    
    # Traiter les mails et extraire le texte du corps
    for mail in mails:
        title = mail.get('subject', '')
        body = mail.get('body', '')
        if body.strip():
            st.session_state['newsletters'].append(body.strip())
            st.session_state['title'].append(title.strip())
    st.success(f"{len(mails)} newsletters ont été ajoutées à partir des emails.")

# Afficher toutes les newsletters ajoutées
if st.session_state['title']:
    st.subheader("Newsletters ajoutées :")
    for i, title in enumerate(st.session_state['title']):
        st.markdown(f"**Newsletter {i+1} :** {title}")  # Afficher les 100 premiers caractères


# Button to generate and download the combined PDF
#if st.button("Générer le PDF combiné"):
if st.session_state['newsletters']:
    merger = PdfMerger()
    all_pdfs = []

    # Create a PDF for each newsletter
    for idx, (title_text, newsletter_text) in enumerate(zip(st.session_state['title'], st.session_state['newsletters'])):
        pdf = create_newsletter_pdf(title_text,newsletter_text)
        if pdf is not None:
            # Get PDF content as bytes
            pdf_bytes = pdf.output(dest='S').encode('latin1', 'ignore')
            pdf_output = BytesIO(pdf_bytes)
            pdf_output.seek(0)  # Ensure we're at the start of the BytesIO object
            all_pdfs.append(pdf_output)
        else:
            st.error(f"Erreur lors de la création du PDF pour la newsletter {idx+1}")

    # Merge all PDFs
    if all_pdfs:
        for pdf_data in all_pdfs:
            # Add each BytesIO PDF to the merger
            merger.append(pdf_data)
        
        # Save the merged PDF in memory
        merged_pdf_output = BytesIO()
        merger.write(merged_pdf_output)
        merger.close()
        merged_pdf_output.seek(0)
        
        # Read the merged PDF for display and download
        pdf_content = merged_pdf_output.getvalue()
        
        # Display the merged PDF directly in the app
        base64_pdf = base64.b64encode(pdf_content).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)

        # Allow downloading the merged PDF
        st.download_button(
            label="Télécharger le PDF combiné",
            data=pdf_content,
            file_name="newsletter_combined.pdf",
            mime="application/pdf"
        )

    else:
        st.error("Aucun PDF valide à combiner.")
    # else:
    #     st.warning("Aucune newsletter n'a été ajoutée pour la génération du PDF.")
