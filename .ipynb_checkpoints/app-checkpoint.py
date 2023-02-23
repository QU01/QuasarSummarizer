import gradio as gr
from gradio.processing_utils import decode_base64_to_file
import openai
import os
import PyPDF2

openai.api_key = OPENAI_KEY

def get_filename(file_obj):
    return file_obj.name

def summarize(prompt):
    augmented_prompt = f"summarize this text: {prompt}"
    augmented_prompt = augmented_prompt[0:2048]
    return openai.Completion.create(
        model="text-davinci-002",
        prompt=augmented_prompt,
        temperature=.5,
        max_tokens=1000,
    )["choices"][0]["text"]

def pdf_summarizer(pdf_file, sections):
    
    with open(get_filename(pdf_file), 'rb') as pdf_file:
    # Crea un objeto PyPDF2.PdfFileReader
    # Ouvre le fichier PDF dans un objet PyPDF2.PdfFileReader
        print(pdf_file)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
    
        # Extrae el texto del PDF
        # Extraire le texte du PDF
        text = ''
        for page in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page].extract_text()
        
        # Elimina caracteres no deseados del texto
        # Supprimer les caractères indésirables du texte
        text = text.replace('\n'," ").replace('- ', '')
        
        # Divide el texto en secciones
        # Diviser le texte en sections
        text_sections = {}
        sections_list = sections.split("-")
        for i, section in enumerate(sections_list):
            if i < len(sections_list)-1:
                start = text.find(section)
                end = text.find(sections_list[i+1])
            else:
                start = text.find(section)
                end = len(text)
            text_sections[section] = text[start:end-3].strip()

        # Genera un resumen para cada sección utilizando GPT-3
        # Générer un résumé pour chaque section en utilisant GPT-3
        summaries = {}
        for section, text_section in text_sections.items():
            summary = summarize(text_section)
            summaries[section] = summary
        
        return summaries

pdf_file = gr.inputs.File(label="PDF File")
sections = gr.inputs.Textbox(label="Sections (separated by '-'): ")
output_text = gr.outputs.Textbox(label="Summarized text:")

while __name__ == '__main__':

    gr.Interface(fn=pdf_summarizer, inputs=[pdf_file, sections], outputs=output_text).launch()