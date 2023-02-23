import gradio as gr
from gradio.processing_utils import decode_base64_to_file
import openai
import os
import PyPDF2

openai.api_key = ""

def get_filename(file_obj):
    return file_obj.name


def generate_html(data):
    # Create the HTML document with Bootstrap
    html = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Quasar Summarizer</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>
            <div class="container">
                <div class="row">
                    <div class="col-md-12">
                        <h1>Quasar Summarizer</h1>
                    </div>
                </div> """

    for name, content in data.items():

      html += f"""<div class="row">
                    <div class="col-md-12">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">{name}</h5>
                                <p class="card-text">{content}</p>
                            </div>
                        </div>
                    </div>
                </div>"""

    html += """</div>
            </body>"""

    return html

def summarize(prompt, coments):
    augmented_prompt = f"summarize this text, {coments}: {prompt}"
    augmented_prompt = augmented_prompt[0:2048]
    return openai.Completion.create(
        model="text-davinci-003",
        prompt=augmented_prompt,
        temperature=.5,
        max_tokens=1000,
    )["choices"][0]["text"]

def pdf_summarizer(pdf_file, sections, coments):
    
    with open(get_filename(pdf_file), 'rb') as pdf_file:
    # Crea un objeto PyPDF2.PdfFileReader
        print(pdf_file)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
    
        # Extrae el texto del PDF
        text = ''
        for page in range(len(pdf_reader.pages)):
            text += pdf_reader.pages[page].extract_text()
        
        # Elimina caracteres no deseados del texto
        text = text.replace('\n'," ").replace('- ', '')
        
        # Divide el texto en secciones
        text_sections = {}
        sections_list = sections.split("-")
        for i, section in enumerate(sections_list):
            if i < len(sections_list)-1:
                start = text.find(section)
                end = text.find(sections_list[i+1])
            else:
                start = text.find(section)
                end = len(text)
            text_sections[section] = text[start:end-1].strip()

        # Genera un resumen para cada sección utilizando GPT-3
        summaries = {}
        for section, text_section in text_sections.items():
            summary = summarize(text_section, coments)
            print("--------")
            summaries[section] = summary
        
        return generate_html(summaries)

pdf_file = gr.inputs.File(label="PDF File")
sections = gr.inputs.Textbox(label="Sections (separated by '-'): ")
coments = gr.inputs.Textbox(label="Add coment for the summarizing. eg: Resumen en español")
output_text = gr.outputs.HTML(label="Summarized text:")
description = "Large Language Models (LLMs) like GPT-3 have the potential to make science more accessible to the masses. With the ability to process and understand natural language at a high level, these models can be used to simplify complex scientific concepts and make them easier to understand for a wider audience. By using LLMs to generate summaries, translate technical jargon, or even answer questions, we can bridge the knowledge gap between experts and the general public, making science more approachable and understandable for all."

gr.Interface(fn=pdf_summarizer, inputs=[pdf_file, sections, coments], outputs=output_text, title="Quasar Summarizer", 
             description=description).launch()