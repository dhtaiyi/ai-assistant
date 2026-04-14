#!/bin/bash
source ~/anaconda3/etc/profile.d/conda.sh
conda activate openclaw
unset HF_ENDPOINT HTTP_PROXY HTTPS_PROXY http_proxy https_proxy
export HF_ENDPOINT=https://hf-mirror.com

echo "下载large-v3模型..."
python3 -c "from faster_whisper import WhisperModel; model = WhisperModel('large-v3', device='cuda', compute_type='int8'); print('Model ready!')"
echo "完成!"
