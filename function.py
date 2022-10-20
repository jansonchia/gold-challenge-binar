import re
from unidecode import unidecode
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

def remove_punct_csv(s):
    s = re.sub(r"\\x[A-Za-z0-9./]+", '', unidecode(s))
    return re.sub(r"[^\w\d\s]+","",s)

def remove_punct_text(s):
    # s = re.sub(r"\\x[A-Za-z0-9./]+", '',unidecode(s))
    s =re.sub(r"[\t|\n|\r]"," ", s)
    return re.sub(r"[^\w\d\s]+","",s)

def remove_multi_space(s):
    return  re.sub(' +', ' ',s)

def remove_stopwords(s):
    df_stopwords = pd.read_csv("E:\Binar\Challenge Gold\stopwordbahasa.csv",names=['kata'])
    list_stopwords = df_stopwords['kata'].to_list()
    s = s.split(" ") # merubah string menjadi list
    s = [x for x in s if x not in list_stopwords] # menghapus kata pada s, jika kata tersebut ada pada list_stopwords
    s = ' '.join(s) # menggabung list menjadi string, dipisah oleh spasi
    return s