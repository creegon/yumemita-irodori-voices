#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Yumemita eight voices: adapted from the local Mocai offline WebUI, pure speaker inversion."""
from __future__ import annotations

import os
import sys
from pathlib import Path

# ⚠️ HF 环境变量必须在 import huggingface_hub / irodori_tts 之前设置才生效
APP_DIR = Path(__file__).resolve().parent
PACK_ROOT = APP_DIR.parent
UPSTREAM = PACK_ROOT / '.runtime/Irodori-TTS'
if UPSTREAM.is_dir():
    sys.path.insert(0, str(UPSTREAM))
os.environ["HF_HOME"] = str(PACK_ROOT / "models")  # 指向包内模型 cache（启动 bat 可覆盖）
os.environ["HF_HUB_OFFLINE"] = "1"  # 全程离线，零网络依赖

os.environ['HF_HUB_CACHE'] = str(PACK_ROOT / 'models/hub')
os.environ['HUGGINGFACE_HUB_CACHE'] = str(PACK_ROOT / 'models/hub')
os.environ['HF_HUB_DISABLE_TELEMETRY'] = '1'
os.environ['GRADIO_ANALYTICS_ENABLED'] = 'False'

import argparse  # noqa: E402
from yumemita_contract import MANIFEST, ROLES, check_request, require_match
import json  # noqa: E402
from datetime import datetime  # noqa: E402

import gradio as gr  # noqa: E402
from huggingface_hub import hf_hub_download  # noqa: E402

from irodori_tts.inference_runtime import (  # noqa: E402
    RuntimeKey,
    SamplingRequest,
    default_runtime_device,
    get_cached_runtime,
    list_available_runtime_precisions,
)

def save_wav(path, audio, sample_rate):
    # Same soundfile fallback as the legacy pack, without requiring FFmpeg DLLs.
    import soundfile as sf
    audio = audio.detach().to(device='cpu').float()
    data = audio.squeeze(0).numpy() if audio.shape[0] == 1 else audio.T.numpy()
    sf.write(str(path), data, sample_rate, subtype='PCM_16')
    return Path(path)


CHECKPOINT_REPO = "Aratako/Irodori-TTS-600M-v3-VoiceDesign"
CODEC_REPO = "Aratako/Semantic-DACVAE-Japanese-32dim"
VOICES_DIR = APP_DIR / "voices"
OUT_DIR = PACK_ROOT / "outputs_yumemita"

# 音色来源
SOURCE_CHARACTER = "预设角色（8 个练好的音色）"
SOURCE_REF = "上传参考音频（克隆任意音色 · 不用 LoRA）"

CHARACTERS = {v["display_name"]: k for k, v in ROLES.items()}

# 演技指导预设（日语 caption）：小白点一下自动填，不用自己憋日语
CAPTION_PRESETS: dict[str, str] = {
    "（不指定·纯文本）": "",
    "平静叙述": "落ち着いた自然な声で、ゆっくりと丁寧に話す。",
    "开心活泼": "明るく元気な声で、楽しそうに弾むように話す。少し笑みを含んだ声。",
    "温柔安慰": "優しく穏やかな声で、相手を包み込むように柔らかく語りかける。",
    "悲伤难过": "悲しげに声を震わせ、今にも泣き出しそうな弱々しいトーンで話す。",
    "生气愤怒": "怒りを込めて、強く鋭い口調で語気を荒げて話す。",
    "害羞傲娇": "恥ずかしそうに、照れた小さな声で、少しぶっきらぼうに話す。",
    "撒娇甜美": "甘えるように、ねだるような可愛らしい声で、語尾を柔らかく伸ばして話す。",
    "耳语ASMR": "耳元でささやくように、息を多く含んだ甘く小さな声で、ゆっくり話す。",
    "认真严肃": "真剣で落ち着いた低めの声で、はっきりと力強く話す。",
}

