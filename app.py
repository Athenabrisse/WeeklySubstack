import streamlit as st
from fpdf import FPDF
from unidecode import unidecode
import base64
from PyPDF2 import PdfMerger
from io import BytesIO
from get_mails import get_email
import re



def process_body(body_text : str):
    # Étape 2: Supprimer tout le texte avant et y compris "Forwarded this email? Subscribe here for more *"
    #pattern = r"Forwarded this email\?"
    pattern = r"\*"

    cleaned_body = re.split(pattern, body_text, flags=re.IGNORECASE)
    
    if len(cleaned_body) < 2:
        st.write("motif non trouvé")
        # Si le motif n'est pas trouvé, retourner le texte original
        cleaned_body = [body_text]
    else:
        abstract = cleaned_body[1]  # Prendre la partie après le motif
        articles = cleaned_body[2]
    #cleaned_body = cleaned_body.strip()

    # Étape 3: Séparer l'Abstract et l'Article à partir du séparateur "------------------------------"
    separator = "------------------------------"
    parts = re.split(separator, articles, flags=re.IGNORECASE)
    if len(parts) >= 2:
        article = parts[1]

    RIAseparator = "READ IN APP"
    articleparts = re.split(RIAseparator, article, flags=re.IGNORECASE)
    if len(articleparts) >= 2:
        article = articleparts[1]

    return abstract, article


# Fonction pour créer un PDF formaté pour une newsletter
def create_newsletter_pdf(email_json : str):
    pdf = FPDF()
    pdf.add_page()

    # Nettoyer le texte pour éviter les problèmes d'encodage
    clean_body = unidecode(email_json)

    # Traiter le "body" pour obtenir l'abstract et l'article
    abstract, article = process_body(clean_body)

    # Configurer la police
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 0, 0)  # Noir

    # Ajouter le Titre
    pdf.cell(0, 10, clean_body.upper(), ln=True, align='C')
    pdf.ln(5)  # Ajouter un espace

    # Ajouter l'Abstract
    if abstract:
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(50, 50, 50)  # Gris foncé
        pdf.cell(0, 10, "Abstract", ln=True, align='L')
        pdf.set_font("Arial", size=12)
        pdf.set_text_color(0, 0, 0)  # Noir
        pdf.multi_cell(0, 6, abstract)
        pdf.ln(5)  # Ajouter un espace

    # Ajouter l'Article
    if article:
        pdf.set_font("Arial", 'B', 14)
        pdf.set_text_color(50, 50, 50)  # Gris foncé
        pdf.cell(0, 10, "Article", ln=True, align='L')
        pdf.set_font("Arial", size=12)
        pdf.set_text_color(0, 0, 0)  # Noir
        pdf.multi_cell(0, 6, article)

    return pdf


# Function to create a single formatted PDF for one newsletter
def create_newsletter_pdf_formatted(newsletter_text):
    pdf = FPDF()
    pdf.add_page()
    
    # Clean and split lines of text
    lines = newsletter_text.split('\n')
    lines = [line.strip() for line in lines if line.strip()]  # Remove extra spaces and empty lines

    # Check if the newsletter has enough parts
    if len(lines) < 5:
        st.error("Le format de la newsletter ne contient pas suffisamment de parties.")
        return None

    title = lines[0]  # Main title
    subtitle = lines[1]  # Subtitle
    quote = lines[2]  # Quote
    author_date = lines[3]  # Author and date
    body_text = '\n'.join(lines[4:])  # Body text (all remaining lines)
        
    # Main title - large, bold, centered
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(105, 105, 105)  # Dark gray (RGB)
    pdf.cell(0, 15, unidecode(title).upper(), ln=True, align='L')

    # Subtitle - smaller, bold, left-aligned
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(0, 0, 0)  # Black
    pdf.cell(0, 10, unidecode(subtitle), ln=True, align='L')  # Appliquer unidecode

    # Quote - italic, framed
    pdf.set_font("Arial", 'I', 14)
    pdf.set_text_color(105, 105, 105)  # Dark gray (RGB)
    pdf.multi_cell(0, 10, unidecode(quote), border=1, align='C')  # Appliquer unidecode

    # Author and date - small, italic, right-aligned
    pdf.set_font("Arial", 'I', 12)
    pdf.set_text_color(0, 0, 0)  # Black
    pdf.cell(0, 10, unidecode(author_date), ln=True, align='R')  # Appliquer unidecode
    
    return pdf

def create_newsletter_pdf_Athena(newsletter_text):
    pdf = FPDF()
    pdf.add_page()

    clean_text = unidecode(newsletter_text)

    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0,0,0)

    pdf.multi_cell(0, 6, clean_text, align='L')
    
    return pdf

# Streamlit app title
st.title("Générateur de PDF pour Newsletter")


# Initialiser l'état de session pour les newsletters
if 'newsletters' not in st.session_state:
    st.session_state['newsletters'] = []

# Bouton pour récupérer les emails et les traiter
if st.button("Mail"):
    mails = get_email()
    #st.write(mails)  # Optionnel : Afficher les mails récupérés pour le débogage
    
    # Traiter les mails et extraire le texte du corps
    for mail in mails:
        body = mail.get('body', '')
        if body.strip():
            st.session_state['newsletters'].append(body.strip())
    st.success(f"{len(mails)} newsletters ont été ajoutées à partir des emails.")

# Afficher toutes les newsletters ajoutées
if st.session_state['newsletters']:
    st.subheader("Newsletters ajoutées :")
    for i, newsletter in enumerate(st.session_state['newsletters']):
        st.markdown(f"**Newsletter {i+1} :** {newsletter[:100]}...")  # Afficher les 100 premiers caractères
        
        #subject = newsletter.get('subject', 'Sans Sujet')
        #st.markdown(f"**Newsletter {i+1} :** {subject}...")  


# Button to generate and download the combined PDF
if st.button("Générer le PDF combiné"):
    if st.session_state['newsletters']:
        merger = PdfMerger()
        all_pdfs = []

        # Create a PDF for each newsletter
        for idx, newsletter_text in enumerate(st.session_state['newsletters']):
            #st.write(newsletter_text)
            pdf = create_newsletter_pdf(newsletter_text)
            if pdf is not None:
                # Get PDF content as bytes
                #pdf_bytes = pdf.output(dest='S').encode('latin1')
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
    else:
        st.warning("Aucune newsletter n'a été ajoutée pour la génération du PDF.")
