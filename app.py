import streamlit as st
from authentication import Authentication_Info
import json
import pandas as pd
from datetime import datetime
from langchain_groq import ChatGroq
import os
from dotenv import load_dotenv

load_dotenv()

groq_api_key = os.getenv('GROQ_API_KEY')

llm = ChatGroq(model='llama-3.3-70b-versatile',api_key=groq_api_key,verbose=True)

st.set_page_config('Fraud App Detector')

with open('fraud-apps.json','r',encoding='utf-8') as f:
    fraud_apps = json.load(f)

with open('genuine-apps.json','r',encoding='utf-8') as f:
    genuine_apps = json.load(f)

combined_apps = fraud_apps+genuine_apps

fraud_dict = {'app_name':[app.get('appId','N/A') for app in fraud_apps],
              'authenticity':['fraud' for _ in range(len(fraud_apps))]}

genuine_dict = {'app_name':[app.get('appId','N/A') for app in genuine_apps],
              'authenticity':['genuine' for _ in range(len(genuine_apps))]}

fraud_df = pd.DataFrame(fraud_dict)

genuine_df = pd.DataFrame(genuine_dict)

app_authenticity_df = pd.concat([fraud_df,genuine_df])

app_authenticity_df = app_authenticity_df.reset_index().drop(columns=['index'])

st.title('Detect Before Download')

def format_prompt(details,review,app_permission,analysis):
   system_prompt = f'''
      You are an experienced app analyst specializing in evaluating applications from the Google Play Store
      for authenticity and reliability. Your expertise includes identifying fraudulent, suspicious, or genuine
      apps based on various key factors.
      Your task is to analyze a specific Google Play Store application using your extensive knowledge and
      it is also important to consider the following details:

      app_id : {details.get('appId','N/A')}
      app_name : {details.get('title','N/A')}
      description : {details.get('description','N/A')}
      downloads : {details.get('realInstalls','N/A')}
      developer : {details.get('developer','N/A')}
      developerId : {details.get('developerId','N/A')}
      developerEmail : {details.get('developerEmail','N/A')}
      developerWebsite : {details.get('developerWebsite','N/A')}
      developerAddress : {details.get('developerAddress','N/A')}
      average rating : {details.get('score','N/A')}
      ads supported : {details.get('adSupported','N/A')}
      number of updates : {details.get('updated','N/A')}
      current date : {datetime.now().strftime("%d %b %Y")}
      last updated : {details.get('lastUpdatedOn','N/A')}
      app permissions : {app_permission}

      reviews : {[[f"user : {i['userName']} , review : {i['content']}"] for i in review[0]]}

      result from self made analysis regarding data privacy : {analysis}

      ### Instructions ###

      1. If result from self made analysis is suspect then check the app more properly.

      2. Based on your assessment, classify the app as one of the following:
      - genuine
      - fraud

      3. Provide a brief,concise explanation (max 300 characters) on why the app falls into the chosen category.

      4. Make sure the output should be in dictionary format :
      example : "type": "fraud"|"genuine", "reason": "Concise explanation (300 char max)"
      5. Do not provide any other additional details other then the output in dictionary format
   '''

   return system_prompt


app_name = st.text_input(label='provide app name from url',placeholder='com.whatsapp')

if app_name:
    auth = Authentication_Info(app_name)
    details = auth.app_details(country='in')
    if details == False:
        st.warning('No Details Found')
        details = []
    review = auth.user_review(country='in',num_reviews=5)
    if review == False:
        review = []

    app_permissions = auth.app_permission()
    analysis = auth.data_privacy_analysis(auth.data_accountability())

    prompt = format_prompt(details,review,app_permissions,analysis)

    response = llm.invoke(prompt)

    if response:
        response = json.loads(response.content)
        st.success(response)

    if details:
        image_url = details.get('headerImage')
        if image_url:
            st.image(image_url,use_container_width=True)