# 情绪 emoji（模型认识这些标记）：emoji -> 中文含义
EMOJI_LIST: list[tuple[str, str]] = [
    ("👂", "耳语/咬耳朵"),
    ("😮‍💨", "叹气/呼吸声"),
    ("⏸️", "停顿/沉默"),
    ("🤭", "偷笑/憋笑"),
    ("🥵", "喘息/呻吟"),
    ("📢", "回声/混响"),
    ("😏", "调侃/撒娇"),
    ("🥺", "颤抖/怯生生"),
    ("🌬️", "气喘/急促呼吸"),
    ("😮", "倒吸气/惊"),
    ("👅", "舔/咀嚼水声"),
    ("💋", "咂嘴/唇音"),
    ("🫶", "温柔"),
    ("😭", "哭腔/呜咽"),
    ("😱", "尖叫"),
    ("😪", "困倦/慵懒"),
    ("😴", "梦话/打鼾"),
    ("⏩", "快语速/急"),
    ("📞", "电话音/听筒"),
    ("🐢", "慢速"),
    ("🥤", "吞咽"),
    ("🤧", "咳嗽/抽鼻"),
    ("😒", "咂舌/不屑"),
    ("😰", "慌张/紧张/结巴"),
    ("😆", "开心/欢喜"),
    ("💥", "气势/有力"),
    ("😠", "生气/不满"),
    ("😲", "惊讶/感叹"),
    ("🥱", "打哈欠"),
    ("😖", "痛苦"),
    ("😟", "担心/不安"),
    ("🫣", "害羞"),
    ("🙄", "无语/翻白眼"),
    ("😊", "愉快"),
    ("😎", "得意/自信"),
    ("👌", "附和/点头"),
    ("🙏", "恳求/拜托"),
    ("🥴", "醉醺醺"),
    ("🎵", "哼歌"),
    ("🤐", "闷声/捂嘴"),
    ("😌", "安心/满足"),
    ("🤔", "疑问"),
    ("💪", "用力/坚定"),
    ("👃", "嗅闻"),
    ("📖", "朗读/旁白"),
]

# 合成示例（指导朋友怎么组合 台词 + 演技 + emoji）
SYNTH_EXAMPLES_MD = """\
照着下面改台词就能上手。**台词必须是日语**，演技选预设或自己写，情绪强的地方插 emoji。

| # | 场景 | 台词（填到②） | 演技预设（选③） |
|---|------|------|------|
| 1 | 日常问候 | `おはよう、今日もいい天気だね。` | 平静叙述 |
| 2 | 开心报喜 | `やった！試験に合格したよ！😆` | 开心活泼 |
| 3 | 温柔安慰 | `大丈夫、私がそばにいるから……🫶` | 温柔安慰 |
| 4 | 害羞告白 | `あの……ずっと、好きだったの……🫣` | 害羞傲娇 |
| 5 | 生气吐槽 | `もう！何回言ったらわかるの！😠` | 生气愤怒 |
| 6 | 睡前耳语 | `おやすみ……👂いい夢を見てね……` | 耳语ASMR |
| 7 | 悲伤哭诉 | `どうして……こんなことに……😭` | 悲伤难过 |
| 8 | 认真宣告 | `これだけは、絶対に譲れない。💪` | 认真严肃 |

**小技巧**：
- 想要停顿 → 在句中插 `⏸️`，例：`そんな……⏸️どうして……`
- 情绪叠加 → emoji 可连用，例：`ふふっ🤭……かわいいね😏`
- 不会写日语 → 用翻译软件把中文翻成日语；生僻汉字可换成假名避免读错。
"""

DEVICE = default_runtime_device()
PRECISION = "fp32"


def _char_embed_lora(char_key: str) -> tuple[str, None]:
    embed = APP_DIR / ROLES[char_key]['embedding']
    if not embed.is_file():
        raise FileNotFoundError(f'缺少声线文件: {embed}')
    return str(embed), None


