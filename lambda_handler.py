import json
from mangum import Mangum
from app.main import app

# MangumによるFastAPIアプリのラッピング
handler = Mangum(app)

# AWS Lambdaが使用するハンドラー関数
def lambda_handler(event, context):
    """
    AWS Lambda用のエントリーポイント
    """
    # Mangumを使ってFastAPIをLambdaに適合させる
    return handler(event, context)