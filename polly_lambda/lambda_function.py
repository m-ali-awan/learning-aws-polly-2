import boto3
#from textblob import TextBlob
import nltk
nltk.data.path.append("/var/task/nltk_data")
import os
import urllib.parse
from contextlib import closing
from pyssml.AmazonSpeech import AmazonSpeech

polly = boto3.client('polly')
s3 = boto3.resource('s3')

def lambda_handler(event, context):
    output = os.environ['output']
    supported_languages = os.environ['supported_languages'].split(',')
    default_language = os.environ['default_language']
    polly_bucket = os.environ['polly_bucket']

    s3_bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')

    try:
        whole_filename, file_extension = os.path.splitext(key)
        filename = whole_filename.split("/")[-1]
        text = str(s3.Object(s3_bucket, key).get()['Body'].read(), 'utf-8')
        # Get the language file_name.lang.md or file_name.md
        language = filename.split(".")[-1]
        voice_language = language if language in supported_languages else default_language

        voice_id = os.environ[voice_language]

        polly_title = "{}.{}".format(filename, output)

        parts = split_text(text, 3000)
        for part in parts:
            part = add_ssml(part)
            response = polly.synthesize_speech(
                OutputFormat=output,
                Text=part,
                TextType='ssml',
                VoiceId=voice_id
            )
            print(part)

            if "AudioStream" in response:
                with closing(response['AudioStream']) as stream:
                    output_title = os.path.join("/tmp", polly_title)
                    with open(output_title, "ab") as f:
                        f.write(stream.read())

        s3.Object(polly_bucket, polly_title).upload_file(os.path.join("/tmp", polly_title),ExtraArgs={'ACL':'public-read'})
    
    except Exception as e:
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function'.format(key, s3_bucket))
        raise e

def split_text(text, max_length):
    # Needs whitespace to avoid Polly saying punctuation mark e.g. "dot"
    parsed_text = [str(sentence) + " " for sentence in TextBlob(text).sentences]

    joined_sentences = []
    joined_sentence = ""
    for sentence in parsed_text:
        if len(sentence) + len(joined_sentence) < max_length:
            joined_sentence += sentence
        else:
            joined_sentences.append(joined_sentence)
            joined_sentence = sentence
    if not any(joined_sentence in js for js in joined_sentences):
        joined_sentences.append(joined_sentence)
    return joined_sentences

def add_ssml(part):
    s = AmazonSpeech()
    s.prosody({'rate':'fast', 'pitch': 'low'}, part)
    return s.ssml()


