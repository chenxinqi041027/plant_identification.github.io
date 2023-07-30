import base64
import os
import requests
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
from st_aggrid import AgGrid, GridOptionsBuilder, JsCode

st.set_page_config(page_title="Streamlit植物识别", page_icon=" ", layout="wide")

def draw_table(df, theme, table_height):
    columns = df.columns
    thead1="""<thead><th scope="col"></th>"""
    thead_temp = []
    for k in range(len(list(columns))):
        thead_temp.append("""<th scope="col" class="text-white">"""+str(list(columns)[k])+"""</th>""")
    header = thead1+"".join(thead_temp)+"""</tr></thead>"""
    rows = []
    rows_temp = []
    for i in range(df.shape[0]):
        rows.append("""<th scope="row">"""+str(i+1)+"""</th>""")
        rows_temp.append(df.iloc[i].values.tolist())
    td_temp = []
    for j in range(len(rows_temp)):
        for m in range(len(rows_temp[j])):
            td_temp.append("""<td class="text-white">"""+str(rows_temp[j][m])+"""</td>""")
    td_temp2 = []
    for n in range(len(td_temp)):
        td_temp2.append(td_temp[n:n+df.shape[1]])
    td_temp3 = []
    for x in range(len(td_temp2)):
        if int(x % (df.shape[1])) == 0:
            td_temp3.append(td_temp2[x])
    td_temp4 = []
    for y in range(len(td_temp3)):
        td_temp4.append("".join(td_temp3[y]))
    td_temp5 = []
    for v in range(len(td_temp4)):
        td_temp5.append("""<tr><th scope="row" class="text-white" style="height: 100px;">"""+str(v+1)+"""</th>"""+str(td_temp4[v])+"""</tr>""")
    table_html = """<link href="https://unpkg.zhimg.com/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-1BmE4kWBq78iYhFldvKuhfTAU6auU8tT94WrHftjDbrCEXSU1oBoqyl2QvZ6jIW3" crossorigin="anonymous">"""+\
    """<script src="https://unpkg.zhimg.com/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-ka7Sk0Gln4gmtz2MlQnikT1wXgYsOg+OMhuP+IlRH9sENBO0LRn5q+8nbTov4+1p" crossorigin="anonymous"></script>"""+\
    """<div class="table-responsive"><table class="table text-center table-bordered """+str(theme)+'"'+">""" + \
    header+"""<tbody>"""+"".join(td_temp5)+"""</tbody></table></div>"""

    return components.html(table_html,height=table_height, scrolling=True)

def baidu_zhiwushibie(target):
    # client_id 为官网获取的AK， client_secret 为官网获取的SK
    client_id = "6ou8xEIFrds3A3dGjgZDrfbW"
    client_secret = "mBlTFKcmKp8bPLm6NxyELhMS2um3OLXd"

    token_url = "https://aip.baidubce.com/oauth/2.0/token"
    host = f"{token_url}?grant_type=client_credentials&client_id={client_id}&client_secret={client_secret}"

    response = requests.get(host)
    access_token = response.json().get("access_token")

    request_url = "https://aip.baidubce.com/rest/2.0/image-classify/v1/plant"
    image = base64.b64encode(target)

    body = {
        "image": image,
        "baike_num": 10
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    request_url = f"{request_url}?access_token={access_token}"
    response = requests.post(request_url, headers=headers, data=body)
    content = response.content.decode("UTF-8")

    if len(json.loads(content)["result"])>=1:
        try:
            df1 = pd.DataFrame.from_dict(json.loads(content)["result"], orient="columns", dtype = None, columns = None)
            df2 = df1['baike_info'].apply(pd.Series)
            df_final = pd.concat([df1, df2], axis = 1).drop('baike_info', axis = 1)
            df_final.columns = ["置信度", "名称", "百科链接", "百科图片链接", "描述"]
            df_final["置信度"] = df_final["置信度"].apply(lambda x: format(x, '.2%'))
            cols = ["置信度", "名称", "描述", "百科链接", "百科图片链接"]
            df_final = df_final[cols]
            st.sidebar.title("识别结果："+df_final.at[0, "名称"])
            st.sidebar.image(file, use_column_width=True)
            draw_table(df_final.iloc[[0]], "bg-info", 600)
        except ValueError:
            df = pd.DataFrame.from_dict(json.loads(content)["result"], orient="columns", dtype=None, columns=None)
            df.columns = ["置信度", "名称", "百科信息"]
            df["置信度"] = df["置信度"].apply(lambda x: format(x, '.2%'))
            st.sidebar.title("识别结果："+df.at[0, "名称"])
            st.sidebar.image(file, use_column_width=True)
            draw_table(df.iloc[[0]], "bg-info", 600)
    else:
        st.error("对不起，识别失败，请更换要识别的植物图片！")

file = st.file_uploader("请上传要识别的图片", type=["jpg", "png", "jpeg"])
if file is not None:
    baidu_zhiwushibie(file.read())