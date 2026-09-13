# 组件与声线来源

- 推理引擎：[Aratako/Irodori-TTS](https://github.com/Aratako/Irodori-TTS)，固定 commit `eaf74d6a19138f743acb5b71a445fd25a57db987`；遵循上游仓库许可。安装脚本复用该提交的 `pyproject.toml` 和 `uv.lock`。
- 通用基座：[Irodori-TTS-600M-v3-VoiceDesign](https://huggingface.co/Aratako/Irodori-TTS-600M-v3-VoiceDesign)，固定 revision `e863a3a93e652e09afeff3e84823a206a0a60314`。
- 解码器：[Semantic-DACVAE-Japanese-32dim](https://huggingface.co/Aratako/Semantic-DACVAE-Japanese-32dim)，固定 revision `47376ee24834d7a05a48ebabfe3cde29b3c5e214`。
- 分词器：[llm-jp-3-150m](https://huggingface.co/llm-jp/llm-jp-3-150m)，固定 revision `b112feef602fff752e4dac4c30af6a2c2fa41c7a`。
- 网页入口参考本地先前制作的魔裁 Irodori-Voice-Pack WebUI；保留其 Gradio 布局、表演预设和 emoji，调整角色与参数，并采用其 soundfile 写 WAV 的兼容方式。
- `yumemita_contract.py` 的比较函数来自当前项目 `production_contract.py`，调用前比较实际请求与导出的当前声线配置。
- 八份 speaker embedding 来源于个人项目当前选定的训练结果，具体文件身份与 step 见 `app/yumemita_voice_manifest.json`。不含训练切片或源番音频。角色及原作相关权利属于相应权利人；分享不额外授予角色或声音的商业使用权。
