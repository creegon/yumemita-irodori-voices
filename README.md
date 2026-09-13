# 梦限大八人语音包 · 使用指南

这份包包含阿拉蕾、野乃花、律、千石ユノ、藤都子、薇欧拉、蓓儿、波波。沿用当前项目选定的声线版本，没有重新训练。八个文件是 Speaker Inversion 声线文件，必须配合 **Irodori-TTS-600M-v3-VoiceDesign** 使用；不是八套完整大模型，也不需要 LoRA。

[八人声线文件](app/voices_yumemita) · [当前参数与版本](app/yumemita_voice_manifest.json)

## 方式一：从 Git 安装（Windows）

先安装 [Git](https://git-scm.com/downloads/win) 和 [uv](https://docs.astral.sh/uv/getting-started/installation/)。然后在 PowerShell 执行：

```powershell
git clone https://github.com/creegon/yumemita-irodori-voices.git
cd yumemita-irodori-voices
powershell -ExecutionPolicy Bypass -File .\setup.ps1
.\START_YUMEMITA.bat
```

`-ExecutionPolicy Bypass` 仅用于这次启动脚本，不修改系统的执行策略。

安装脚本复用上游官方 `uv sync --extra cu128` 路线，锁定 Irodori 源码 commit `eaf74d6a19138f743acb5b71a445fd25a57db987`、其 `uv.lock` 与 Python 3.10，不跟随上游 main 自动升级。首次安装需要从 GitHub、PyPI / PyTorch 和 Hugging Face 下载数 GB 内容；已缓存的内容会复用，中断后重新执行同一个脚本即可继续。完成安装后的合成入口固定离线运行。

仅 CPU 安装可改为 `powershell -ExecutionPolicy Bypass -File .\setup.ps1 -Backend cpu`，速度较慢，本仓库没有做 CPU 耗时测试。NVIDIA 路线需要兼容 CUDA 12.8 的驱动。网络受限时，按自己电脑的代理配置运行 Git、uv 和 Hugging Face；脚本不写死作者的代理端口。

**八个声线文件已经在 Git 仓库里，无需 Git LFS。** 通用基座、依赖和生成结果放在本地忽略目录，不会随普通提交上传。

## 方式二：复用之前的魔裁离线整合包

下载或 clone 本仓库，将本仓库的 `app` 文件夹和 `START_YUMEMITA.bat` 复制到旧 **Irodori-Voice-Pack** 根目录，与旧包 `app`、`models` 合并。然后双击新入口，不必运行 `setup.ps1`，也不必下载基座。八人声线和新界面使用独立文件名，原魔裁的 `START.bat` 仍照常使用。

这八人是纯 Speaker Inversion；不要继续给她们挂魔裁 LoRA，也不要换成 v4 或 500M 基座。

## 三步开始

1. 将仓库或整合包放到可写的短路径，例如 `D:\YumemitaTTS`。不要在压缩软件里直接启动。
2. 双击 **START_YUMEMITA.bat**。保留命令行窗口，浏览器会打开 `http://127.0.0.1:7861`；没自动打开就手动输入这个地址。
3. 音色来源选“预设角色”，选人，填写日语台词，点“生成语音”。第一次生成要加载模型；具体速度取决于电脑。

默认安装路线是 Windows 64 位、PyTorch 2.10.0 + CUDA 12.8。优先使用 NVIDIA 显卡及兼容的新驱动；没有可用 CUDA 时程序会选 CPU，速度会明显变慢。未验证 AMD GPU 加速，也未给小显存显卡做兼容承诺。建议预留至少 20 GB 安装空间；Git 仓库很小，大文件在首次安装时下载。包内固定为 fp32 精度，不会为了省显存自动切换成别的精度。

## 台词与表演怎么填

台词框填要说出的**日语正文**，例如：

> おはよう。今日も一緒に頑張ろうね。

演技指导框只写表演方式，不把中文舞台指示放进台词。可以直接点预设，或写：

> 明るく自然な声で、親しい相手に話しかける。

意思是“用明快自然的声音，向熟悉的人说话”。想温柔些可以写 `優しく穏やかな声で、ゆっくり話す。`。也可以留空先听默认效果。预设和 emoji 是可尝试的控制方式，不保证每次都实现指定情绪。

人名、生僻汉字容易读错时，在正文改成正确假名。先一次合成一两句；长段落按句号或自然停顿分开生成，再自行拼接。底层单次生成上限为 30 秒，长文本可能漏掉后半句。

## 破音、杂音、跑声线时怎么做

**蓓儿、波波目前仍可能出现这些问题。这是现有模型的已知局限，打包没有把它修好。**

1. 随机种子保持空白，直接再次生成；空白表示换一个随机 seed。填固定数字再点生成，会重复使用那个 seed。
2. 只重生成有问题的句子。长句可以在自然停顿处分成两段。
3. 仍不满意时先用较简单的演技说明、去掉过密的 emoji，再试一次。不要把 CFG 和步数一路拉高当作修复保证。

每次生成的 WAV 都保存在包根目录 **outputs_yumemita**，旁边的 `.request.json` 保存台词、表演、实际 seed 和参数。每次独立保存，不会覆盖上一条。网页音频播放器也可试听、下载。跨显卡、驱动和依赖版本，同 seed 不承诺逐字节相同。

## 八个声线与默认参数

| 角色 | 文件名 | 选用训练 step | speaker CFG |
|---|---|---:|---:|
| 阿拉蕾 / 仲町あられ | `arale.speaker.safetensors` | 750 | 5 |
| 野乃花 / 宮永ののか | `nonoka.speaker.safetensors` | 250 | 5 |
| 律 / 峰月律 | `ritsu.speaker.safetensors` | 250 | 5 |
| 千石ユノ | `yuno.speaker.safetensors` | 3000 | 5 |
| 藤都子 | `miyako.speaker.safetensors` | 1000 | 5 |
| 薇欧拉 / ヴィオラ | `viola.speaker.safetensors` | 250 | 5 |
| 蓓儿 / ベル | `bell.speaker.safetensors` | 1000 | 3 |
| 波波 / ポポ | `popo.speaker.safetensors` | 1000 | 5 |

八个文件在 `app/voices_yumemita`。完整默认值在 `app/yumemita_voice_manifest.json`：model / codec 都为 fp32；40 steps；text CFG 3；caption CFG 3；speaker CFG 蓓儿为 3、其余为 5；cfg_min_t 0.5；duration_scale 1；不裁尾；不加载 LoRA。切换角色会恢复该角色的四个高级设置默认值。自己改高级设置属于实验，程序会将改动写入请求记录。

声线文件每个只有约 49 KB 是正常的：它保存角色条件，通用合成能力在共享基座中。八份声线并非分别复制几 GB 基座。蓓儿和波波的生成稳定性仍有限，建议多换种子尝试。

## 本次运行验证

2026-09-13 在 Windows / RTX 4090 上，实际运行 `setup.ps1` 拉取固定版本源码并新建 Python 3.10.20 环境，安装锁定依赖；基座文件复用本地缓存。随后通过 `START_YUMEMITA.bat` 启动网页服务，并调用网页的生成接口，八个角色各生成一条日语测试句，8/8 成功保存 WAV 与 seed / 参数记录。蓓儿实际使用 speaker CFG 3，其余为 5，均为 fp32、40 steps。

这验证安装与生成调用，不等于听感验收；本次没有进行 ASR 或模型听音评审。没有做其他硬件或完整冷缓存下载的测试。

## 常见启动问题

- **提示 Run setup.ps1 first**：Git 安装尚未完成；运行上面的安装命令。使用旧包时，检查 `START_YUMEMITA.bat` 旁边是否有 `app/python-runtime/python.exe` 和 `models`。
- **缺少离线模型 / LocalEntryNotFoundError**：Git 方式重新运行 `setup.ps1` 补下载；旧包方式检查是否完整保留 `models/hub`。合成入口固定离线，不会自动补下载。
- **端口 7861 被占用**：关闭已运行的这一套程序；也可以在终端运行 `START_YUMEMITA.bat --server-port 7862`，然后打开对应地址。
- **CUDA out of memory**：关闭其他占显存的程序、一次只生成一条并缩短文本；这不是训练失败。不能保证小显存设备运行当前 fp32 配置。
- **生成较慢**：看日志里的 device 是否为 cpu。GPU 不可用时先核对驱动与硬件；不要反复开多个窗口生成。
- **SilentCipher watermark is unavailable**：该次运行未找到可选水印模型，因此生成文件不带该水印；这条日志不会阻止保存 WAV。
- **不想用了**：关闭启动时的命令行窗口即可。

## 来源与范围

界面及离线运行方式参考先前的魔裁 Irodori-Voice-Pack；Git 安装复用固定版本上游源码和依赖锁；本次适配八人列表、纯 Speaker Inversion 路线、当前默认参数、独立输出与 seed 记录。没有加入训练集、原番切片、旧魔裁角色或新的模型训练。

上游：[Irodori-TTS](https://github.com/Aratako/Irodori-TTS)；[v3 VoiceDesign 基座](https://huggingface.co/Aratako/Irodori-TTS-600M-v3-VoiceDesign)；[解码器](https://huggingface.co/Aratako/Semantic-DACVAE-Japanese-32dim)。上游源码许可随 `.runtime/Irodori-TTS/LICENSE` 或旧包 `app/LICENSE` 保留；第三方说明见 [THIRD_PARTY.md](THIRD_PARTY.md)。这里不额外授予角色、素材或声音的商业使用权。

包内 manifest 锁定实际基座 revision；`BUILD_INPUTS.json` 记录所用源码和工具链。当前指南服务于上述 Windows 本地组合，不将它描述为已在其他机器上验证。打包测试确认启动、声线加载与实际生成是否成功，不代表每一句声音都完美。