def _runtime_key() -> RuntimeKey:
    # checkpoint 固定 600M VoiceDesign，离线从包内 cache 解析出本地 model.safetensors 路径
    ckpt_path = hf_hub_download(repo_id=CHECKPOINT_REPO, filename="model.safetensors", revision=MANIFEST["model_revision"], local_files_only=True)
    return RuntimeKey(
        checkpoint=str(ckpt_path),
        model_device=DEVICE,
        codec_repo=CODEC_REPO,
        model_precision=PRECISION,
        codec_device=DEVICE,
        codec_precision=PRECISION,
        compile_model=False,
        compile_dynamic=False,
    )


def _apply_preset(preset_name: str) -> str:
    return CAPTION_PRESETS.get(preset_name, "")


def _insert_emoji(current_text: str, emoji: str) -> str:
    # gradio 原生事件：点击 emoji 按钮 → 追加到台词末尾（不依赖被 gradio 6 sanitize 的内联 JS）
    return (current_text or "") + emoji


def _toggle_source(source: str):
    is_char = source == SOURCE_CHARACTER
    # 返回 (角色下拉 visible, 参考音频 visible)
    return gr.update(visible=is_char), gr.update(visible=not is_char)


def _emoji_tooltip_head() -> str:
    # 注入 <head> 脚本：MutationObserver 监听 SPA 渲染，emoji 按钮一出现就设 title（HTML 原生悬停提示）。
    # head 里的 <script> 一定执行（不被 sanitize）；MutationObserver 彻底解决"js 跑在按钮渲染前"的时机问题。
    titles = {f"emoji-btn-{i}": meaning for i, (_emoji, meaning) in enumerate(EMOJI_LIST)}
    titles_json = json.dumps(titles, ensure_ascii=False)
    return (
        "<script>\n"
        "(function() {\n"
        f"  var titles = {titles_json};\n"
        "  function apply() {\n"
        "    var n = 0;\n"
        "    for (var id in titles) {\n"
        "      var el = document.getElementById(id);\n"
        "      if (!el) continue;\n"
        "      var b = (el.tagName === 'BUTTON') ? el : (el.querySelector('button') || el);\n"
        "      if (b.getAttribute('title') !== titles[id]) { b.setAttribute('title', titles[id]); b.style.cursor = 'help'; }\n"
        "      n++;\n"
        "    }\n"
        "    window.__emojiTipCount = n;\n"
        "  }\n"
        "  function start() {\n"
        "    apply();\n"
        "    var obs = new MutationObserver(apply);\n"
        "    obs.observe(document.documentElement, { childList: true, subtree: true });\n"
        "    [500, 1500, 3000, 5000].forEach(function(t) { setTimeout(apply, t); });\n"
        "  }\n"
        "  if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', start); } else { start(); }\n"
        "})();\n"
        "</script>"
    )


