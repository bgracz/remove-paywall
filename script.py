import requests
from bs4 import BeautifulSoup
import json

def try_archive_fallback(url):
    api_url = f"http://archive.org/wayback/available?url={url}"
    try:
        response = requests.get(api_url, timeout=20)
        data = response.json()
        
        if data.get('archived_snapshots'):
            archive_url = data['archived_snapshots']['closest']['url']
            
            res = requests.get(archive_url, timeout=25)
            soup = BeautifulSoup(res.text, 'lxml')
            paragraphs = soup.find_all('p')
            return "\n".join([p.get_text() for p in paragraphs])
        else:
            return "❌ Cannot find"
    except Exception as e:
        return f"❌ Archive error: {e}"

def remove_paywall(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'lxml')
        content = None
        json_scripts = soup.find_all('script', type='application/ld+json')
        
        for script in json_scripts:
            try:
                data = json.loads(script.text)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if 'articleBody' in item:
                        content = item['article']
                        break
            except: 
                continue
        
        if not content:
            paragraphs = soup.find_all('p')
            content = "\n".join([p.get_text(strip=True) for p in paragraphs])

        if content and len(content) > 1000:
            return content
        else:
            return try_archive_fallback(url)

    except Exception as e:
        return f"Error: {e}"

print("URL:")
url = input()
print("\n--- working... ---\n")
print(remove_paywall(url))