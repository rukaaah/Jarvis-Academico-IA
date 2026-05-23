import requests
import base64

def extrair_texto_imagem(caminho_imagem: str) -> str:

    # Chave gratuita da api OCR.space
    api_key = "helloworld"
    
    try:
        with open(caminho_imagem, "rb") as image_file:
            img_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        
        payload = {
            'apikey': api_key,
            'base64Image': f"data:image/jpg;base64,{img_base64}",
            'language': 'por',  
            'isOverlayRequired': False
        }
        
        url = 'https://api.ocr.space/parse/image'
        response = requests.post(url, data=payload, timeout=30)
        response.raise_for_status()
        result = response.json()
        
        if result.get('IsErroredOnProcessing'):
            error_msg = result.get('ErrorMessage', ['Erro desconhecido'])[0]
            return f"Erro no OCR: {error_msg}"
        
        parsed_text = result['ParsedResults'][0]['ParsedText']
        return parsed_text
        
    except requests.exceptions.RequestException as e:
        return f"Falha na comunicação com a API de OCR: {e}"
    except Exception as e:
        return f"Erro inesperado ao processar a imagem: {e}"