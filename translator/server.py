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


# Read configuration

configparser = configparser.ConfigParser()
configparser.read('server.ini')

host = configparser['DEFAULT']['host']
port = configparser['DEFAULT']['port']
api_key = configparser['DEFAULT']['api_key']
api_url = configparser['DEFAULT']['api_url']
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


@app.route("/api/translate", methods=["POST"])
def translate():
        input_sentence = request.args.get("input_sentence")
        language_model = request.args.get("language_model")

        print("input_sentence=", input_sentence)
        print("language_model=", language_model)

        # Prepare the Authenticator
        authenticator = IAMAuthenticator(api_key)
        language_translator = LanguageTranslatorV3(
            version='2018-05-01',
            authenticator=authenticator
        )

        language_translator.set_service_url(api_url )

        input_model = model_id

        if (language_model != "" and language_model != None):
            input_model = language_model

        print(input_model)

        # Translate
        response = language_translator.translate(
            text=input_sentence,
            model_id=input_model).get_result()


        output_sentence = " "

        for s in response["translations"]:
            output_sentence = s["translation"]

        return output_sentence



if __name__ == "__main__":
    app.run(host=host, port=port, debug=True, threaded=False)
#    app.run(ssl_context='adhoc')