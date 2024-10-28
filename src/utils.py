import streamlit as st
import requests as rqs
import pandas as pd

@st.cache_data(show_spinner="Carregando Estoque...")
def call_estoque():
    estq = rqs.get(st.secrets["estoque_url"])
    return estq

@st.cache_data(show_spinner="Carregando Devices...")
def call_device():
    devc = rqs.get(st.secrets["device_url"])
    return devc

@st.cache_data(show_spinner="Carregando Hardwares...")
def call_hw():
    hw = rqs.get(st.secrets["hardware_url"])
    return hw

@st.cache_data(show_spinner="Carregando Trocas...")
def call_exchange():
    exch = rqs.get(st.secrets["exchange_url"])
    return exch


def value_to_hex_color_g2r(value, max_value):
    if value < 0 or max_value <= 0 or value > max_value:
        raise ValueError("Value must be between 0 and max_value.")

    # Calculate the ratio of the value to the max value
    ratio = value / max_value

    # Calculate RGB values
    red = int(255 * ratio)  # red increases as the value increases
    green = int(255 * (1 - ratio))  # green decreases as the value increases

    # Construct the hex color
    hex_color = f'#{red:02X}{green:02X}00'
    return hex_color

def value_to_hex_color_r2g(value, max_value):
    if value < 0 or max_value <= 0 or value > max_value:
        raise ValueError("Value must be between 0 and max_value.")

    # Calculate the ratio of the value to the max value
    ratio = value / max_value

    # Calculate RGB values
    red = int(255 * ratio)  # red increases as the value increases
    green = int(255 * (1 - ratio))  # green decreases as the value increases

    # Construct the hex color
    hex_color = f'#{green:02X}{red:02X}00'
    return hex_color

