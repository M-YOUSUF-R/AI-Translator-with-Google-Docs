import os.path
from PIL import Image
import urllib.request as r
import json
#################################################### 
# header file for google docs api                  #
####################################################
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


# If modifying these scopes, delete the file token.json.


#####################################################################################
# function to initialize the google docs with the                                   #
# SCOPES ["https://www.googleapis.com/auth/documents"](given in google docs api)    #
# DOCUEMNT_ID (https://docs.google.com/document/d/DOCUMENT_ID/edit?tab=t.TAB_ID)    #
#####################################################################################

def InitializeDoc(SCOPES:list , DOCUMENT_ID:str,clien_credential:str,token_json:str):
  """Shows basic usage of the Docs API.
  Prints the title of a sample document.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists(token_json):
    creds = Credentials.from_authorized_user_file(token_json, SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          clien_credential, SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(token_json, "w") as token:
      token.write(creds.to_json())

  try:
    service = build("docs", "v1", credentials=creds)

    # Retrieve the documents contents from the Docs service.
    document = service.documents().get(documentId=DOCUMENT_ID).execute()
    return service, document
  except HttpError as err:
    print(err)

###############################
# to create a new document    #
###############################

def createDocument(title:str,SCOPES:list,DOCUMENT_ID:str,client_credential:str,token_name:str):
  service , document = InitializeDoc(SCOPES,DOCUMENT_ID,client_credential,token_name);
  title = title
  body = {
    'title':title
  }
  doc = service.documents() \
    .create(body=body).execute();
  print('created document with title: {0}'.format(
    doc.get('title')
  ))

###########################
# inserting text (append) #
###########################

def insertText(SCOPES:list , DOCUMENT_ID:str,text:str ,client_credential:str,token_name:str ,endline:bool = False):
  service ,document = InitializeDoc(SCOPES,DOCUMENT_ID,client_credential,token_name);
  end_index = document.get('body').get('content')[-1]['endIndex'];
  if(endline):
    text += '\n'
  
  request = [
    {
      'insertText':{
        'location':{
          'index': end_index -1  ,
        },
        'text': text
      }
    }
  ]
  try:
    result = service.documents().batchUpdate(
      documentId=DOCUMENT_ID,body={'requests':request}
    ).execute();
  except Exception as  e:
    print(e);

###################################################
# function to insert image                        #
# image must be a http// request and less then 2k #
# ----this function need more development----     #
###################################################

def inserImage(imageUrl:str):
  r.urlretrieve(imageUrl,'image.png')
  image = Image.open('image.png');
  service ,document = InitializeDoc(SCOPES,DOCUMENT_ID);
  end_index = document.get('body').get('content')[-1]['endIndex'];
  requests = [{
    'insertInlineImage':{
      'location': {
        'index': end_index
      },
      'uri': imageUrl,
      'objectSize': {
        'height':{
          'magnitude' : image.size[1] * 0.75,  
          'unit':'PT'
        },
        'width': {
          'magnitude': image.size[0] * 0.75,
          'unit':'PT'
        }
      }
    }
  }]
  #execute the request
  try:
    body = {'requests': requests}
    response = service.documents().batchUpdate(
      documentId=DOCUMENT_ID , body=body
    ).execute()
    os.remove('image.png')
  except Exception as e:
    print(e)
      
################################    
#    read text for the docs    #
################################

def readText(SCOPES:list,DOCUMENT_ID:str,client_credential,token_name:str,slice:str=None):
  service , document = InitializeDoc(SCOPES,DOCUMENT_ID,client_credential,token_name);
  text:str =""; 
  result = service.documents().get(documentId=DOCUMENT_ID).execute()
  if 'body' in result and 'content' in result['body']:
    for element in result['body']['content']:
      if 'paragraph' in element:
        text += (element['paragraph']['elements'][0]['textRun']['content']) 
  if(slice != None ):
    textList = text.split(slice)
    finalList:list = [];
    for para in textList:
      para = para.replace('\x0b','')
      finalList.append(para)
    textList = []
    return finalList[1:]
  else:
    return text
############################################################################
"""
      elif 'table' in element:
        table = element.get('table')
        if table and 'tableRows' in table:
          for row in table['tableRows']:
            cells = row.get('tableCells',[])
            row_text = []
            for cell in cells:
              cell_content = "".join([
                run.get('content','')
                for struct_elem in cell.get('content',[])
                for paragraph in [struct_elem.get('paragraph',{})]
                for run in paragraph.get('elements',[])
                if 'textRun' in run
              ])
              row_text.append(cell_content.strip())
        return " | ".join(row_text)
"""
###########################################################################
############################
#     delete text          #
############################
def deleteText(index_range:list,SCOPES,DOCUMENT_ID,client_credential:str,token_name:str):
  service ,document = InitializeDoc(SCOPES,DOCUMENT_ID,client_credential,token_name);
  request = [
    {
      'deleteContentRange':{
        'range':{
          'startIndex':index_range[0],
          'endIndex': index_range[1],
        }
      }
    },
  ]
  try:
    result = service.documents().batchUpdate(
      documentId=DOCUMENT_ID, body={'requests': request}
    ).execute()
  except Exception as e:
    print('error:');
    print(e);

def deleteALLText(SCOPES,DOCUMENT_ID,clien_credential:str,token_name:str):
  service ,document = InitializeDoc(SCOPES,DOCUMENT_ID,clien_credential,token_name);
  
  try:
      start_index = document.get('body').get('content')[1]['startIndex'];
      end_index = document.get('body').get('content')[-1]['endIndex'];
  
      request = [
        {
          'deleteContentRange': {
              'range': {
                'startIndex':start_index,
                'endIndex': end_index -1,
              }
          }
        },
      ]

      result = service.documents().batchUpdate(
        documentId=DOCUMENT_ID, body={'requests': request}
      ).execute()
      
  except Exception as e:
    print('deletion issue:');
    print(e);

# SCOPES = ["https://www.googleapis.com/auth/documents"]

# DOCUMENT_ID = "1Qr8OT6HR-euowQsiIrqI4wWaAtwOzNnWMfYLad37l0w"