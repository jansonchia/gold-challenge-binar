import pandas as pd
from flask import Flask, request,jsonify, render_template
from flasgger import Swagger, LazyString, LazyJSONEncoder,swag_from
from unidecode import unidecode
import re
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
from function import remove_punct_csv,remove_punct_text,remove_multi_space, remove_stopwords
from wordcloud import WordCloud
import timeit


conn = sqlite3.connect ("sqlite3_csv.db")
conn.execute("create table csv (Tweet varchar,HS int,Abusive int,HS_Individual int,HS_Group int,HS_Religion int,HS_Race int,HS_Physical int,HS_Gender int,HS_Other int,HS_Weak int,HS_Moderate int,HS_Strong int);")
conn.close()

conn = sqlite3.connect ("sqlite3_text.db")
conn.execute("create table text (input_text varchar, clean_text varchar);")
conn.close()



app = Flask (__name__)
app.json_encoder =LazyJSONEncoder

swagger_template = dict(
info = {
    'title': LazyString(lambda: 'percobaan membuat api swagger'),
    'version': LazyString(lambda: '1'),
    'description': LazyString(lambda: 'coba-coba'),
    },
    host = LazyString(lambda: request.host)
)

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs/"
}

swagger= Swagger(app, template=swagger_template,config=swagger_config)

@swag_from("swagger_cleansing_text.yml", methods=['POST'])
@app.route("/cleansing_text/v1",methods=["POST"])
def cleansing_text():
    s=request.get_json()
    non_punct = remove_punct_text(s["text"]).lower()
    remove_space = remove_multi_space(non_punct)
    conn = sqlite3.connect ("sqlite3_text.db")
    add='''insert into text (input_text, clean_text) values (?,?);'''
    conn.execute(add,(s["text"],remove_space))
    conn.commit()
    conn.close()
    return jsonify({"Result" : remove_space})

@swag_from("swagger_cleansing_csv.yml", methods=['POST'])
@app.route("/upload_csv/v1",methods=["POST","GET"])
def cleansing_csv():
    f = (request.files.get("file"))
    df= pd.read_csv(f, encoding="latin")
    df_tweet = pd.DataFrame(df)
    sns.heatmap(df_tweet[["HS","Abusive","HS_Individual","HS_Group","HS_Religion","HS_Race","HS_Physical","HS_Gender","HS_Other","HS_Weak","HS_Moderate","HS_Strong"]].corr(),annot=True, fmt=".1f")
    start = timeit.default_timer()
    conn = sqlite3.connect ("sqlite3_csv.db")
    df_tweet.to_sql("csv", con=conn,index=False,if_exists="replace")
    conn.close()
    df_tweet["Tweets"]= df_tweet["Tweet"].replace([r"\\t|\\n|\\r"], " ", regex=True)
    df_tweet["Tweets"]= df_tweet["Tweets"].apply(remove_punct_csv).str.lower()
    df_tweet["Tweets"]= df_tweet["Tweets"].apply(remove_multi_space)
    conn = sqlite3.connect ("sqlite3_csv.db")
    df_tweet.to_sql("csv", con=conn,index=False,if_exists="replace")
    conn.close()
    stop = timeit.default_timer()
    lama_eksekusi = str(stop - start)+ " dtk"
    json = df_tweet["Tweets"].head().to_json()
    df_tweet['Tweets_2'] = df_tweet.Tweets.apply(remove_stopwords) 
    df_hs= df[(df["HS_Weak"]==1)&(df["HS_Individual"]==1)]
    text =" ".join(df_hs["Tweets_2"]) # menggabungkan semua text menjadi 1 string
    wordcloud=WordCloud().generate(text)
    plt.imshow(wordcloud)
    plt.show()
    return jsonify({"Result" : json, "Lama Eksekusi":lama_eksekusi})

if __name__=="__main__":
    app.run(port=1234,debug=True)
