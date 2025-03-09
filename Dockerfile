FROM public.ecr.aws/lambda/python:3.9

# アプリケーションディレクトリをコピー
COPY . ${LAMBDA_TASK_ROOT}

# 依存関係のインストール
RUN pip install --no-cache-dir -r requirements.txt

# Lambda ハンドラの設定
CMD ["lambda_handler.handler"]