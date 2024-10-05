import streamlit as st
from fpdf import FPDF
from unidecode import unidecode
import base64
from PyPDF2 import PdfMerger
from io import BytesIO

# Function to create a single formatted PDF for one newsletter
def create_newsletter_pdf(newsletter_text):
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
    
    # Add space after the title
    pdf.ln(5)
    
    # Subtitle - smaller, bold, left-aligned
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(0, 0, 0)  # Black
    pdf.cell(0, 10, subtitle, ln=True, align='L')
    
    # Add space after the subtitle
    pdf.ln(10)
    
    # Quote - italic, framed
    pdf.set_font("Arial", 'I', 14)
    pdf.set_text_color(105, 105, 105)  # Dark gray (RGB)
    pdf.multi_cell(0, 10, quote, border=1, align='C')
    
    # Add space after the quote
    pdf.ln(10)
    
    # Author and date - small, italic, right-aligned
    pdf.set_font("Arial", 'I', 12)
    pdf.set_text_color(0, 0, 0)  # Black
    pdf.cell(0, 10, author_date, ln=True, align='R')
    
    # Add space after the author and date
    pdf.ln(10)
    
    # Body text - centered
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0, 0, 0)  # Black
    pdf.multi_cell(0, 8, unidecode(body_text), align='C')
    
    return pdf

# Streamlit app title
st.title("Générateur de PDF pour Newsletter")

# Initialize session state for newsletters
if 'newsletters' not in st.session_state:
    st.session_state['newsletters'] = []

# Text area for user input
newsletter_text = st.text_area("Entrez le contenu de votre newsletter :")

# Button to add the newsletter to session state
if st.button("Ajouter la Newsletter"):
    if newsletter_text.strip():  # Add only if text is not empty
        st.session_state['newsletters'].append(newsletter_text.strip())
        st.success("Newsletter ajoutée !")
    else:
        st.warning("Veuillez entrer le contenu de la newsletter avant d'ajouter.")

# Display all added newsletters
if st.session_state['newsletters']:
    st.subheader("Newsletters ajoutées:")
    for i, newsletter in enumerate(st.session_state['newsletters']):
        st.markdown(f"**Newsletter {i+1}:** {newsletter[:100]}...")  # Display first 100 characters

# Button to generate and download the combined PDF
if st.button("Générer le PDF combiné"):
    if st.session_state['newsletters']:
        merger = PdfMerger()
        all_pdfs = []

        # Create a PDF for each newsletter
        for idx, newsletter_text in enumerate(st.session_state['newsletters']):
            pdf = create_newsletter_pdf(newsletter_text)
            if pdf is not None:
                # Get PDF content as bytes
                pdf_bytes = pdf.output(dest='S').encode('latin1')
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