def _generate(
    source: str,
    character_display: str,
    uploaded_audio: str | None,
    text: str,
    caption: str,
    num_steps: float,
    duration_scale: float,
    cfg_scale_speaker: float,
    cfg_scale_caption: float,
    seed_raw: str,
):
    logs: list[str] = []

    def log(msg: str) -> None:
        print(msg, flush=True)
        logs.append(msg)

    text_value = "" if text is None else str(text).strip()
    if text_value == "":
        raise gr.Error("请先填写台词（日语）。")
    caption_value = "" if caption is None else str(caption).strip()

    seed_text = "" if seed_raw is None else str(seed_raw).strip()
    seed = int(seed_text) if seed_text not in {"", "none", "None"} else None

    use_ref = source == SOURCE_REF
    if use_ref:
        ref_wav_path = (
            None if (uploaded_audio is None or str(uploaded_audio).strip() == "") else str(uploaded_audio)
        )
        if ref_wav_path is None:
            raise gr.Error("「上传参考音频」模式：请先上传一段参考音频（建议 5~15 秒清晰人声）。")
        ref_embed_path: str | None = None
        lora_path: str | None = None
        tag = "refvoice"
        log(f"[webui] 模式=上传参考音频克隆（无 LoRA） device={DEVICE} 演技={'有' if caption_value else '无'}")
    else:
        if character_display not in CHARACTERS:
            raise gr.Error("请选择一个角色。")
        char_key = CHARACTERS[character_display]
        ref_embed_path, lora_path = _char_embed_lora(char_key)
        ref_wav_path = None
        tag = char_key
        log(
            f"[webui] 模式=预设角色 角色={character_display}({char_key}) "
            f"device={DEVICE} 演技={'有' if caption_value else '无'}"
        )

    runtime_key = _runtime_key()
    runtime, reloaded = get_cached_runtime(runtime_key)
    log(f"[webui] 模型 {'首次加载' if reloaded else '复用缓存'}（首次加载耗时取决于电脑）")
    if not runtime.model_cfg.use_caption_condition:
        raise gr.Error("当前模型不支持 caption，请确认用的是 600M VoiceDesign。")

    request = SamplingRequest(
            text=text_value,
            caption=caption_value or None,
            ref_wav=ref_wav_path,
            ref_latent=None,
            ref_embed=ref_embed_path,
            no_ref=False,
            ref_normalize_db=-16.0,
            ref_ensure_max=True,
            num_candidates=1,
            decode_mode="sequential",
            seconds=None,
            duration_scale=float(duration_scale),
            max_ref_seconds=30.0,
            max_text_len=None,
            max_caption_len=None,
            num_steps=int(num_steps),
            seed=seed,
            cfg_guidance_mode="independent",
            cfg_scale_text=3.0,
            cfg_scale_caption=float(cfg_scale_caption),
            cfg_scale_speaker=float(cfg_scale_speaker),
            cfg_scale=None,
            cfg_min_t=0.5,
            cfg_max_t=1.0,
            truncation_factor=None,
            rescale_k=None,
            rescale_sigma=None,
            context_kv_cache=True,
            speaker_kv_scale=None,
            speaker_kv_min_t=None,
            speaker_kv_max_layers=None,
            t_schedule_mode="linear",
            sway_coeff=-1.0,
            trim_tail=False,
            lora_adapter=lora_path,
    )
    ui_values = {'num_steps': int(num_steps), 'duration_scale': float(duration_scale),
                 'cfg_scale_speaker': float(cfg_scale_speaker), 'cfg_scale_caption': float(cfg_scale_caption)}
    record = check_request(tag, runtime_key, request, ui_values) if not use_ref else {
        'mode': 'reference_audio', 'text': text_value, 'caption': caption_value, 'requested_seed': seed}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    request_path = OUT_DIR / f'{tag}_{stamp}.request.json'
    request_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
    result = runtime.synthesize(request, log_fn=log)
    record['used_seed'] = result.used_seed
    request_path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = save_wav(
        OUT_DIR / f"{tag}_{stamp}.wav",
        result.audios[0].float(),
        result.sample_rate,
    )
    log(f"[webui] 完成 seed={result.used_seed} -> {out_path}")
    return str(out_path), "\n".join(logs)


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="Irodori 语音合成", head=_emoji_tooltip_head()) as demo:
        gr.Markdown("# 🎙️ 梦限大 · 八人语音合成")
        gr.Markdown(
            "**用法**：① 选音色来源 → ② 填日语台词 →（可选演技/emoji）→ 点生成。"
            "首次生成需要加载模型，请等待。蓓儿和波波偶发破音时，清空种子后重试。"
        )

        source = gr.Radio(
            label="① 音色来源",
            choices=[SOURCE_CHARACTER, SOURCE_REF],
            value=SOURCE_CHARACTER,
        )
        with gr.Row():
            character = gr.Dropdown(
                label="选预设角色",
                choices=list(CHARACTERS.keys()),
                value=list(CHARACTERS.keys())[0],
                visible=True,
                scale=2,
            )
            ref_audio = gr.Audio(
                label="上传参考音频（5~15 秒清晰人声，克隆这个音色）",
                type="filepath",
                visible=False,
            )
            preset = gr.Dropdown(
                label="③ 演技预设（自动填入下方演技指导，可再手改）",
                choices=list(CAPTION_PRESETS.keys()),
                value="（不指定·纯文本）",
                scale=3,
            )

        text = gr.Textbox(
            label="② 台词（日语）· 情绪强的地方可插 emoji（点下方调色板）",
            lines=4,
            placeholder="例：こんにちは、今日はいい天気ですね。",
        )

        with gr.Accordion("😊 情绪 Emoji（点按钮插入台词 · 鼠标悬停看含义）", open=False):
            gr.Markdown("点下面的 emoji 插入台词末尾，**把鼠标停在 emoji 上会浮现它的含义**。")
            for row_start in range(0, len(EMOJI_LIST), 12):
                with gr.Row():
                    for idx in range(row_start, min(row_start + 12, len(EMOJI_LIST))):
                        emoji, _meaning = EMOJI_LIST[idx]
                        btn = gr.Button(emoji, min_width=40, scale=0, elem_id=f"emoji-btn-{idx}")
                        # 闭包默认参数 e=emoji 绑定当前 emoji（避免循环延迟绑定）
                        btn.click(lambda t, e=emoji: _insert_emoji(t, e), inputs=[text], outputs=[text])

        caption = gr.Textbox(
            label="演技指导 caption（日语·可选）· 描述情绪/语速/距离感",
            lines=3,
            placeholder="例：優しく穏やかな声で、ゆっくり話す。",
        )

        with gr.Accordion("💡 合成示例（照着改台词就能上手）", open=False):
            gr.Markdown(SYNTH_EXAMPLES_MD)

        with gr.Accordion("高级设置（已填入当前角色默认值）", open=False):
            with gr.Row():
                num_steps = gr.Slider(label="生成步数（默认40；调高不保证更好）", minimum=10, maximum=80, value=40, step=1)
                duration_scale = gr.Slider(label="语速（>1更慢，<1更快）", minimum=0.7, maximum=1.3, value=1.0, step=0.01)
            with gr.Row():
                cfg_scale_speaker = gr.Slider(label="声线强度（蓓儿3，其余5）", minimum=1.0, maximum=8.0, value=5.0, step=0.5)
                cfg_scale_caption = gr.Slider(label="演技遵循强度（默认3）", minimum=1.0, maximum=8.0, value=3.0, step=0.5)
            seed_raw = gr.Textbox(label="随机种子（留空=每次随机）", value="")

        generate_btn = gr.Button("🎵 生成语音", variant="primary", size="lg")

        out_audio = gr.Audio(label="生成结果", type="filepath", interactive=False)
        out_log = gr.Textbox(label="运行日志", lines=6)

        character.change(
            lambda name: tuple(ROLES[CHARACTERS[name]]['config'][k] for k in
                               ('num_steps', 'duration_scale', 'cfg_scale_speaker', 'cfg_scale_caption')),
            inputs=[character], outputs=[num_steps, duration_scale, cfg_scale_speaker, cfg_scale_caption],
        )
        source.change(_toggle_source, inputs=[source], outputs=[character, ref_audio])
        preset.change(_apply_preset, inputs=[preset], outputs=[caption])
        generate_btn.click(
            _generate,
            inputs=[
                source,
                character,
                ref_audio,
                text,
                caption,
                num_steps,
                duration_scale,
                cfg_scale_speaker,
                cfg_scale_caption,
                seed_raw,
            ],
            outputs=[out_audio, out_log],
        )

    return demo


def main() -> None:
    parser = argparse.ArgumentParser(description="Irodori 语音合成 WebUI（整合包小白版）")
    parser.add_argument("--server-name", default="127.0.0.1")
    parser.add_argument("--server-port", type=int, default=7861)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()

    print(f"[webui] HF_HOME={os.environ.get('HF_HOME')}  device={DEVICE}  precision={PRECISION}")
    demo = build_ui()
    demo.queue(default_concurrency_limit=1)
    demo.launch(
        server_name=args.server_name,
        server_port=args.server_port,
        share=False,
        inbrowser=not args.no_browser,
    )


if __name__ == "__main__":
    main()
