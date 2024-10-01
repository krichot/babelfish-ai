import streamlit as st
import tomli

with open('.streamlit/settings.toml', mode='rb') as fp:
    settings = tomli.load(fp)

st.set_page_config(
    page_title="Babelfish AI Settings",
    layout="wide")

st.write("# settings")
st.write(settings)

MODEL = "gemini-1.5-flash"
#VERSION = settings["general"]["version"]
VERSION = "0.1"

st.write (f'Model: {MODEL}')
st.write (f'Version: {VERSION}')