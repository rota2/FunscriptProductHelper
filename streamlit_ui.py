import pandas as pd
import streamlit as st
import json
import requests
from bs4 import BeautifulSoup
import csv
import re
from sellix import Sellix
import pyshorteners
import pyperclip
import webbrowser


DEFAULT_FILEPATH = "DEFAULTS.json"
DATA_FILEPATH = "DATA.json"
SCRIPTED_FOR_LIST = ["The Handy", "The SR6", "The OSR2"]
INTENSITY_LIST = ["LIGHT", "MEDIUM", "HEAVY"]
NICHE_LIST = ["BJ", "PASSTHROUGH"]
SELLIX_ONLY_DATA = ["PRICE", "SELLIX TITLE", "LINK", "PASSWORD", "EROSCRIPT URL", "LIVE"]


NEW_DEFAULTS={}

HEADERS = {}
client = None
DATA= {}
DEFAULT_GATEWAY = []
DEFAULT_DELIVERY_TEXT = ""
DEFAULTS = {}

with open(DEFAULT_FILEPATH, 'r') as file:
    DEFAULTS = json.load(file)
    HEADERS = {
        "Authorization": DEFAULTS["SELLIX_AUTH_TOKEN"],
        "X-Sellix-Merchant": DEFAULTS["SELLIX_SHOP"],
        "Content-Type": "application/json",
    }
    DEFAULT_GATEWAY = DEFAULTS["DEFAULT_GATEWAYS"].split(",")
    DEFAULT_DELIVERY_TEXT = DEFAULTS["DEFAULT_DELIVERY_TEXT"]

    client = Sellix(DEFAULTS["SELLIX_AUTH_TOKEN"], DEFAULTS["SELLIX_SHOP"])



with open(DATA_FILEPATH, 'r') as file:
    try:
        DATA = json.load(file)
        FILLEDCOUNT = len(next(iter(DATA.values())))
    except:
        DATA = {}
        FILLEDCOUNT = 0

def copyEroscriptPost(row):
    updatedDataRow = pd.DataFrame(DATA).iloc[row].to_dict()
    eroscriptPost = buildEroscriptPost(updatedDataRow)
    pyperclip.copy(eroscriptPost)

def copyEroscriptTitle(row):
    updatedDataRow = pd.DataFrame(DATA).iloc[row].to_dict()
    eroscriptTitle = buildEroscriptTitle(updatedDataRow["TITLE"], updatedDataRow["STUDIO"])
    pyperclip.copy(eroscriptTitle)

def visitSellixListing(row):
    updatedDataRow = pd.DataFrame(DATA).iloc[row].to_dict()
    webbrowser.open(updatedDataRow["SELLIX POST"])

def visitEroscriptPost(row):
    updatedDataRow = pd.DataFrame(DATA).iloc[row].to_dict()
    webbrowser.open(updatedDataRow["EROSCRIPT URL"])

def visitEroscriptPaid():
    webbrowser.open("https://discuss.eroscripts.com/c/scripts/paid-scripts/")

def visitEroscriptFree():
    webbrowser.open("https://discuss.eroscripts.com/c/scripts/free-scripts/")
def buildEroscriptPost(data):
    print("Building Eroscript Post...")
    if data["TITLE"] == "":
        return None

    imagesMkDown = ""
    for image in data["IMAGES"]:
        imagesMkDown += f"""[url={image}][img]{image}[/img][/url]"""

    postBody = f"""
### :framed_picture: Preview
{imagesMkDown}

### :information_source: Details
Actress: {data["PORNSTAR"]}
Studio: {data["STUDIO"]}


### :memo: Notes
{data["DESCRIPTION"]}

**Script is {data["INTENSITY"]} intensity!**
**Scripted for {data["SCRIPTED FOR"]}**



### :clock1: Length and :fire: Heatmap
Duration: {data["DURATION"]}
[url={data["HEATMAP"]}][img]{data["HEATMAP"]}[/img][/url]




### :movie_camera: Video link
{data["LINK"]}

### :file_folder: Script
Price: {data["PRICE"]} USD
https://blewclue215.mysellix.io/product/{data["SELLIX TITLE"]}

### :closed_book: Portfolio
Check out my portfolio for more scripts! (Including freebies)
https://discuss.eroscripts.com/u/blewclue215/activity/portfolio

{",".join(data["TAGS"])}
        """
    return postBody


