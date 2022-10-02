import streamlit as st
import requests
import pandas as pd
#import numpy as np

#nltk initializers
# from nltk.sentiment import SentimentIntensityAnalyzer
# sia = SentimentIntensityAnalyzer()

# import gensim
# from gensim.utils import simple_preprocess
# from gensim.parsing.preprocessing import STOPWORDS
# from nltk.stem import WordNetLemmatizer, SnowballStemmer
# from nltk.stem.porter import *

# np.random.seed(2018)
# import nltk
# nltk.download('wordnet')

# import spacy
# import en_core_web_sm
# nlp = en_core_web_sm.load()
import texthero as hero
from texthero import preprocessing

st.set_page_config(
    page_title="Preservers of Knowledge",
    page_icon="🤖",
    layout = "wide",
    # layout="wide",
    initial_sidebar_state="expanded",
)

st.title('NASA space app challenge')

sidebar = st.sidebar.radio('App Navigation', ['General Info','Project Demo'])

if sidebar=='General Info':
    st.header('General Info')
if sidebar=='Project Demo':
    st.header('Project Minerva')
    df = pd.DataFrame()
    topic=st.text_input('Search Abstract',value="space station")
    response = requests.get("https://ntrs.nasa.gov/api/openapi/")
    parameters={#"abstract":"acid",
           "abstract":topic
           }
    response = requests.get("https://ntrs.nasa.gov/api/citations/search", params=parameters)
    x=response.json()
    
    for y in range(len(x['results'])):
        title = str(x['results'][y]['title'])
        abstract = str(x['results'][y]['abstract'])
        subject_category = str(x['results'][y]['subjectCategories'])
        downloadble = str(x['results'][0]['downloadsAvailable'])
        new_row = {'Title':title,'Abstract':abstract,'subject_category':subject_category,'is_downloadable':downloadble}
        df = df.append(new_row, ignore_index=True)
        
    #cleaning
    category_custom_pipeline = [preprocessing.remove_punctuation,
                                preprocessing.lowercase,
                                preprocessing.remove_whitespace
                               ]
    df['subject_category'] = hero.clean(df['subject_category'], category_custom_pipeline)
    
    custom_pipeline = [preprocessing.remove_stopwords,
                       preprocessing.remove_punctuation,
                       preprocessing.fillna,
                       preprocessing.lowercase,
                       preprocessing.remove_whitespace]
    df['Abstract'] = hero.clean(df['Abstract'], custom_pipeline)
    
    st.dataframe(df)
    
    narrow_by_category = pd.DataFrame()

    category_list = pd.Series(df['subject_category'].unique())
    st.subheader('Filter by subject category')
    options = st.multiselect('Choose narrowed subject category',category_list,default=category_list[0])
    
    if options:
        for x in range(len(options)):
            narrow_by = df[df['subject_category']==options[x]]
            narrow_by_category = narrow_by_category.append(narrow_by)
        
    st.dataframe(narrow_by_category)
    
    st.subheader('Filter by named entities')
    
    col1, col2 = st.columns([3,2])
    options_named_entities = col1.selectbox('choose named_entities in abstract',['PERSON', 'NORP', 'FAC', 'ORG','GPE','LOC','PRODUCT','EVENT','WORK_OF_ART','LAW','LANGUAGE','DATE','TIME','PERCENT','MONEY','QUANTITY','ORDINAL','CARDINAL'])
    
    
    
#    st.dataframe(narrow_by_category['abstract'])
    narrow_by_category['abstract_entities'] = hero.named_entities(narrow_by_category['Abstract'])
    
    
    narrow_by_entities= pd.DataFrame()

    for x in range(len(narrow_by_category['abstract_entities'])):
        try:
            data = [item for item in narrow_by_category['abstract_entities'][x] if options_named_entities in item]
            dataformat = pd.DataFrame(data, columns=['Name', 'Label', 'starting character','ending character'])
            dataformat['index']=x
            narrow_by_entities = narrow_by_entities.append(dataformat)
        except KeyError:
            continue

    narrow_by_entities=narrow_by_entities[['index','Name','Label']]
    col1.dataframe(narrow_by_entities)
    
    col2.write('''<p>List of labels:</p>
               <ul>
               <li>PERSON: People, including fictional.</li>
               <li>NORP: Nationalities or religious or political groups.</li>
               <li>FAC: Buildings, airports, highways, bridges, etc.</li>
               <li>ORG : Companies, agencies, institutions, etc.</li>
               <li>GPE: Countries, cities, states.</li>
               <li>LOC: Non-GPE locations, mountain ranges, bodies of water.</li>
               <li>PRODUCT: Objects, vehicles, foods, etc. (Not services.)</li>
               <li>EVENT: Named hurricanes, battles, wars, sports events, etc.</li>
               <li>WORK_OF_ART: Titles of books, songs, etc.</li>
               <li>LAW: Named documents made into laws.</li>
               <li>LANGUAGE: Any named language.</li>
               <li>DATE: Absolute or relative dates or periods.</li>
               <li>TIME: Times smaller than a day.</li>
               <li>PERCENT: Percentage, including ”%“.</li>
               <li>MONEY: Monetary values, including unit.</li>
               <li>QUANTITY: Measurements, as of weight or distance.</li>
               <li>ORDINAL: “first”, “second”, etc.</li>
               <li>CARDINAL: Numerals that do not fall under another type.</li>
               </ul>
               ''',unsafe_allow_html=True)
    
    #visualization
    wordcloudfig = hero.wordcloud(df['Abstract'])
    st.set_option('deprecation.showPyplotGlobalUse', False)
    col1, col2 = st.columns([3,1])
    col1.subheader('Word Cloud')
    col1.pyplot(wordcloudfig)
    col2.subheader('Top Words')
    col2.dataframe(hero.top_words(df['Abstract']))