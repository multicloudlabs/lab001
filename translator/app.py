#!/usr/bin/env python3

from flask import Flask, render_template, request
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from ibm_watson import LanguageTranslatorV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import configparser
import json
import requests


# Read configuration

configparser = configparser.ConfigParser()
configparser.read('app.ini')

host = configparser['DEFAULT']['host']
port = configparser['DEFAULT']['port']
server_port = configparser['DEFAULT']['server_port']
model_id = configparser['DEFAULT']['model_id']

# Create app
app = Flask(__name__)


# Initialize tracing and an exporter
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# Initialize automatic instrumentation with Flask
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

chat_history = []

@app.route("/")
def index():
    return render_template("./index.html")

@app.route("/translate", methods=['GET',"POST"])
def process_request():
    if request.method == "GET":
        #chat_history.append(msg)

        chat_history.append(" ")

        history_copy = chat_history.copy()
        history_copy.reverse()

        return render_template("./translate.html", messages=history_copy)
    else:
        # Get input sentence
        input_sentence = request.form.get("input")

        url = "http://127.0.0.1:" + server_port+ "/api/translate"
        response = requests.post(url=url,params={'input_sentence':input_sentence,'language_model':model_id})

        output_sentence = response.text

        chat_history.append("PL: " +str(output_sentence))
        chat_history.append("EN: " +input_sentence)
        chat_history.append("***")
    
        history_copy = chat_history.copy()
        history_copy.reverse()

        return render_template("./translate.html", messages = history_copy)

if __name__ == "__main__":
    app.run(host=host, port=port, debug=True, threaded=False)
#    app.run(ssl_context='adhoc')