def buildEroscriptTitle(
    videoName,
    studio,
):
    print("Building Eroscript Title...")
    if videoName == "":
        return
    return f"[{studio}] {videoName}"

def buildSellixLink(title):
    return f"https://blewclue215.mysellix.io/product/{title}"

def setFunscriptPostState(uniqid, live="NO"):
    if live == "NO":
        state = {"private": True}
    elif live == "YES":
        state = {"private": False}

    url = f"https://dev.sellix.io/v1/products/{uniqid}"
    response = requests.request("PUT", url, json=state, headers=HEADERS)
    return f"LIVE NOW: {live}"


@st.dialog("Create New Data", width="large")
def instanceNewDataForm():
    newData = {}
    with st.form("newDataForm"):
        # st.write(f'Create new data at row {FILLEDCOUNT+1}')
        st.caption("Fill in as much data as you can here!")
        st.caption("The tool will scrape for the video metadata using the link you've provided!")
        st.caption("After submission, the tool will automatically build a Sellix Listing for you!")
        description = st.text_area("Description", help="Describe your funscript here (in eroscript post)")
        videoLink = st.text_input("Video Link [REQUIRED]", help="REQUIRED! Video link to scrape data from!", placeholder="[REQUIRED] https://vrporn.com/what-you-wanna-do-with-me/")
        heatmap = st.text_input("Heatmap Image Link", help="Online-hosted image address for heatmap!", placeholder="https://gcdnb.pbrd.co/images/gtvKGwnvOTYb.png?o=1")
        scriptedFor = st.selectbox("Scripted For:", SCRIPTED_FOR_LIST)
        intensity = st.selectbox("Intensity", INTENSITY_LIST)
        price = st.text_input("Price")
        megalink = st.text_input("Download Link [REQUIRED]",
                                 help="REQUIRED! Link to download the funscript! Best to lock this behind a password!",
                                 placeholder="[REQUIRED] https://mega.nz/#P!AgAncDSMKgskwzVszbXqz-V6OO9OpXQ8BpTH8574FKubklHcIgjFWFu4h0SXE3FdjZ-EZ3bOCgNft1YrMyZRgM8j3-t3KHWNzRtD6WyRinNgSSqdGoufcQ")
        megapassword = st.text_input("Download Password")
        primaryNiche = st.selectbox("Primary Niche", NICHE_LIST)
        secondaryNiche = st.selectbox("Secondary Niche", NICHE_LIST)

        submitted = st.form_submit_button("Create Data and build Sellix Listing!")
        if submitted:
            if videoLink!="" and megalink!="":
                title, pornstar, studio, duration, images, filteredTags = getDataFromVRPORN(videoLink)
                newData["TITLE"] = title
                newData["PORNSTAR"] = pornstar
                newData["STUDIO"] = studio
                newData["DURATION"] = duration
                newData["IMAGES"] = images
                newData["TAGS"] = filteredTags
                newData["DESCRIPTION"] = description
                newData["HEATMAP"] = heatmap
                newData["SCRIPTED FOR"] = scriptedFor
                newData["INTENSITY"] = intensity
                newData["PRICE"] = price
                newData["LINK"] = megalink
                newData["PASSWORD"] = megapassword
                newData["PRIMARY NICHE"] = primaryNiche
                newData["SECONDARY NICHE"] = secondaryNiche
                SELLIX_TITLE_ACRONYM = create_initials(title)
                newData["SELLIX TITLE"] = SELLIX_TITLE_ACRONYM
                newData["SELLIX POST"] = buildSellixLink(SELLIX_TITLE_ACRONYM)
                newData["EROSCRIPT URL"] = buildEroscriptsURLFromTitleAndStudio(studio, title)
                newData["EROSCRIPT TITLE"] = buildEroscriptTitle(title, studio)
                newData["ID"] = createFunscriptPost(newData)
                newData["LIVE"] = False

                try:
                    print("mergedData")
                    mergeData = merge_dictionaries(DATA, pd.json_normalize(newData))
                    with open(DATA_FILEPATH, "w") as file:
                        file.write(json.dumps(mergeData))
                except:
                    with open(DATA_FILEPATH, "w") as file:
                        file.write(pd.json_normalize(newData).to_json(indent=4))
                st.rerun()
            else:
                st.write("Please fill in the required fields!")


