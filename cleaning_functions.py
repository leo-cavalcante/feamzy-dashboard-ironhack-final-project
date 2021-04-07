import pandas as pd
import numpy as np
import os
import glob

def grouping_notifications(string):
    if string in ["INFORMATION_EVENT","INVITATION_EVENT", "PERIOD_TO_VALIDATE", "INFORMATION"]:
        return "EVENT"
    elif string in ["SETUP_CALENDAR","SETUP_CLASS","SETUP_SCHOOL"]:
        return "SETUP"
    elif string in ["HOMEWORK_REQUEST", "HOMEWORK_RESPONSE"]:
        return "HOMEWORK"
    elif string in ["INVITATION_CLASS","MODAL_NOTIF_END_COACH","MODAL_NOTIF_INIT_COACH"]:
        return "CLASSES"
    else:
        return "UNKNOWN"


def clean_text(df):
    # Transform to lowercase
    df = df.str.lower()

    # Formating some words with weird characters that were translated with the bad accent
    df = df.str.replace("ãª", "ê").str.replace("ã", "à")

    # Correcting some words
    df = df.str.replace("lévénement", "l'événement", regex=False).str.replace("l''agenda", "l'agenda", regex=False)

    # Replace inconvenient whitespaces
    df = df.str.replace('  ', ' ', regex=False)

    # Replace different placeholders
    df = df.str.replace('{0}', '', regex=False).str.replace('{1}', '', regex=False).str.replace('{2}', '',regex=False).str.replace('{3}', '', regex=False)

    # Removing ponctuation
    # df = df.str.replace(".","", regex=False).str.replace(",","", regex=False).str.replace(":","", regex=False).str.replace("-","", regex=False).str.replace("'","",regex=False)
    df = df.str.replace('[^\w\s]', '', regex=True)

    df = df.str.strip("'.")

    return df


def clean_database(df):
    # Looping through columns to transform values from "Null" to NaN
    df = df.where(df != "Null")
    df = df.where(df != "null")
    df = df.where(df != "")

    # Droping rows that contains only NaN (null values)
    df.dropna(axis=0, how='all', inplace=True)

    # Droping columns that contains only NaN (null values)
    df.dropna(axis=1, how='all', inplace=True)

    # Droping columns that contains less than 99% of NaN values
    list_columns = []

    for column in df.columns:
        if df[column].isna().sum() / df.shape[0] >= 0.999:
            list_columns.append(column)

    if len(list_columns) > 0:
        df.drop(columns=list_columns, inplace=True)

    if ('label' in df.columns):
        df['label'] = clean_text(df['label'])

    if ('message' in df.columns):
        df['message'] = clean_text(df['message'])

    if ('notificationType' in df.columns):
        df["Group"] = df["notificationType"].apply(grouping_notifications)
        df["sphere"].loc[df.sphere.isna()] = df["Group"].loc[df.sphere.isna()]

    if ('Unnamed: 0' in df.columns):
        df.drop(columns="Unnamed: 0", inplace=True)

    return df


def clean_all_databases():
    # Changing the working directory if needed
    if "data" not in os.getcwd().split("/"):
        os.chdir("data")

    # Getting all files from the "data" folder
    files = glob.glob('*.csv')

    for file in files:
        # Getting the name of the file
        file_name = file.strip("export").split("-")[0]

        # Opening the database
        df = pd.read_csv(file)

        # Cleaning the database
        df = clean_database(df)

        # Exporting cleaned database to new folder
        os.chdir("../data_clean/")
        df.to_csv(file_name + ".csv")

        # Getting back to the right folder with the raw databases
        os.chdir("../data")

    return None

clean_all_databases()