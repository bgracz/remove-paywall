import requests
from bs4 import BeautifulSoup
import json
from readability import Document

def extract_clean_text(html_content):
    doc = Document(html_content)
    clean_html = doc.summary()
    soup = BeautifulSoup(clean_html, 'lxml')
    return soup.get_text(separator='\n\n', strip=True)

def try_archive_fallback(url):
    api_url = f"http://archive.org/wayback/available?url={url}"
    
    try:
        response = requests.get(api_url, timeout=10)
        data = response.json()
        
        if data.get('archived_snapshots'):
            archive_url = data['archived_snapshots']['closest']['url']           
            res = requests.get(archive_url, timeout=15)
            return extract_clean_text(res.text)
        else:
            return "❌ No data"
    except Exception as e:
        return f"❌ Error: {e}"

def remove_paywall(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)',
        'Referer': 'https://t.co/',
        'X-Forwarded-For': '66.249.66.1',
        'Cookie': ''
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'lxml')
        content = None

        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.text)
                items = data if isinstance(data, list) else [data]
                for item in items:
                    if 'articleBody' in item:
                        content = item['articleBody']
                        break
            except: 
                continue
        
        if not content:
            content = extract_clean_text(response.text)

        if content and len(content) > 600:
            return content
        else:
            return try_archive_fallback(url)

    except Exception as e:
        return f"Error główny: {e}"

# --- Uruchomienie ---
print("URL:")
url = input().strip()
print("\n--- working... ---")

wynik = remove_paywall(url)
print("\n" + "="*50 + "\n")
print(wynik)
print("\n" + "="*50 + "\n")