def create_initials(input_string):
    # Remove special characters except alphabetic characters and spaces
    cleaned_string = re.sub(r'[^A-Za-z\s]', '', input_string)

    # Split the string into words
    words = cleaned_string.split()

    # Get the first letter of each word and capitalize it
    initials = ''.join(word[0].upper() for word in words)

    return initials


def create_url(d9, b9):
    # Function to split and clean text
    def clean_text(text):
        # Replace non-alphanumeric characters with a comma, split by commas, and filter out empty strings
        return [word.strip() for word in re.split(r'[^a-zA-Z0-9]', text) if word.strip()]

    # Clean and join the D9 and B9 fields
    d9_clean = "-".join(clean_text(d9))
    b9_clean = "-".join(clean_text(b9))

    # Combine to form the URL
    url = f"https://discuss.eroscripts.com/t/{d9_clean}-{b9_clean}"

    return url


def buildEroscriptsURLFromTitleAndStudio(studio, title):
    return create_url(studio, title)

def getDataFromVRPORN(url):
    """
    Webscrapes data from video link! ONLY FOR VRPORN
    """

    def seconds_to_minutes(seconds):
        minutes = seconds // 60  # Integer division to get minutes
        remaining_seconds = seconds % 60  # Modulus to get the remaining seconds
        return f"{minutes}:{remaining_seconds}"

    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')
        title = soup.find('h1', class_='content-title h2-d').text
        pornstar = soup.find('div', class_='name_pornstar').text
        studio = soup.find('span', class_='footer-titles').text
        duration = seconds_to_minutes(
            int(soup.find('meta', attrs={'property': 'og:duration'}).get('content'))
        )
        vrpGallery = soup.find('div', class_="vrp-gallery-pro")
        imagesA = vrpGallery.findAll('a', class_="swipebox nopu item_link all_hover")
        images = [imageA.get("href") for imageA in imagesA]
        comma_delimited_images = ', '.join(images)
        print(comma_delimited_images)

        tags = [tag.text for tag in soup.find_all("a", rel="tag")]
        excludedTags = [
            "Binaural Sound",
            '4K',
            "8K",
            "6K",
            "180°",
            "3D",
            "60 FPS",
            "Fisheye",
            "HD",
            "POV",
            "Premium",
            "VR Sex",
        ]
        filteredTags = [item for item in tags if item not in excludedTags]
        tagString = ",".join(filteredTags)

        return title, pornstar, studio, duration, images, filteredTags


def merge_dictionaries(dict1, dict2):
    # Create a new dictionary to store the result
    merged_dict = {}

    for key in dict1.keys() | dict2.keys():
        # Combine the values from both dictionaries for the given key
        combined_dict = {}

        if key in dict1 and key in dict2:
            # Get the dictionaries to merge
            dict1_inner = dict1[key]
            dict2_inner = dict2[key]

            # Merge the dictionaries by assigning new keys for the second one
            combined_dict = {**dict1_inner, **{str(int(k) + len(dict1_inner)): v for k, v in dict2_inner.items()}}

        elif key in dict1:
            combined_dict = dict1[key]
        else:
            combined_dict = dict2[key]

        merged_dict[key] = combined_dict

    return merged_dict


