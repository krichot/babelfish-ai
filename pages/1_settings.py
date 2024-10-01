import streamlit as st
import os
import tomli

# get the config form file
with open(".streamlit/settings.toml", "rb") as f:
    settings = tomli.load(f)

st.set_page_config(
    page_title="Babelfish AI Settings",
    layout="wide")

st.write("# settings")

VERSION = settings['general']['version']
MODEL = settings['model']['name']

st.write (f'Model: {MODEL}')
st.write (f'Version: {VERSION}')