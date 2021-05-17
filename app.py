
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 21:20:56 2021
Based on https://github.com/cds-hooks/cds-service-example-python
@author: Chit Win
"""

from flask import Flask, json
from flask_cors import CORS
from flask import Response, request
import requests
from werkzeug.datastructures import ResponseCacheControl
import random
import os

app = Flask(__name__)
cors = CORS(app)


@app.route('/cds-services')
def discovery():
    return json.jsonify({
        'services': [
            {
                'hook': 'patient-view',
                'name': 'Static CDS Service in Python',
                'description': 'An example static CDS service in Python',
                'id': 'static',
                'prefetch': {
                    'patient': "Patient/{{context.patientId}}"
                }
            },
            {
                "id": "patient-greeting",
                "title": "Patient greeting",
                "description": "Display which patient the user is currently working with",
                "hook": "patient-view",
                "prefetch": {
                    "patient": "Patient/{{context.patientId}}"
                }
            },
        #  {
        #         "id": "patient-order-select",
        #         "title": "Patient bundle",
        #         "description": "Display patient related data",
        #         "hook": "order-select",
        #         "selection": ["MedicationRequest?patient={{context.patientId}}", "NutritionOrder?patient={{context.patientId}}", "Condition?patient={{context.patientId}}"]
        #     },
            {
                "id": "complete-patient-history",
                "title": "Complete medical history",
                "description": "Display patient related data",
                "hook": "patient-view"
            },
            {
                "id": "patient-immunization",
                "title": "Immunization history",
                "description": "Display patient related immunization data",
                "hook": "patient-view"
            },
            {
                "id": "patient-allergy",
                "title": "AllergyIntolerance history",
                "description": "Display patient related allergy data",
                "hook": "patient-view"
            },
            {
                "id": "patient-documentreference",
                "title": "Patient DocumentReference",
                "description": "Display patient related document reference data",
                "hook": "patient-view"
            }
        ]
    })


@app.route('/cds-services/static', methods=['POST'])
def service():
    card1 = card('Success Card', 'success', link(
        'Static CDS Service', 'http://example.com'))
    card1['detail'] = 'This is a test of a static success card.'
    card1['links'].append(link('Google', 'https://google.com'))
    card1['links'].append(link('Github', 'https://github.com'))

    print(card1)

    source = link('Static CDS Service')

    card2 = card('Info card', 'info', source)
    card3 = card('Warning card', 'warning', source)
    card4 = card('Hard stop card', 'hard-stop', source)

    return json.jsonify({
        'cards': [card1, card2, card3, card4]
    })


def card(summary, indicator, source):
    return {
        'summary': summary, 'detail': '', 'indicator': indicator,
        'source': source, 'links': []
    }


def link(label, url=None):
    result = {'label': label}
    if url:
        result['url'] = url

    return result


@app.route('/cds-services/patient-greeting', methods=['POST'])
def greeting():
    cards = {}

    # if get_fhirVersion(request.json['fhirServer']) == "4.5.0":
    print(request.json)
    if request.json['prefetch'] and 'patient' in request.json['prefetch']:
        cards = {
            "cards": [
                {
                    "uuid": "73b7f78f-bd27-4a8f-9ec8-7f8737a7ad31",
                    "summary": f"Now seeing: {request.json['prefetch']['patient']['name'][0]['given'][0]} {request.json['prefetch']['patient']['name'][0]['family']}",
                    "source": {
                        "label": "Patient greeting service"
                    },
                    "indicator": (lambda: ["info", "warning", "critical"][random.randint(0, 2)])()
                }
            ]
        }

    print(cards)

    return Response(json.dumps(cards), 200)


def get_fhirVersion(endpoint):
    return requests.get(endpoint+'/metadata').json()['fhirVersion']


@app.route('/cds-services/patient-order-select', methods=['POST'])
def pos():
    print(request.json)
    return Response(json.dumps(request.json), 200)


# @app.route('/cds-services/patient-visit', methods=['POST'])
# def drill():
#   print(request.json)
#   return Response(json.dumps(request.json), 200)


_RESTcall = lambda method, endpoint, headers, data={}: requests.request(
    method, endpoint, headers=headers, data=data)

patient_name = ''


@app.route('/cds-services/complete-patient-history', methods=['POST'])
def drill():

    patient_hook = request.json
    headers = {'Authorization': _get_auth_from_hook(
        patient_hook['fhirAuthorization'])}
    url = patient_hook['fhirServer'] + \
        f"/Patient/{patient_hook['context']['patientId']}/$everything"
    response = _RESTcall("GET", url, headers=headers).json()
    entry = response['entry']
    for r in response['link']:
        if 'next' in r:
            response = _RESTcall(
                "GET", r['next'], headers=headers, data={}).json()
            entry += response['entry']

    return Response(json.dumps({"cards": [entry2card(e) for e in entry]}), 200)


track_count = {}


def entry2card(entry: dict):
    global patient_name
    card = dict()
    card['indicator'] = (
        lambda: ["info", "warning", "critical"][random.randint(0, 2)])()
    if entry['resource']['resourceType'] not in track_count:
        if entry['resource']['resourceType'] != "Patient":
            track_count[entry['resource']['resourceType']] = 1
        else:
            patient_name = entry['resource']['name'][0]['given'][0]
    else:
        track_count[entry['resource']['resourceType']] += 1

    card['summary'] = patient_name + '\'s ' + str(track_count[entry['resource']['resourceType']]) + _num_suffix(
        track_count[entry['resource']['resourceType']]) + ' ' + entry['resource']['resourceType'] if entry['resource']['resourceType'] != "Patient" else patient_name

    card['source'] = {
        "label": entry['resource']['resourceType'],
        "url": entry["fullUrl"]
    }
    card['suggestions'] = [{
        "label": "Human-readalbe label",
        "action":  [entry['resource']['text']]
    }]
    card['links'] = [{
        "label": "Complete patient medical history",
        "type": entry['resource']['meta']
    }]

    return card


@app.route('/cds-services/patient-immunization', methods=['POST'])
def immunize():

    patient_hook = request.json
    headers = {'Authorization': _get_auth_from_hook(
        patient_hook['fhirAuthorization'])}
    url = patient_hook['fhirServer'] + \
        f"/Immunization?patient={patient_hook['context']['patientId']}"
    response = _RESTcall("GET", url, headers=headers).json()
    print(response)
    cards = []
    if response['total']:
        for et in response['entry']:
            cards.append({
                'summary': et['resource']['code']['text'],
                'source': [{'label': et['resource']['resourceType'],
                            'suggestions': [{'label': et['resource']["verificationStatus"]['coding'][0]['code']}],
                            'links': [{'label': et["fullUrl"]}]

                            }]
            })
    return Response(json.dumps({"cards": cards}), 200)


@app.route('/cds-services/patient-allergy', methods=['POST'])
def allergy():

    patient_hook = request.json
    headers = {'Authorization': _get_auth_from_hook(
        patient_hook['fhirAuthorization'])}
    url = patient_hook['fhirServer'] + \
        f"/AllergyIntolerance?patient={patient_hook['context']['patientId']}"
    response = _RESTcall("GET", url, headers=headers).json()
    print(response)
    cards = []
    if response['total']:
        for et in response['entry']:
            cards.append({
                'summary': et['resource']['code']['text'],
                'source': [{'label': et['resource']['resourceType']}],
                'suggestions': [{'label': et['resource']["verificationStatus"]['coding'][0]['code']}],
                'links': [{'label': et["fullUrl"]}]
            })
    return Response(json.dumps({"cards": cards}), 200)


@app.route('/cds-services/patient-documentreference', methods=['POST'])
def documentreference():

    patient_hook = request.json
    headers = {'Authorization': _get_auth_from_hook(
        patient_hook['fhirAuthorization'])}
    url = patient_hook['fhirServer'] + \
        f"/DocumentReference?patient={patient_hook['context']['patientId']}"
    response = _RESTcall("GET", url, headers=headers).json()
    print(response)
    cards = []
    if response['total']:
        for et in response['entry']:
            cards.append({
                'summary': et['resource']['code']['text'],
                'source': [{'label': et['resource']['resourceType']}],
                'suggestions': [{'label': et['resource']["verificationStatus"]['coding'][0]['code']}],
                'links': [{'label': et["fullUrl"]}]
            })
    return Response(json.dumps({"cards": cards}), 200)


def _num_suffix(num):
    suffix = ["th", "st", "nd", "rd"]
    return suffix[num % 10] if num % 10 in [1, 2, 3] and num not in [11, 12, 13] else suffix[0]


def _get_auth_from_hook(fhirAuthorization: dict):
    return fhirAuthorization['token_type'] + ' ' + fhirAuthorization['access_token']


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