def dataEditorChanged():
    print(DATA)
    with open(DATA_FILEPATH, "w") as file:
        file.write(DATA.to_json(indent=4))

def shorten_url(long_url):
    s = pyshorteners.Shortener()
    short_url = s.tinyurl.short(long_url)
    return short_url

def buildFunscriptDeliveryText(megalink=None, megapassword=None):
    if megalink == None:
        return None
    elif megapassword == None:
        return None
    return f"LINK: \n{megalink} \n\nPASSWORD: \n{megapassword}"


def buildFunscriptPayload(**kwargs):
    if kwargs["price"] == None:
        return None
    serviceText = buildFunscriptDeliveryText(kwargs["megalink"], kwargs["megapassword"])
    if serviceText == None:
        return None

    payload = {
        "title": kwargs["title"],
        "price": kwargs["price"],
        "description": kwargs["description"],
        "currency": "USD",
        "gateways": DEFAULT_GATEWAY,
        "type": "SERVICE",
        "serials": [None],
        "service_text": serviceText,
        "stock": -1,
        "delivery_text": DEFAULT_DELIVERY_TEXT,
        "max_risk_level": 100,
        'custom_fields': [
            {
                'name': 'I will be interested in a multi-axis version!',
                'required': True,
                'type': 'checkbox',
            }
        ],
        "private": True,
    }
    # print(payload)
    return payload

def updateFunscriptPost(uniqid, **kwargs):
    url = f"https://dev.sellix.io/v1/products/{uniqid}"
    response = requests.request("PUT", url, json=kwargs, headers=HEADERS)
    return json.loads(response.text)["data"]["uniqid"]


def setFunscriptPostState(data):
    state = {"private": not data['LIVE']}
    url = f"https://dev.sellix.io/v1/products/{data['ID']}"
    response = requests.request("PUT", url, json=state, headers=HEADERS)
    return data['LIVE']



def createFunscriptPost(data):
    title = data["SELLIX TITLE"]
    price = data["PRICE"]
    megalink = data["LINK"]
    megapassword = data["PASSWORD"]
    eroscriptURL = data["EROSCRIPT URL"]
    shortenedURL = shorten_url(eroscriptURL)
    linkedDescription = f"""Link After Purchase 
[Thread here!]({shortenedURL})"""

    try:
        ID = data["ID"]
    except:
        ID = ""


    if ID == "":
        print("No ID, creating")
        url = "https://dev.sellix.io/v1/products"
        response = requests.request(
            "POST",
            url,
            json=buildFunscriptPayload(
                title=title,
                description=linkedDescription,
                price=price,
                megalink=megalink,
                megapassword=megapassword,
            ),
            headers=HEADERS,
        )

        # nt.sheets["CATALOGUE"][int(currentRow), 17] = json.loads(response.text)["data"][
        #     "uniqid"
        # ]
        return json.loads(response.text)["data"]["uniqid"]
    else:
        print(ID)
        print("ID, Updating")
        print(shortenedURL)
        return updateFunscriptPost(
            ID,
            title=title,
            description=linkedDescription,
            price_display=price,
            service_text =  buildFunscriptDeliveryText(megalink, megapassword),
        )



GATEWAYS = [
    'PAYPAL',
    'STRIPE',
    'BITCOIN',
    'LITECOIN',
    'ETHEREUM',
    'BITCOIN_CASH',
    'NANO',
    'MONERO',
    'SOLANA',
    'RIPPLE',
    'BINANCE',
    'CRONOS',
    'BINANCE_COIN',
    'USDC',
    'USDT',
    'TRON',
    'BITCOIN_LN',
    'CONCORDIUM',
    'POLYGON',
    'PEPE',
    'DAI',
    'WETH',
    'APE',
    'SHIB',
    'USDC_NATIVE',
    'DOGECOIN',
]





st. set_page_config(layout="wide")

