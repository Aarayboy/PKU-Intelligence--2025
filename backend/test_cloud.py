import requests
import json

def test_cloud_status():
    url = "http://localhost:4000/cloud"
    
    payload = {
        "userId": 1,
        "xuehao": "2300013230",  # 替换为真实学号
        "password": "1111111"   # 替换为真实密码
    }
    
    try:
        print("正在发送请求到 cloud_status 接口...")
        response = requests.post(url, json=payload, timeout=120)
        print(f"状态码: {response.status_code}")
        print("响应内容:")
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        
        return response.json()
    except Exception as e:
        print(f"请求失败: {e}")
        return None

if __name__ == "__main__":
    test_cloud_status()