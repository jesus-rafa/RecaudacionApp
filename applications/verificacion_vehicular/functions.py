from datetime import date, datetime
import xmltodict
import requests
import json
import ast

def get_data_vehiculo(self, rfc, opcion):

    url = "http://172.31.113.187:180/Informacion_Contribuyente.asmx"
    headers = {
        'Content-Type': 'text/xml',
        'SOAPAction': 'http://tempuri.org/Obtiene_Informacion'
    }
    xml = "<?xml version=\"1.0\" encoding=\"utf-8\"?>\r\n<soap:Envelope xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xmlns:xsd=\"http://www.w3.org/2001/XMLSchema\" xmlns:soap=\"http://schemas.xmlsoap.org/soap/envelope/\">\r\n    <soap:Body>\r\n        <Obtiene_Informacion xmlns=\"http://tempuri.org/\">\r\n            <rfc>"+str(rfc)+"</rfc>\r\n            <opcion>"+str(opcion)+"</opcion>\r\n        </Obtiene_Informacion>\r\n    </soap:Body>\r\n</soap:Envelope>"

    response = requests.post(url, headers=headers, data=xml)
    dictionary = xmltodict.parse(response.text)

    for key, value in dictionary.items():
        for key2, value2 in value.items():
            if key2 == 'soap:Body':
                for key3, value3 in value2.items():
                    if key3 == 'Obtiene_InformacionResponse':
                        for key4, value4 in value3.items():
                            if key4 == 'Obtiene_InformacionResult':
                                result = json.loads(value4)

    return result['Table']