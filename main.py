from google import genai as ai
from dotenv import load_dotenv
from docsApi import readText,insertText,deleteALLText
import msvcrt as ms
load_dotenv();


import os


prompt = "As a professional translator, analyze the following text to understand its meaning, context, and intent. Then, translate it into fluent and natural English, using appropriate vocabulary and phrasing,translate the text and think internally to understand its meaning, context and intent.Only translate the text that is under the 'input:' label and do not translate the text that is under or with the 'output:' label.After translation, output the entire text in the following format:'output:\n[translated English text]'.Do not output any analysis, explanation. the text is: \n";

#####################################################################################
# SCOPES ["https://www.googleapis.com/auth/documents"](given in google docs api)    #
# DOCUEMNT_ID (https://docs.google.com/document/d/DOCUMENT_ID/edit?tab=t.TAB_ID)    #
#####################################################################################

SCOPES = ["https://www.googleapis.com/auth/documents"]

DOCUMENT_ID = os.getenv("DOCUMENT_ID");
token1 = "tokens/token.json"
c1 = "credentials/credentials.json";
RESULT_DOCUMENT_ID = os.getenv("RESULT_DOCUMENT_ID")
c2 = "credentials/credentials2.json";
token2 = "tokens/token2.json"


######################################################
# this is the part of google generative ai           #
# this part is responsible for generating translaion #
###################################################### 

def aiTranslator(SCOPES,DOCUEMNT_ID):
    client =  ai.Client(api_key=os.getenv('API_KEY'));

    userInput = '';
    fileInput:list = readText(SCOPES,DOCUMENT_ID,c1,token1,'INPUT:');
    print(fileInput)
    prevFileInput:list = [];
    i:int = 0;
    # deleteALLText(SCOPES,DOCUEMNT_ID,c1,token1);
    print('translating the text...')
    try:
        while(userInput != '/exit' and i < len(fileInput)):
            
            content = prompt + fileInput[i];
            # print(content)
            response = client.models.generate_content(
                model="gemini-2.0-flash", 
                contents= content
            );
            # print(response.text)
            prevFileInput.append(fileInput[i])
            insertText(SCOPES,RESULT_DOCUMENT_ID,response.text,c2,token2,True);
            i += 1
            if prevFileInput == fileInput:
                print("all text are translated.")
                break;
            print('to exit press "ESC" key')
            if ms.kbhit():
                if(ms.getch() == '\x1b'):
                    break;
        else:
            if(userInput):
                print('exit,due to user pressed: ',userInput)
            else:
                print('user exited.');
    except Exception as e:
        print('the issue is: ',e);
if __name__ == '__main__':
    aiTranslator(SCOPES=SCOPES,DOCUEMNT_ID=DOCUMENT_ID)