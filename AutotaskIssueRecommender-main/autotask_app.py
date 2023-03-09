# -*- coding: utf-8 -*-
"""autotask_str.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1oz_YP8f4bO-zN7kxG47Gdg4yivmbqaGJ
"""

# Importing library
import pandas as pd
import re
import time
from tqdm import tqdm
import seaborn as sns
import numpy as np
from textblob import TextBlob
import matplotlib.pyplot as plt
from sentence_transformers import SentenceTransformer
import streamlit as st
import os
model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')
from scipy.spatial.distance import cosine
import torch
from numpy.linalg import norm
#device = torch.device("cuda")
device = torch.device("cpu")
model.to(device)

import pickle
# Load the text embeddings from the file
with open(r"./textEmbedding/text_embeddings.pkl", "rb") as f:
    embeddings_dataset = pickle.load(f)


# Pre trained Sentence Transformers
from transformers import AutoTokenizer, AutoModel

model_ckpt = "sentence-transformers/multi-qa-mpnet-base-dot-v1"
tokenizer = AutoTokenizer.from_pretrained(model_ckpt)
model = AutoModel.from_pretrained(model_ckpt)

def autoTaskRec():

    st.set_page_config(
      page_title = "Autotask Similar Issue"
    )

    st.title('Autotask Ticket Recommendation')

    def cls_pooling(model_output):
        return model_output.last_hidden_state[:, 0]

    def get_embeddings(text_list):
      encoded_input = tokenizer(
      text_list, padding=True, truncation=True, return_tensors="pt")
      encoded_input = {k: v.to(device) for k, v in encoded_input.items()}
      model_output = model(**encoded_input)
      return cls_pooling(model_output)



    question = st.text_input("Enter Keyword to find similar issue")




    # Start Button
    if st.button('Start') :
        st.write('Started...')

        question_embedding = get_embeddings([question]).cpu().detach().numpy()
        #print(type(question_embedding))
        scores, samples = embeddings_dataset.get_nearest_examples("embeddings", question_embedding, k=20)

        samples_df = pd.DataFrame.from_dict(samples)
        samples_df["scores"] = scores
        ##st.dataframe(samples_df)
      

        cs = []
        for i in samples_df['embeddings'] :
            cosine = np.dot(question_embedding,i)/(norm(question_embedding)*norm(i))
            cs.append(cosine)
            #distance = cosine(question_embedding, i)
            #cs.append(np.round(1-distance, 3))

        samples_df["Cosine_Score"] = cs
        samples_df.sort_values("Cosine_Score", ascending=False, inplace=True)

        samples_df5 = samples_df.head(5)
        t = [1,2,3,4,5]
        samples_df5['No'] = t

        # Printing top 5 results in the output
        for _, row in samples_df5.iterrows():
            #st.write(f"DESC: {row.Description_re_concate}")
            #st.write(f"FAISS SCORE: {row.scores}")
            st.write(f"**Serial Number** {row.No}")
            st.write(f"**TICKET TITLE:** {row.Ticket_Number}")
            st.write(f"**TITLE:** {row.Ticket_Title}")
            st.write(f"**CONFIDENCE SCORE(%):** {round(row.Cosine_Score[0],2)}")
            st.write("=" * 50)
            print()

            # # Start Button
            #if st.button('View more option') :
                #samples_df_all = sample_df


# -----------------------------------------------------------------------------------
if __name__ == '__AutotaskIssueRecommender__':
    autoTaskRec()