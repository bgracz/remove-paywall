import requests
from bs4 import BeautifulSoup
import json

def remove_paywall(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    }
    
    print(f"Working...\n")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')

        print("[1/2]")
        json_scripts = soup.find_all('script', type='application/ld+json')
        
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                items = data if isinstance(data, list) else [data]
                
                for item in items:
                    if 'articleBody' in item:
                        return item['articleBody']
            except:
                continue

        print("[2/2]")
        
        article = soup.find('article')
        target = article if article else soup
        
        paragraphs = target.find_all('p')
        content = "\n".join([p.get_text() for p in paragraphs])
        
        if len(content) > 1000: 
            return content
        else:
            print("\n❌ FAILED")
            return None

    except Exception as e:
        return f"Error: {e}"

url = input()
wynik = remove_paywall(url)

if wynik:
    print("\n--- YOUR ARTICLE ---\n")
    print(wynik)
else:
    print("\nNext steps...")