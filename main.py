import google.generativeai as genai
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import json
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from bs4 import BeautifulSoup


def goodxpaths(data_list=None, file_name="goodxpaths.txt"):
    unique_items = set()
    
    # Mevcut dosyadaki verileri okuyup kümeye ekleyelim (varsa)
    try:
        with open(file_name, "r", encoding="utf-8") as file:
            existing_items = file.read().splitlines()
            unique_items.update(existing_items)
    except FileNotFoundError:
        pass  # Dosya yoksa sorun olmaz, devam ederiz
    
    # Yeni veri varsa ekleyelim
    if data_list:
        unique_items.update(data_list)
        
        # Dosyaya yazalım
        with open(file_name, "w", encoding="utf-8") as file:
            for item in sorted(unique_items):  # İsteğe bağlı: sıralayarak kaydediyoruz
                file.write(item + "\n")
    
    return list(unique_items)  # Liste olarak döndür


class WebSelector:
    def __init__(self,google_api):
        self.API = google_api
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service)
        self.goodxpaths = []
        self.hidden_elements = []


        genai.configure(api_key=self.API)
        self.model = genai.GenerativeModel("gemini-2.0-flash-exp")

    def Goto(self,url):
        self.driver.get(url)
    

    def TakeAHtml(self):
        html_content = self.driver.page_source
        soup = BeautifulSoup(html_content, "html.parser")

        elements = self.driver.find_elements(By.XPATH, "//*")
        hidden_elements = []

        for element in elements:
            style = self.driver.execute_script("return window.getComputedStyle(arguments[0]).getPropertyValue('display');", element)
            visibility = self.driver.execute_script("return window.getComputedStyle(arguments[0]).getPropertyValue('visibility');", element)

            if style == "none" or visibility == "hidden":
                hidden_elements.append({
                    "tag": element.tag_name,
                    "class": element.get_attribute("class"),
                    "id": element.get_attribute("id"),
                    "xpath": self.driver.execute_script("return arguments[0].outerHTML;", element)
                })

        self.hidden_elements =  hidden_elements
        return soup.prettify()
    
    def AskToAI(self,question):

        context = question

        try:
            answer = self.model.generate_content(context)
        
            TOKEN = self.model.count_tokens(context)
            print(f"COST [TOKEN] : {TOKEN}")
            return(answer.text)
                    
        except ValueError as e :
            print(f"ERROR ! : {e}")
            pass


    def LOGIN(self,url,username,password):
        self.driver.get(url)
        self.mission = "Login the web site"
        self.errors = ""
        self.complated = 0
        self.errstep = ""
        self.badxpath = []
        self.sucsess = []
        while True:
            time.sleep(3)
            self.goodxpaths = goodxpaths(self.goodxpaths)


            #Already completed steps: {self.sucsess}  
            #The one Last step you have error : {self.errstep}
            
            check = self.AskToAI(f"""
                Check this misson [{self.mission}] is done or not with this html [{self.TakeAHtml()}] and say **JUST**  yes or no 
            """)
        

            if "yes" in check:
                print(f"{self.mission} Complated")
                return


            actions_json = (self.AskToAI(f"""
                Login Credentials:
                Username: {username}

                Password: {password}

                Current Page HTML Content:
                {self.TakeAHtml()}

                IMPORTANT:

                You Already Did List : {self.sucsess}
                JUST TRY THE BEST SHORTCUT WAY TO DO


                You only have access to the provided HTML and must make decisions based only on the visible elements within it.

                DO NOT assume the presence of any elements that are not explicitly included in the provided HTML.

                Ensure all XPath values are accurate and correctly identify the elements.

                Only include interactive and visible elements. Ignore hidden, disabled, or non-functional elements.

                Sort all actions in a logical order that follows the structure of the page.

                XPath Selection Rules:
                
                

                If an element has a unique id, use //*[@id="element_id"].

                If an element has a unique name, use //*[@name="element_name"].

                If necessary, use functions such as contains() or text() to ensure precise selection.

                Do NOT guess missing elements—only use those present in the HTML.


                Good Examples XPath: 

                1. //button[@type='button' and div/span/span[text()='Next']]
                2. //button[@data-testid='LoginForm_Login_Button' and @role='button' and @type='button']

                Bad Examples XPath: {self.badxpath}




                Misson:
                {self.mission}
                

                Task:
                Generate a Python Selenium action list that includes only visible and interactive elements from the HTML. Do NOT add extra steps based on assumptions or missing information. Each action should directly correspond to an identifiable element in the provided HTML.

                Output Format:
                Your response must be a valid JSON array only, with no explanations or additional text. The JSON array must strictly follow this format:


                

                actions = [
                    {{ "action": "click", "xpath": "Full_XPath_here", "description": "Click on login button on homepage" }},
                    {{ "action": "send_keys", "xpath": "Full_XPath_here", "keys": "your_username", "description": "Enter username" }},
                    {{ "action": "send_keys", "xpath": "Full_XPath_here", "keys": "your_password", "description": "Enter password" }},
                    {{ "action": "click", "xpath": "Full_XPath_here", "description": "Click login button" }},
                    
                ]


                Strict Constraints:
                ONLY output a JSON array—no explanations, comments, or extra text.

                Ensure XPaths are correct, unique, and precisely identify the element.

                Actions should be in a logical order, matching the page structure.

                Only include actions for visible and interactive elements. Ignore anything hidden or disabled.


                """))
            
            #/html/body/div[1]/div/div/div[1]/div/div[1]/div/div/div/div/div[2]/div/div[2]/div[1]/a
            #/html/body/div[1]/div/div/div[1]/div/div[1]/div/div/div/div[2]/div[2]/div/div/div[1]/a
            actions_json = ((actions_json.strip()).replace("`","")).replace("json","")
            print(actions_json)


            if actions_json:
                xpathas= ""
                try:
                    # AI'nın cevabını JSON formatına çevir
                    actions = json.loads(actions_json)  # `exec` yerine `json.loads()`
                    
                    wait = WebDriverWait(self.driver, 10)

                    for step in actions:
                        action_type = step["action"]
                        xpath = step["xpath"]
                        xpathas = xpath

                        print(step)


                        
                        if action_type == "complated":
                            self.complated +=1
                            if self.complated == 5:
                                print("# LOGIN IS COMPLATED #")
                                return
                        
                        # XPath'i bekle (elementi görünene kadar)
                        
                        
                        self.errstep = step
                        
                        element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

                        if action_type == "click":
                            element.click()
                            print(f"✅ Clicked: {step['description']}")
                            self.sucsess.append(step)
                            self.goodxpaths.append(xpath)

                        elif action_type == "send_keys":
                            keys = step["keys"]
                            element.send_keys(keys)
                            print(f"✅ Entered: {step['description']}")
                            self.sucsess.append(step)
                            self.goodxpaths.append(xpath)


                        elif action_type == "press_enter":
                            element.send_keys(Keys.ENTER)
                            print(f"✅ Pressed Enter: {step['description']}")
                            self.sucsess.append(step)
                            self.goodxpaths.append(xpath)


                        elif action_type == "hover":
                            actions = ActionChains(self.driver)
                            actions.move_to_element(element).perform()
                            print(f"✅ Hovered: {step['description']}")
                            self.sucsess.append(step)
                            self.goodxpaths.append(xpath)


                    #print("🎉 Login ✅!")
                    #return
                    xpathas = ""
                except Exception as e:
                    print(f"❌ Error: {e}")
                    #print(self.AskToAI(f"{self.errstep} bu değerin doğrusunu {self.TakeAHtml()} içinde bulup dönebilir misin"))
                    self.errors = e
                    self.badxpath.append(xpathas)
                    print(self.badxpath)

                    

            else:
                print("❌ AI'dan geçerli bir işlem listesi alınamadı.")


        
    def tryit(self,misson):
            
            self.driver.get("https://www.google.com/search?q=twitter")

            self.mission = misson
            self.errors = ""
            self.complated = 0
            self.errstep = ""
            self.badxpath = []
            self.sucsess = []
            while True:
                time.sleep(3)
                self.goodxpaths = goodxpaths(self.goodxpaths)

                #Already completed steps: {self.sucsess}  
                
                

                '''
                check = self.AskToAI(f"""
                    Check this misson [{self.mission}] is done or not with this html [{self.TakeAHtml()}] and say **JUST**  yes or no 
                """)
            

                if "yes" in check:
                    print(f"{self.mission} Complated")
                    return

                '''

                actions_json = (self.AskToAI(f"""


                    Current Page HTML Content:
                    {self.TakeAHtml()}

                    IMPORTANT:

                    - **Some elements on the page may be covered by modal popups, overlays, or other UI elements.**
                    - **Before interacting with any element, check if there are blocking elements with high z-index.**
                    - **If a blocking element is found, close it first by clicking its close button or interacting with an appropriate element.**
                    - **Use the following list of blocking elements detected in the current page:**
                    {self.hidden_elements}

                    You Already Did List : {self.sucsess}

                    **IF IT GETS BACK,The one Last step you have error {self.errstep} REVIEW THE MISTAKE IN THE FIRST STEP AND FIND ALTERNATIVE NEW WAYS**

                    You only have access to the provided HTML and must make decisions based only on the visible elements within it.

                    DO NOT assume the presence of any elements that are not explicitly included in the provided HTML.

                    Ensure all XPath values are accurate and correctly identify the elements.

                    Only include interactive and visible elements. Ignore hidden, disabled, or non-functional elements.

                    Sort all actions in a logical order that follows the structure of the page.

                    XPath Selection Rules:
                    
                    


                    **DONT USE THİS LİST OF XPATHS {self.badxpath}**


                    Good Examples XPath: 

                    1. //button[@type='button' and div/span/span[text()='Next']]
                    2. //button[@data-testid='LoginForm_Login_Button' and @role='button' and @type='button']
                    {self.goodxpaths}
                    




                    Misson:
                    {self.mission} [IF THERE ARE OTHER THINGS IN FRONT OF THE SCREEN, CLOSE THEM FIRST [COOKIES,RECOMMENDATIONS,ADVERTISEMENTS]]
                    

                    Task:
                    Generate a Python Selenium action list that includes only visible and interactive elements from the HTML. Do NOT add extra steps based on assumptions or missing information. Each action should directly correspond to an identifiable element in the provided HTML.

                    Output Format:
                    Your response must be a valid JSON array only, with no explanations or additional text. The JSON array must strictly follow this format You have to add multiple Xpath:


                    

                    actions = [
                        {{ "action": "click", "xpath": "[Full_XPath_here,Full_XPath_here,Full_XPath_here...]", "description": "description_of_action" }},
                        {{ "action": "send_keys", "xpath": "[Full_XPath_here,Full_XPath_here,Full_XPath_here...]", "keys": "keys", "description": "description_of_action" }},
                        {{ "action": "press_enter", "xpath": "press_enter", "keys": "keys", "description": "description_of_press_enter" }}

                       
                        
                    ]


                    Strict Constraints:
                    ONLY output a JSON array—no explanations, comments, or extra text.

                    Ensure XPaths are correct, unique, and precisely identify the element.

                    Actions should be in a logical order, matching the page structure.

                    Only include actions for visible and interactive elements. Ignore anything hidden or disabled.


                    """))
                
                #/html/body/div[1]/div/div/div[1]/div/div[1]/div/div/div/div/div[2]/div/div[2]/div[1]/a
                #/html/body/div[1]/div/div/div[1]/div/div[1]/div/div/div/div[2]/div[2]/div/div/div[1]/a
                actions_json = ((actions_json.strip()).replace("`","")).replace("json","")
                print(actions_json)


                if actions_json:
                    xpathas= ""
                    try:
                        # AI'nın cevabını JSON formatına çevir
                        actions = json.loads(actions_json)  # `exec` yerine `json.loads()`
                        
                        wait = WebDriverWait(self.driver, 10)

                        for step in actions:
                            time.sleep(2)
                            action_type = step["action"]
                            xpaths = step["xpath"]
                            for xpath in xpaths:
                                xpathas = xpath

                                print(step)

                                
                                # XPath'i bekle (elementi görünene kadar)
                                
                                
                                self.errstep = step
                                
                                element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))

                                if action_type == "click":
                                    element.click()
                                    print(f"✅ Clicked: {step['description']}")
                                    self.sucsess.append(step)
                                    self.goodxpaths.append(xpath)
                                    break

                                elif action_type == "send_keys":
                                    keys = step["keys"]
                                    element.send_keys(keys)
                                    print(f"✅ Entered: {step['description']}")
                                    self.sucsess.append(step)
                                    self.goodxpaths.append(xpath)
                                    break




                                elif action_type == "press_enter":
                                    element.send_keys(Keys.ENTER)
                                    print(f"✅ Pressed Enter: {step['description']}")
                                    self.sucsess.append(step)
                                    self.goodxpaths.append(xpath)
                                    break




                                elif action_type == "hover":
                                    actions = ActionChains(self.driver)
                                    actions.move_to_element(element).perform()
                                    print(f"✅ Hovered: {step['description']}")
                                    self.sucsess.append(step)
                                    self.goodxpaths.append(xpath)
                                    break




                        #print("🎉 Login ✅!")
                        #return
                        xpathas = ""
                    except Exception as e:
                        print(f"❌ Error: {e}")
                        #print(self.AskToAI(f"{self.errstep} bu değerin doğrusunu {self.TakeAHtml()} içinde bulup dönebilir misin"))
                        self.errors = e
                        self.badxpath.append(xpathas)
                        print(self.badxpath)

                        

                else:
                    print("❌ AI'dan geçerli bir işlem listesi alınamadı.")



X = WebSelector(google_api="----")
#X.LOGIN("https://x.com/home","---","----")
X.tryit("Go to twitter")