import requests
import json

class RequestError(Exception):
    """
    Request Error class for returning unsuccessfull status code
    """
    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        self.message = f"Received unsuccessfull result from request with status code {status_code}"
        
    def __str__(self):
        return self.message
    
class ClientLunaryAI:
    """
    Client for Lunary AI
    """
    def __init__(self, key: str, model: str):
        self.api_key = key
        self.ai_model = model

    def request_to_api(self, prompt: str):
        data = json.dumps({
            "model": self.ai_model,
            "messages": [{
                "role": "system",
                "content": "You - Lunary AI, telegram bot created by Mars Games Co."
            },{
                "role": "user",
                "content": prompt
            }]
        })

        with requests.post(
            url = "https://openrouter.ai/api/v1/chat/completions",
            headers = {"Authorization": f"Bearer {self.api_key}"},
            data = data,
            stream = True
        ) as response:
            if response.status_code != 200:
                return RequestError(status_code = response.status_code)

            json_responce = json.loads(response.text)
            content = json_responce["choices"][0]["message"]["content"]
            content_list = list(content)
            for num in range(0, len(content_list)):
                
                if content_list[num] == "*" and content_list[num+1] == " ":
                    content_list[num] == ""
                    content_list[num+1] == ""
                if content_list[num] == "#":
                    bruh = 0
                    while True:
                        if content_list[num+bruh] == "#":
                            content_list[num+bruh] = ""
                            bruh += 1
                        else:
                            break
                        

            return ''.join(content_list)