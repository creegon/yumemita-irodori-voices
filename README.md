# 梦限大八人语音合成 · 从零安装指南

给第一次使用 Irodori 的朋友：**有 Git 就可以开始，不需要任何旧整合包或以前的项目文件。** 安装程序会准备 Python、依赖和通用模型，八人的声线已经放在仓库里。

包含阿拉蕾、野乃花、律、千石ユノ、藤都子、薇欧拉、蓓儿、波波。[八人声线文件](app/voices_yumemita) · [详细参数](app/yumemita_voice_manifest.json)

## 电脑需要什么

- Windows 10 / 11，64 位；已安装 Git。
- 推荐 NVIDIA 显卡，并安装兼容 CUDA 12.8 的驱动。不需要另装 CUDA Toolkit。
- 预留至少 20 GB 硬盘空间。第一次安装需要联网，下载约 3 GB 通用模型和数 GB 运行依赖；以后合成可以离线。

目前实际验证设备为 RTX 4090，尚未验证小显存显卡和 AMD 加速。没有 NVIDIA 显卡也有 CPU 安装选项，见下方常见问题，但速度会慢很多。

## 第一次用：下载、安装、启动

### 1. 下载这个仓库

在想保存程序的位置打开 PowerShell，执行：

```powershell
git clone https://github.com/creegon/yumemita-irodori-voices.git
```

会得到一个 `yumemita-irodori-voices` 文件夹。建议放在简短、可写的位置，例如 `D:\VoiceTools`。

### 2. 双击 SETUP_YUMEMITA.bat，等待安装完成

打开刚下载的文件夹，双击 **SETUP_YUMEMITA.bat**。它会自动：

1. 检查 Git；没有 uv 时从 [uv 官方安装入口](https://docs.astral.sh/uv/getting-started/installation/)下载到本文件夹。
2. 下载固定版本的 Irodori 源码，准备 Python 3.10 和运行依赖。
3. 下载对应的通用语音模型、解码器和分词器。

**不用自己安装 Python，不用自己找基座文件，也不用配置训练环境。** 第一次下载可能较慢，保留窗口并等待；看到 `Setup complete` 就表示安装完成。下载中断后重新双击同一个安装文件，已经完成的部分会复用。

也可以在 PowerShell 中进入仓库后运行：

```powershell
.\SETUP_YUMEMITA.bat
```

### 3. 双击 START_YUMEMITA.bat

安装完成后双击 **START_YUMEMITA.bat**。浏览器会打开 `http://127.0.0.1:7861`；如果没有自动打开，手动把这个地址填进浏览器。启动窗口需要一直保留。

之后每次使用只需双击启动文件，不用重新安装。八个声线都已经配置好，无需手动选模型文件。

### 4. 先生成一句试试

网页中音色来源选“预设角色”，再选一个人。台词框粘贴：

> おはよう。今日も一緒に頑張ろうね。

第一次先把演技指导和随机种子留空，高级设置保持默认，点击“生成语音”。首次生成需要加载模型。完成后可在网页试听、下载，文件也会自动保存到本文件夹的 **outputs_yumemita** 目录。

关闭启动时的命令行窗口即可退出程序。

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

2026-09-13，在 Windows / RTX 4090 上验证了两件事：

- 八个角色都通过网页生成接口各输出一条 WAV，并保存 seed 和参数记录；蓓儿实际使用 speaker CFG 3，其余为 5，均为 fp32、40 steps。
- 新建一个没有旧项目文件、没有模型缓存的目录，并从测试进程的 PATH 隐藏已安装的 uv 和 Python。新的安装入口自行安装 uv、创建 Python 环境、安装依赖，从 Hugging Face 官方完整下载通用模型、解码器和分词器；随后通过启动入口打开服务，以蓓儿默认参数、空演技和随机 seed 成功输出 WAV。

新目录没有引用旧整合包或它的模型目录；uv 自身允许复用正常的 Python / 包下载缓存。这验证从零准备项目与实际生成调用，不等于在另一台物理电脑上的测试，也不等于听感验收；未进行 ASR 或模型听音评审。

## 常见启动问题

- **只有 CPU / 没有 NVIDIA 显卡**：首次安装时在 PowerShell 运行 `.\SETUP_YUMEMITA.bat -Backend cpu`，之后仍用同一个启动文件。这条路线未做速度测试。
- **下载很慢或失败**：需要能访问 GitHub、PyPI / PyTorch 和 Hugging Face。先检查自己的网络，再重跑安装。如果使用代理，在同一个 PowerShell 窗口配置自己的 `HTTPS_PROXY` / `HTTP_PROXY` 后运行安装文件；本仓库不预设他人电脑的代理地址。
- **提示 First run SETUP_YUMEMITA.bat**：先双击 `SETUP_YUMEMITA.bat` 完成安装。
- **缺少离线模型 / LocalEntryNotFoundError**：重新双击 `SETUP_YUMEMITA.bat` 补齐下载。合成入口固定离线，不会自动补下载。
- **端口 7861 被占用**：关闭已运行的这一套程序；也可以在终端运行 `START_YUMEMITA.bat --server-port 7862`，然后打开对应地址。
- **CUDA out of memory**：关闭其他占显存的程序、一次只生成一条并缩短文本；这不是训练失败。不能保证小显存设备运行当前 fp32 配置。
- **生成较慢**：看日志里的 device 是否为 cpu。GPU 不可用时先核对驱动与硬件；不要反复开多个窗口生成。
- **SilentCipher watermark is unavailable**：该次运行未找到可选水印模型，因此生成文件不带该水印；这条日志不会阻止保存 WAV。
- **不想用了**：关闭启动时的命令行窗口即可。

## 来源与范围

本项目使用 Irodori-TTS v3 VoiceDesign。安装锁定公开上游 commit `eaf74d6a19138f743acb5b71a445fd25a57db987` 及其依赖锁，不跟随 main 自动升级。八份声线为现有训练结果，本次没有重新训练。界面与组件的来源记录在 [THIRD_PARTY.md](THIRD_PARTY.md)，使用者无需取得那些历史项目。

上游：[Irodori-TTS](https://github.com/Aratako/Irodori-TTS)；[v3 VoiceDesign 基座](https://huggingface.co/Aratako/Irodori-TTS-600M-v3-VoiceDesign)；[解码器](https://huggingface.co/Aratako/Semantic-DACVAE-Japanese-32dim)。上游源码许可随 `.runtime/Irodori-TTS/LICENSE` 保留；第三方说明见 [THIRD_PARTY.md](THIRD_PARTY.md)。这里不额外授予角色、素材或声音的商业使用权。

包内 manifest 锁定实际基座 revision；`BUILD_INPUTS.json` 记录所用源码和工具链。当前指南服务于上述 Windows 本地组合，不将它描述为已在其他机器上验证。打包测试确认启动、声线加载与实际生成是否成功，不代表每一句声音都完美。