def translate_clients(series):
    translation_dict = {
        "6dcd40b3-c23a-489a-8f29-8bd77e7ea85d": "BRF",
        "746bff17-0804-4e36-b5d9-3a1e93615683": "ELKS Engenharia Florestal e Ambiental Ltda",
        "46d5a92c-ea8b-4b9d-b925-1e0e5f67bbd8": "Bracell São Paulo",
        "c7a9b347-079c-47d1-88f4-880b501e0a27": "WorldTree",
        "e37e93b1-b0a3-4500-a422-4db41dd0f703": "Suzano Inventário",
        "96345ac4-e5f2-4ba4-a372-6c3058176683": "SLB",
        "373006c1-b1ed-4455-96b3-faa387a76eb7": "CLIENTE TREINAMENTO",
        "0e139182-273d-4de0-b71b-c4188f31e743": "Treevia Consultoria",
        "277ca40f-80ae-4876-b7ca-e9d580b025b7": "Klabin",
        "69d460cd-0654-48c6-b609-467f745f6e53": "Saint-Gobain",
        "d98a3d44-d1e8-4292-a729-05e8e6f87738": "Melhoramentos Florestal",
        "4470c6eb-f273-4e01-939e-a8807a21e21d": "Agencia Florestal Ltda",
        "b45b681d-c584-4e58-91f2-e281cc393873": "CMPC",
        "af61d1ab-b4e8-44dc-b4f8-c5b07a966b9d": "Bracell Bahia Florestal",
        "2a9da92e-063e-4368-8325-1bbf46e41c15": "Marques_Pro",
        "ab3381d6-928e-47bf-b7cc-77e2bd293d91": "Simasul Siderurgia",
        "2e5690d2-73e8-468c-bbd1-156e5f328aef": "Desafio Cabruca",
        "acf7e056-63e3-4d46-b451-565e93cbb759": "Placas do Brasil S.A",
        "bf015979-9977-4ce7-b133-f1e5b0befbff": "UNESP",
        "78574165-06f7-453d-83d4-8cfece7db5f7": "TRC",
        "7f7b5f04-4fab-456c-8727-aa2bd325af74": "Projeto UFT",
        "1a213600-2ce8-4172-b0e9-0f8e32f1bc35": "High Precision",
        "9d7bdab2-26e5-4417-8785-328b3603515a": "Gaia Agroflorestal",
        "f6012de6-551a-4d05-9adc-01c1464c5179": "QA - Ambiente de Testes",
        "09fbfe53-cb1a-42db-913b-b7b1cd1463f2": "Treevia Forest Technologies",
        "9ca3e49b-33f1-4743-aa99-102c5cdc0990": "Corus Agroflorestal",
        "e9c82444-80f3-4dc1-ad21-1604d59c8fd2": "Teste Veracel",
        "8f188098-3733-40cc-b0e9-7a92f88c5b69": "Forte Florestal",
        "f4fb566c-86a7-4a49-b966-0ce9bab212c9": "Veracel",
        "30da811d-4b39-4459-9256-b51ecf182d00": "Radix",
        "939020db-4b7d-4ff8-9663-f6ff8d90ca85": "demo_treevia",
        "c8e7bf99-c20f-404e-a8d1-0a3f537c7137": "Grupo Mutum",
        "8545d8be-5414-4d4b-a3f1-810e20305c0f": "Treevia - Equipe de Quality Analyst",
        "28fba4a9-84f6-441b-ae1c-24e33acb0585": "Bracell",
        "15b79a01-be2f-4a60-8441-31af61a2a7f0": "Remasa",
        "1a951671-b390-4959-a2bc-79f87efe3e81": "G2 Forest",
        "cb86084a-c5c9-432f-8f38-5b9e9b2eb2c7": "Inventec",
        "cfd0f913-0f40-49a0-ae13-1ac9f33c838e": "KLINGELE PAPER NOVA CAMPINA LTDA",
        "02cafdfc-5682-43a5-895a-3f64b4183d7f": "R.S FLORESTAL LTDA",
        "9f6b7729-83ac-4d7f-b30f-852725eb1bbc": "Trial 2a Rotação",
        "4b2431f1-9489-4a4a-aaaa-053e57ef81b5": "NORFLOR EMPREENDIMENTOS AGRÍCOLAS S/A",
        "3cebf34a-d618-43f1-8202-363b5d4b15c6": "GELF SIDERURGIA S/A",
        "92c9d66a-2a80-4a06-8234-7d94b35b577c": "ALJIBES AZULES S.A",
        "8730bc85-cdd0-4c7b-9750-1784c42a9072": "Trail",
        "70ed1b2b-3427-42ca-9085-4af19bb4a0b9": "SFDEMO2",
        "a78e6533-0123-4cd7-af21-9d5cdd738b95": "PARCEL REFLORESTADORA LDTA",
        "8c2dacf8-6c29-4125-9af2-2e18c3a7d5db": "TTG Brasil Investimentos Florestais Ltda.",
        "dacd1e78-d096-46f8-acad-9b16a9d91029": "Suzano Papel e Celulose",
        "e310e73b-4207-4db1-a36c-9dcdb3af5615": "Smart Forest Demo 2",
        "4e7fbf74-ed7f-44b6-b37c-f26b56328f6b": "High Precision Demo",
        "4786c8ce-909a-4e22-a589-e969b8fafc6e": "3A Composites",
        "4d7a221b-de2d-4f68-92b0-cf8a20d299ea": "Laminados AB",
        "b48deec6-b90c-4b59-840d-7b6006f7e3cb": "Projeto NANORAD'S",
        "2d204924-b51a-48ef-a586-4c1ac3e82c6f": "Floresta Assesoria e Planejamento Florestal LTDA",
        "abd4fcd3-0ac5-4db5-991a-c510d2f4694b": "Farol Consultoria Agroflorestal",
        "e99ed730-7d69-4296-9bb0-8cdee25b6a07": "Madeireira Rio Claro",
        "62dd6613-de30-4b02-b5ab-d7e859ac6ffa": "LIF - Land Inovation Fund",
        "d8ee6d1f-b58f-4aaa-8fe3-f5295f2c9010": "Taboão Reflorestamento SA",
        "9e68ca90-071b-4be5-a915-84e0052a5335": "Colpar Participações",
        "c0c8de9a-b688-4978-b769-dce557fb5549": "Agrobusiness Floresta e Pecuária",
        "a00f23a2-889e-4bce-8195-9faebdf77c4c": "Cenibra",
        "60a60b2a-9d9d-4297-bc67-e11919c694d3": "Unesp - Acadêmico",
        "423b4aa4-62cd-4828-a9bd-060303fdd44e": "Google_PlayStore",
        "c877a8f4-05c7-4d81-83d7-b6dd0b194552": "Topo_Floresta",
        "7b4c12f7-c6c3-4c98-be8c-83fe01c9e3fc": "MANTENA FLORESTAL S.A.",
        "caca3c79-2f2b-4e52-a1b0-82ca7a62e375": "FoxFlorestal",
        "67baca90-69ef-4ada-8e94-8531378baf59": "Treevia - Equipe de Desenvolvimento",
        "a2c52ad2-0414-4345-804c-2fa13689a873": "Vallourec",
        "e4baaa62-9d39-43e9-804c-ad0a1a5f3196": "Eldorado Brasil Celulose S/A",
        "0265e5a7-a880-45f4-bb65-f8c5908317dd": "Eldorado Máxima Produtividade",
        "530f8684-c252-405c-a822-6d22f8b783b0": "Atenil S.A.",
        "b7df7a81-4ac3-4930-9c9a-126942902d79": "Teste Front 2.0 - Apagar EAGG",
        "cb56144f-a250-4c94-b9c6-1285cd95f526": "Test_Front 2.0",
        "3a048cc4-07d9-4530-b8cd-6aa0b26912ee": "Treevia - Equipe de Data Analisys",
        "5590a633-3eda-464b-8f6a-2d67ca4b817d": "Norflor Prognose Apresentacao",
        "d519800f-4b51-40e6-bec4-29e6a17c6803": "Thalis",
        "51274c90-3c59-41c7-ad1e-85c6c25d7a2f": "Smart Forest Demo",
        "30dc1cd7-7aaf-45f2-a999-347307d03b7a": "Aldeir Testes Corporation",
        "f38c52fe-3a75-49b0-9a0b-878f054c71b2": "Brafor Projetos Ambientais Ltda",
        "e2016e43-be78-49c1-bf47-6fdab59322f1": " Eldorado Inventario Tradicional",
        "7332948d-62e3-48fb-a43f-e71af7e426f5": "Minasligas",
        "8f6192e6-4263-42b2-9132-fbb0f633a538": "PONTUAL BIOENERGIA LTDA",
        "3af99273-f930-4bcf-b19a-22a01b93af61": "Teste IFQ",
        "e05d9fa9-2607-4a96-a1aa-fc171ea5407d": "The Nature Conservancy",
        "d1c32f51-a552-4017-b0e9-570218570786": "Treevia Academy",
        "None": "Estoque"
    }

    return series.replace(translation_dict)

