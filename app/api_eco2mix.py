import requests
from urllib.parse import urlencode
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from datetime import date

eco2mix_api_url = "https://odre.opendatasoft.com/api/explore/v2.1/catalog/datasets/eco2mix-regional-tr/records?"



def get_region()-> list[str]:
    """
    Construit une liste de string représentant les libellés des regions présentent dans les données fournie par l'API éco2mix

    Returns:
        list[str] : liste comprenant les libellés des regions
    """
    list_dict = get_all_records(eco2mix_api_url, select_clause="libelle_region", group_by_clause = "libelle_region") # on récupère une liste de dictionnaires [{'libelle_region': 'Auvergne-Rhône-Alpes'},...]
    return [region for dict in list_dict for region in dict.values()]
    

def construction_query(date_debut: str, date_fin: str, region: str)-> str:
    """
    Permet de construire la condition permettant de filtrer les données éco2mix sur une période et une région données 

    Args:
        date_debut (str): string représentant la date du début de la période voulue.
        date_fin (str): string représentant la date de fin de la période voulue.
        region (str): libellé de la region voulue.

    Returns:
        str: String contenant la clause "where" permettant de filtrer les données de l'api éco2mix selon une période et une région données 
    """
    conditions = "date_heure >= date'"+date_debut+"' "
    conditions += "AND date_heure <= date'"+date_fin+"' "
    conditions += "AND libelle_region = '"+region+"'"
    return conditions


def get_all_records(url: str, where_clause: str = None, select_clause: str = None, group_by_clause: str = None)-> list:
    """
    Récupère toutes les données de l'API éco2mix selon les clauses "select", "where" et "group_by"

    Args:
        url (str): string comportant l'url permettant d'acceder aux records de l'api éco2mix
        where_clause (str, optional): string représentant la clause "where" avec toutes les conditions à respecter
        select_clause (str, optional): string représentant la clause "select" avec les noms des colonnes à récupérer
        group_by_clause (str, optional): string représentant la clause "group_by"

    Returns:
        list: une list des dictionnaires représentant toutes les données issues de la requete
    """
    all_records = []
    records_limit = 100
    params = {
            "limit": records_limit,
            "offset": 0
    }
    if select_clause is not None: params["select"] = select_clause
    if where_clause is not None: params["where"] = where_clause
    if group_by_clause is not None: params["group_by"] = group_by_clause

    while True:
        rep = requests.get(url, params=params)
        if rep.status_code != 200: break
        curr_records = rep.json()["results"]
        all_records.extend(curr_records)
        if len(curr_records) < records_limit:
            break
        else:
            params["offset"] += records_limit
    return all_records

def get_monitoring_figure(date_debut: date, date_fin: date, region: str):
    """
    Renvoie une figure matplotlib avec des plot représentant différentes distributions des données de l'API éco2mix selon une période et une région données 

    Args:
        date_debut (str): string représentant la date du début de la période voulue.
        date_fin (str): string représentant la date de fin de la période voulue.
        region (str): libellé de la region voulue.

    Returns:
        Figure: Une figure matplotlib contenant les graphiques.
    """

    conditions = construction_query(date_debut.strftime('%Y-%m-%d'),date_fin.strftime('%Y-%m-%d'),region)

    all_records = get_all_records(eco2mix_api_url, where_clause=conditions)
    df_records = pd.DataFrame(all_records)
    df_records["date_heure"] = pd.to_datetime(df_records["date_heure"], utc=True)
    df_records = df_records.sort_values("date_heure")


    fig, axs = plt.subplots(2, 2, figsize=(15, 12)) #création de la figure avec 4 graphiques
    fig.tight_layout(pad=3.0)
    
    #Premier graphique: consommation sur la période donnée
    axs[0][0].plot(df_records["date_heure"], df_records["consommation"], color="blue")
    axs[0][0].set_title("Consommation en MW")
    axs[0][0].set_ylabel("MW")
    axs[0][0].xaxis.set_major_locator(mdates.AutoDateLocator())
    axs[0][0].xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %Hh'))
    axs[0][0].tick_params(axis='x', labelsize=8) 

    #Deuxième graphique: affichage de valeur sur les pics de consommation
    conso_journaliere = df_records.groupby('date')["consommation"].sum()
    jour_pic_conso = conso_journaliere.idxmax()
    max_conso_journaliere = conso_journaliere[jour_pic_conso]
    axs[0][1].axis("off")
    axs[0][1].text(0.0, 0.5,
    "la consommation totale sur la période: " + str(df_records['consommation'].sum()) + " MW \n"+
    "La journée avec la plus grosse consommation est le: " + jour_pic_conso + " \navec une consommation de " + str(max_conso_journaliere) + " MW",
    ha='left', va='center',
    fontsize=10,
    weight='bold',
    transform=axs[0][1].transAxes)

    #Troisième graphique: distribution des production d'énergie par filière
    filiere_column_prod = ["thermique", "nucleaire", "eolien", "solaire", "hydraulique", "bioenergies"]
    axs[1][0].stackplot(df_records["date_heure"], [df_records[filiere] for filiere in filiere_column_prod], labels=filiere_column_prod, alpha=0.8)
    axs[1][0].xaxis.set_major_locator(mdates.AutoDateLocator())
    axs[1][0].xaxis.set_major_formatter(mdates.DateFormatter('%d/%m %Hh'))
    axs[1][0].tick_params(axis='x', labelsize=8) 
    axs[1][0].legend(loc="upper left", title="Filières")
    axs[1][0].set_title("Production par filière")

    #Quatrième graphique: Pourcentage de production d'énergie par filière sur la période
    sum_prod_filiere = df_records[filiere_column_prod].sum()
    sum_prod = sum_prod_filiere.sum()
    rate_by_field = (sum_prod_filiere / sum_prod * 100).round(2)
    wedges, _ = axs[1][1].pie(rate_by_field, colors=plt.cm.Set3.colors, labeldistance=1.1, pctdistance=0.8)
    axs[1][1].legend( wedges, rate_by_field.index, title="Filières", bbox_to_anchor=(1, 0.5))
    axs[1][1].set_title("Pourcentage de la production totale par filière")
    
    return fig



