import ruamel.yaml
import sys
import os
from yattag import Doc
import boto3
import urllib.request
from urllib.parse import urlparse

def getTemplateText(file_url):
    try:
        s3 = boto3.resource('s3')
        file_s3_uri = f"s3://{file_url}"
        s3_parse = urlparse(file_s3_uri)
        bucket = s3_parse.netloc
        s3_key = s3_parse.path.lstrip('/')
        s3_obj = s3.Object(bucket, s3_key)
        template_raw_data = s3_obj.get()["Body"].read().decode('utf-8')
        return template_raw_data.strip()
    except:
        return "ERROR"


def lambda_handler(event, context):
    config_file = os.environ.get('ConfigFileLocation')
    config_file_text = getTemplateText(config_file)
    configuration = ruamel.yaml.safe_load(config_file_text)
    print(configuration)
    questions = configuration['Questions'];
    title = configuration['Title'];
    author = configuration['Author'];
    image = configuration['Image'];
    theme = configuration['Theme'];
    
    questionsNames = list()
    for questionIterator in questions:
        questionsNames.append(questionIterator)
    questionsNames.sort()
    
    doc, tag, text = Doc().tagtext()

    with tag('html'):
        with tag('body'):
                            
            doc.stag('br')
            doc.stag('br')
            doc.stag('br')
            
            with tag('div', align='center'):
                with doc.tag('div', style="font-size: medium;font-weight: bold; font-family: verdana; color:#" + str(theme) + ";"): 
                    text(title)
                    doc.stag('br')
                with doc.tag('div', style="font-size: small; font-weight: bold; font-family: verdana;"):
                    text("by " + author)
                    doc.stag('br')
                    doc.stag('img', src=image, width="500")
                    doc.stag('br')
                    doc.stag('br')
            
            with tag('form', action = "submitsurvey", style="margin-left: auto; margin-right: auto; width: 70%;"):
                for questionName in questionsNames:
                    with tag('div'):
                        questionLabel = questions[questionName]['Label']
                        questionType = questions[questionName]['Type']

                        #doc.stag('font', size="4", style="font-weight: bold; font-family: verdana; color:#" + str(theme) + ";")    
                        with doc.tag('div',style="font-size: medium;font-weight: bold; font-family: verdana; color:#" + str(theme) + ";"): 
                            doc.asis(questionLabel)
                            doc.stag('br')
                        
                        if (questionType == "Text"):
                            with doc.textarea(name = questionName, style="width: 100%; border-color: #" + str(theme) + "; " , rows="5"):
                                pass
                            
                        if (questionType == "ShortText"):  
                            with doc.textarea(name = questionName, style="width: 100%; border-color: #" + str(theme) + "; " , rows="1"):
                                pass
                            
                        if (questionType == "Radio"):
                            values = questions[questionName]['Values']
                            for valueIterator in values:
                                value = questions[questionName]['Values'][valueIterator]
                                with doc.tag('div', style="font-size: small; font-weight: normal; font-family: verdana; color:black;"):
                                    doc.input(name = questionName, type = 'radio', value = value, style="border-color: #" + str(theme) + "; ")
                                    text(" "+str(value))
                                    doc.stag('br')
                                
                        if (questionType == "CheckBox"):
                            with tag('fieldset',style="border: 0px; padding: 0px; font-size: small; font-weight: normal; font-family: verdana; color:black;"):
                                values = list(questions[questionName]['Values'])
                                for valueIterator in values:
                                    value = questions[questionName]['Values'][valueIterator]
                                    field_name = questionName + "_" + "".join([ c if c.isalnum() else "_" for c in value.lower() ])
                                    doc.input(name = field_name, type = 'hidden', value = "0",style="border-color: #" + str(theme) + "; ")
                                    doc.input(name = field_name, id = field_name ,  type = 'checkbox', value = "1", style="border-color: #" + str(theme) + "; ")
                                    text(" "+str(value))
                                    doc.stag('br')
                            
                        doc.stag('br')
                        doc.stag('br')
    
                doc.stag('input', type = "submit", value = "Send!", style="background-color: #" + str(theme) + "; border: none; color: white; float: right; padding: 15px 32px; text-align: center; text-decoration: none; display: inline-block; font-size: 16px; margin: 4px 2px; cursor: pointer;")




    htmlResult = doc.getvalue()

    return {
            'statusCode': "200",
            'body': htmlResult,
            'headers': {
                'Content-Type': 'text/html',
            }
        }


if __name__ == '__main__':
    print(sys.argv[1])
    os.environ['ConfigFileLocation'] = sys.argv[1]
    lambda_handler(None, None)