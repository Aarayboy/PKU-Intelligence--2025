from flask import Flask, jsonify
from . import spider # 导入爬虫模块

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False # 传给前端的json信息直接使用中文，不转义为 Unicode

@app.route('/api/start-spider', methods=['POST']) # 定义了一个 HTTP API 接口,指定路径和只允许 POST 请求
def handle_spider_request(): # 请求到达时调用
    """
    一个API端点，用于触发爬虫
    使用 POST 方法，因为它会执行一个动作
    """
    print("收到爬取请求...")
    try:
        # 调用爬虫的主函数
        downloaded_files = spider.start_spidering()
        
        if not downloaded_files:
            return jsonify({
                "status": "warning",
                "message": "爬虫已运行，但没有下载到任何文件。"
            }), 200

        return jsonify({
            "status": "success",
            "message": f"成功下载 {len(downloaded_files)} 个文件。",
            "files": downloaded_files
        }), 200

    except Exception as e:
        # 捕获爬虫过程中可能出现的任何错误
        print(f"爬虫执行出错: {e}")
        return jsonify({
            "status": "error",
            "message": "爬虫执行过程中发生内部错误。",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    # 运行 Flask app
    # debug=True 模式会在修改代码后自动重启服务器
    app.run(host='0.0.0.0', port=5001, debug=True)