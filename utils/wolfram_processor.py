import os
import logging
import requests
from urllib.parse import quote
from utils.math_translator import translate_math_text, translate_math_pods

logger = logging.getLogger(__name__)

# Get the Wolfram Alpha API key from environment variables
WOLFRAM_APP_ID = os.environ.get("WOLFRAM_APP_ID", "")

def process_with_wolfram(query):
    """
    Send the processed query to Wolfram Alpha API and get the results.
    
    Args:
        query (str): The processed query to send to Wolfram Alpha
        
    Returns:
        dict: A dictionary containing the result and result type, or None if processing fails
    """
    if not WOLFRAM_APP_ID:
        logger.error("WOLFRAM_APP_ID environment variable not set")
        return None
    
    try:
        logger.debug(f"Wolfram API App ID available: {bool(WOLFRAM_APP_ID)}")
        
        # URL encode the query
        encoded_query = quote(query)
        
        # الإعداد للوصول إلى واجهة Wolfram Alpha بإعداد معرّب
        podTitles = ["Input", "Result", "Definition", "Solution", "Derivative", "Indefinite integral", 
                    "Definite integral", "Roots", "Plot", "Properties"]
        exclude_pods = ["Input interpretation"]
        
        # First try the full results API with images and more detailed output
        url = f"https://api.wolframalpha.com/v2/query?input={encoded_query}&appid={WOLFRAM_APP_ID}&output=json&includepodid=*&format=image,plaintext"
        
        response = requests.get(url)
        
        if response.status_code == 200:
            result_json = response.json()
            
            # Check if we have success
            if result_json.get('queryresult', {}).get('success'):
                # Extract the pods from the result
                pods = result_json.get('queryresult', {}).get('pods', [])
                
                # Prepare structured results with both text and images
                result_data = []
                
                # Process pods to extract image and text data
                for pod in pods:
                    pod_title = pod.get('title', '')
                    if pod_title not in exclude_pods:
                        # تحقق من أن العنوان ليس فارغًا قبل إضافته
                        if not pod_title:
                            pod_title = "النتيجة"  # عنوان افتراضي إذا كان فارغًا
                            
                        pod_data = {
                            'title': pod_title,
                            'subpods': []
                        }
                        
                        for subpod in pod.get('subpods', []):
                            subpod_data = {
                                'text': subpod.get('plaintext', ''),
                                'image': None
                            }
                            
                            # Get image if available
                            if 'img' in subpod:
                                img_data = subpod.get('img', {})
                                if 'src' in img_data:
                                    subpod_data['image'] = img_data.get('src')
                            
                            pod_data['subpods'].append(subpod_data)
                        
                        result_data.append(pod_data)
                
                # تطبيق الترجمة على البيانات
                # ترجمة الـpods
                translated_result_data = translate_math_pods(result_data)
                
                # إعداد نسخة نصية للتوافق مع الإصدارات السابقة
                result_text = ""
                
                for pod in translated_result_data:
                    result_text += f"**{pod['title']}**\n"
                    for subpod in pod['subpods']:
                        result_text += subpod['text'] + "\n"
                    result_text += "\n"
                
                logger.debug("تمت ترجمة النتائج الرياضية بنجاح")
                
                return {
                    'result': result_text.strip(),
                    'result_type': 'rich',
                    'rich_data': translated_result_data
                }
            
        # If full API fails or returns no results, try the simple API
        simple_url = f"https://api.wolframalpha.com/v1/result?i={encoded_query}&appid={WOLFRAM_APP_ID}"
        
        simple_response = requests.get(simple_url)
        
        if simple_response.status_code == 200:
            # ترجمة النتيجة النصية البسيطة
            translated_text = translate_math_text(simple_response.text)
            return {
                'result': translated_text,
                'result_type': 'text'
            }
        
        logger.error(f"Error from Wolfram Alpha API: {simple_response.text}")
        return None
            
    except Exception as e:
        logger.error(f"Error processing query with Wolfram Alpha: {e}")
        return None