def check_series_match(series1, series2):
    return series1.isin(series2).all()

def update_or_add_rows(csv_file, key_column, update_data):
    """
    Updates rows in a DataFrame based on a key column or adds new rows if no match is found.

    Parameters:
    csv_file (str): Path to the CSV file.
    key_column (str): The column to match on.
    update_data (pd.DataFrame): A DataFrame containing the columns and their new values.

    Returns:
    pd.DataFrame: The updated DataFrame.
    """
    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_file)

    # Check if the key_column exists in the DataFrame
    if key_column not in df.columns:
        raise ValueError(f"{key_column} not found in the DataFrame.")
    
    # List to hold rows to be added
    rows_to_add = []

    # Iterate over each row in the update_data DataFrame
    for _, row in update_data.iterrows():
        key_value = row[key_column]
        
        # Update the row if the key exists
        if key_value in df[key_column].values:
            df.loc[df[key_column] == key_value, row.index] = row.values
        else:
            # If key doesn't exist, prepare to add a new row
            rows_to_add.append(row)

    # If there are rows to add, concatenate them to the original DataFrame
    if rows_to_add:
        new_rows_df = pd.DataFrame(rows_to_add)
        df = pd.concat([df, new_rows_df], ignore_index=True)

    # Save the updated DataFrame back to the CSV
    df.to_csv(csv_file, index=False)

def append_to_csv(file_path, new_rows):
    """
    Append new rows to a CSV file, ensuring only existing columns are used.

    Parameters:
    - file_path: str, path to the CSV file
    - new_rows: list of dicts, each dict represents a new row to append
    """
    # Read the existing CSV file into a DataFrame
    df = pd.read_csv(file_path)

    # Create a DataFrame for the new rows
    new_df = pd.DataFrame(new_rows)

    # Retain only the columns that exist in the original DataFrame
    new_df = new_df[df.columns.intersection(new_df.columns)]

    # Append the new rows to the original DataFrame
    updated_df = pd.concat([df, new_df], ignore_index=True)

    # Write the updated DataFrame back to the CSV file
    updated_df.to_csv(file_path, index=False)