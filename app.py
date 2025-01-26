# encoding:utf-8
from flask import Flask, request, Response, stream_with_context, jsonify
import requests
import json
from flask_cors import CORS, cross_origin
import time

app = Flask(__name__)
models = ["gpt-4o","gemini-pro","claude-sonnet-3.5","deepseek-v3","deepseek-r1","blackboxai-pro"]

# OpenAI API的URL
OPENAI_API_URL = "https://www.blackbox.ai/api/chat"

@app.route('/v1/chat/completions', methods=['POST'])
@cross_origin(origin='*')  # 允许所有域的请求
def openai_chat_stream():
    # 获取客户端发送的数据
    data = request.json
    null = None
    true = True
    false = False
    
    model = data["model"]
    
    if model not in models:
        return "不支持该模型", 500

    messages = data["messages"]
    prompt = None
    for m in messages:
        if m["role"] == "system":
            prompt = m["content"]
            break
    
    requestBody = {"messages":messages,"agentMode":{},"id":"NEX4Hei",
                   "previewToken":null,"userId":null,"codeModelMode":true,
                   "trendingAgentMode":{},"isMicMode":false,
                   "userSystemPrompt":prompt,"maxTokens":10240,
                   "playgroundTopP":null,"playgroundTemperature":null,
                   "isChromeExt":false,"githubToken":"","clickedAnswer2":false,
                   "clickedAnswer3":false,"clickedForceWebSearch":false,
                   "visitFromDelta":false,"isMemoryEnabled":false,
                   "mobileClient":false,
                   "userSelectedModel":model,
                   "validated":"00f37b34-a166-4efb-bce5-1312d87f2f94",
                   "imageGenerationMode":false,"webSearchModePrompt":false,
                   "deepSearchMode":false,"domains":null,"vscodeClient":false}
    # requestBody = json.dumps(requestBody)

    
    # 构建请求头
    headers = {
        "Content-Type": "application/json",
        "origin": "https://www.blackbox.ai",
        "referer": "https://www.blackbox.ai",
        "Accept": "*/*",
        "Connection": "keep-alive",
        # 'content-type': str(len(requestBody)),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0"
    }

    try:
        enable_stream = False
        if "stream" in data:
            enable_stream = data["stream"]
            
        
        # 发送HTTP请求到OpenAI API
        response = requests.post(
            OPENAI_API_URL,
            headers=headers,
            json=requestBody,
            stream=enable_stream  # 启用流式传输
        )

        # 检查响应状态码
        if response.status_code != 200:
            return jsonify(
                {'error': f"OpenAI API error: {response.status_code}, {response.text}"}), response.status_code

        if enable_stream:
            # 使用stream_with_context来处理流式响应
            def generate():
                size = 0
                for chunk in response.iter_lines():
                    
                    if chunk:
                        text = chunk.decode("utf-8")
                        body = {
                            "id": "chatcmpl-5e9568c7-31d8-4a25-9eaf-ac5f872fb461",
                            "object": "chat.completion.chunk",
                            "created": time.time(),
                            "model": data["model"],
                            "choices": [
                                {
                                    "index": 0,
                                    "delta": {
                                        "content": text,
                                        "role": "assistant"
                                    },
                                    "finish_reason": null
                                }
                            ],
                            "usage": null
                        }
                        
                    #     # 解析OpenAI的流式响应
                        yield "data:" +  json.dumps(body,ensure_ascii=False) + "\n\n"
                yield "[DONE]"
            return Response(stream_with_context(generate()), content_type='text/event-stream')
        else:
            text = ""
            for chunk in response.iter_lines():
                    
                if chunk:
                    text += chunk.decode("utf-8") + "\n\n"
                        
            return jsonify({
                            "id": "chatcmpl-5e9568c7-31d8-4a25-9eaf-ac5f872fb461",
                            "object": "chat.completion.chunk",
                            "created": time.time(),
                            "model": data["model"],
                            "choices": [
                                {
                                    "index": 0,
                                    "message": {
                                        "content": text,
                                        "role": "assistant"
                                    },
                                    "finish_reason": null
                                }
                            ],
                            "usage": null
                        })
                    #     # 解析OpenAI的流式响应
            

        

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/v1/models', methods=['POST','GET'])
@cross_origin(origin='*')  # 允许所有域的请求
def get_models():
    data = []
    for model in models:
        data.append({"id": model,
            "object": "model"})
        
    return jsonify({
        "data": data
    })


if __name__ == '__main__':
    app.run()