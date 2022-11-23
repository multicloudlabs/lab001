from flask import Flask, render_template, request
app = Flask(__name__)
    
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

# Initialize tracing and an exporter
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

# Initialize automatic instrumentation with Flask
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
### otel for 

import json
from ibm_watson import LanguageTranslatorV3
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# Set some variables

import configparser
configparser = configparser.ConfigParser()
configparser.read('translator.ini')


api_key = configparser['DEFAULT']['api_key']
api_url = configparser['DEFAULT']['api_url']
model_id = configparser['DEFAULT']['model_id']

chat_history = []

@app.route("/")
def index():
    return render_template("./index.html")

@app.route("/translate", methods=['GET',"POST"])
def home():
    if request.method == "GET":
        #chat_history.append(msg)

        chat_history.append(" ")

        history_copy = chat_history.copy()
        history_copy.reverse()

        return render_template("./translate.html", messages=history_copy)
    else:
        # Get input sentence
        input_sentence = request.form.get("input")

        # Prepare the Authenticator
        authenticator = IAMAuthenticator(api_key)
        language_translator = LanguageTranslatorV3(
            version='2018-05-01',
            authenticator=authenticator
        )

        language_translator.set_service_url(api_url )

        # Translate
        response = language_translator.translate(
            text=input_sentence,
            model_id=model_id).get_result()


        # Print results
        # print(json.dumps(translation, indent=2, ensure_ascii=False))
        #s = json.dumps(response.json)

        answer = " "

        for s in response["translations"]:
            answer = s["translation"]

        #j = json.loads(response)
        #tx = j["translations"][0]
        #t = tx["translation"]

        # answer = chatbot.get_response(user_response)
        # ans = standard_answers.get(user_response.lower(),"Sorry, I could not understand")
        #answer = t
        chat_history.append("Polish: " +str(answer))
        chat_history.append("English: " +input_sentence)
        chat_history.append("***")
    
        history_copy = chat_history.copy()
        history_copy.reverse()

        return render_template("./index.html", messages = history_copy)
app.run(debug=True, threaded=False)