with st.container():
    if DEFAULTS["SELLIX_AUTH_TOKEN"] == "":
        # Probably first time setup
        with st.form("SELLIX AUTHENTICATION"):
            st.title("FIRST-TIME SETUP!")
            st.write(
                "This will only be written locally into your CATALOGUE cells AE1:AI1, because 'Secrets' function is buggy!"
            )
            token = st.text_input("Please provide your Sellix Auth Token!")
            shop = st.text_input("Please provide the Sellix Shop Name!")
            defaultDeliveryText = st.text_area(
                "Set your default delivery text here!",
                placeholder="""Link and password will also be sent to your email address!
    
    Here's a coupon for 25% off any of my scripts! ( One-Time use!)
    CODE: COMEONBACK
    
    P.S:
    If you give a 5 star review, you'll also get another 50% off coupon! :)""",
            )
            defaultGateways = st.multiselect(
                "Please choose the default payment gateways for your products!",
                GATEWAYS,
            )
            submitted = st.form_submit_button("Submit")
            if submitted:
                NEW_DEFAULTS["SELLIX_AUTH_TOKEN"] = token
                NEW_DEFAULTS["SELLIX_SHOP"] = shop
                NEW_DEFAULTS["DEFAULT_DELIVERY_TEXT"] = defaultDeliveryText
                NEW_DEFAULTS["DEFAULT_GATEWAYS"] = ",".join(defaultGateways)
                with open(DEFAULT_FILEPATH, 'w') as file:
                    json.dump(NEW_DEFAULTS, file, indent=4)  # `indent=4` makes the JSON pretty-printed
                st.rerun()

    else:
        st.title(f'FUNSCRIPT PRODUCT HELPER')
        st.subheader("This tool is meant to help automate some of the tedious work when making a funscript listing on Sellix and Eroscripts!")
        with st.expander("Quick Start Guide"):
            st.subheader("Automated Sellix Listing: ")
            st.caption("1. Get started by clicking on 'Create New Data at Row'" )
            st.caption("2. This will automatically create a Sellix Listing for you!")
            st.caption("3. Then confirm that the post is satisfactory in your Sellix Dashboard")
            st.caption("4. If it is, then click on 'Live' in the row to make the listing live")
            st.subheader("Eroscript Post Generation")
            st.caption("1. Once the sellix posting is live, time to post on Eroscripts!")
            st.caption("2. Click on the row's 'Copy Gen. Post', this will copy to your clipboard a generated eroscript post with all the information filled in!")
            st.caption("3. Paste that into the eroscript post editor")
            st.caption("4. Click on the row's 'Copy Gen. Title', this will copy to your clipbaord a generated eroscript title!")
            st.caption("5. Paste that into the eroscript post editor")
            st.subheader("Catalogue Management")
            st.caption("1. Simply modify the fields in the catalogue!")
            st.caption("2. Price, Download Link and Download Password modifications will update Sellix Posting")
            st.caption("3. Everything else will modify the generated Eroscript Post, so i recommend copying the gen. post once the updates are done and editing the original post to keep it in sync with the sellix listing!")

        st.divider()

        try:
            df = pd.DataFrame(DATA)
        except:
            df = pd.DataFrame(pd.json_normalize(DATA))

        olddf = df



        st.header("CATALOGUE")
        st.caption("IMPORTANT: modifying the 'Price', 'Download Link' and 'Download Password' here at any point will update the Sellix Listing!")
        if st.button(f'CREATE NEW DATA AT ROW {FILLEDCOUNT+1}',use_container_width=True):
            instanceNewDataForm()

            #with st.expander(f'CREATE NEW DATA AT ROW {FILLEDCOUNT+1}'):
            #instanceNewDataForm()

        utilbox, spreadsheet = st.columns([0.3, 0.8])


        with utilbox:
            post,title,sellix, eroscripts = st.columns([0.3,0.3,0.25,0.2])
            with post:
                #st.write("Copy Gen. Post")
                for i in range(FILLEDCOUNT):
                    st.button(f"Copy Gen. Post {i}", key=f"postCopy{i}",  on_click=copyEroscriptPost, kwargs={"row": i})
            with title:
                #st.write("Copy Gen. Title")
                for i in range(FILLEDCOUNT):
                    st.button(f"Copy Gen. Title {i}", key=f"titleCopy{i}",  on_click=copyEroscriptTitle, kwargs={"row": i})
            with sellix:
                #st.write("Visit Sellix Post")
                for i in range(FILLEDCOUNT):
                    st.button(f"Visit Sellix {i}", key=f"sellixList{i}",  on_click=visitSellixListing, kwargs={"row": i})
            with eroscripts:
                #st.write("Visit ES Post")
                for i in range(FILLEDCOUNT):
                    st.button(f"Visit ES {i}", key=f"eroscriptPost{i}",  on_click=visitEroscriptPost, kwargs={"row": i})


        with spreadsheet:
            DATA = st.data_editor(df,
                                  use_container_width=True,
                                  column_order=( "LIVE","PRICE", "EROSCRIPT TITLE", "DESCRIPTION", "HEATMAP", "INTENSITY", "SCRIPTED FOR",  "LINK", "PASSWORD"),
                                  column_config={"PORNSTAR": None,
                                                 "STUDIO":None,
                                                 "DURATION": None,
                                                 "IMAGES": None,
                                                 "TAGS":None,
                                                 "DESCRIPTION":st.column_config.TextColumn("EROSCRIPT BODYTEXT"),
                                                 "PRICE": st.column_config.NumberColumn("PRICE (USD)",min_value=0, max_value=100, format="$%.2f"),
                                                 "LIVE": st.column_config.CheckboxColumn(),
                                                 "INTENSITY": st.column_config.SelectboxColumn(options=INTENSITY_LIST),
                                                 "SCRIPTED FOR": st.column_config.SelectboxColumn(options=SCRIPTED_FOR_LIST),
                                                 "PRIMARY NICHE": st.column_config.SelectboxColumn(options=NICHE_LIST),
                                                 "SECONDARY NICHE": st.column_config.SelectboxColumn(options=NICHE_LIST),
                                                 "LINK": st.column_config.LinkColumn("DOWNLOAD LINK", width="medium"),
                                                 "PASSWORD": st.column_config.TextColumn("DOWNLOAD PASSWORD"),
                                                 "EROSCRIPT URL": st.column_config.LinkColumn("EROSCRIPT LINK", display_text="Visit Eroscript Post"),
                                                 "HEATMAP": st.column_config.LinkColumn("HEATMAP LINK", width="medium"),
                                                 "SELLIX POST": st.column_config.LinkColumn("SELLIX_ LISTING", display_text="Visit Sellix Listing")
                                                 },
                                  hide_index=False,
                                  on_change=dataEditorChanged
                                  )

            try:
                diff_df = olddf.compare(DATA)
                print(diff_df)
                # Extract the row indices where changes occurred
                changed_column = diff_df.columns.get_level_values(0).unique().tolist()[0]
                if changed_column in SELLIX_ONLY_DATA:
                    changed_rows = diff_df.index.values
                    print("Changes occurred:")
                    index = int(changed_rows[0])
                    updatedDataRow = DATA.iloc[index].to_dict()
                    createFunscriptPost(updatedDataRow)
                    liveState = setFunscriptPostState(updatedDataRow)
                    st.write(f"{updatedDataRow['TITLE']} Live State is now: {liveState}")
            except Exception as e:
                print(e)
                st.write("Ooops! Try that again please!")

        st.divider()
        st.header("Helpers")

        st.button("VISIT EROSCRIPT PAID SCRIPTS", on_click=visitEroscriptPaid, use_container_width=True)
        st.button("VISIT EROSCRIPT FREE SCRIPTS", on_click=visitEroscriptFree, use_container_width=True)
