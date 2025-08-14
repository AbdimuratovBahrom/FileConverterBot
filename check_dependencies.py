import shutil
import subprocess

tools = {
    "ImageMagick (magick)": ["magick", "-version"],
    "FFmpeg": ["ffmpeg", "-version"],
    "Pandoc": ["pandoc", "-v"],
    "7-Zip": ["7z"],
    "FontForge": ["fontforge", "-version"]
}

for name, cmd in tools.items():
    print(f"Проверка {name}...")
    if shutil.which(cmd[0]) is None:
        print(f"❌ {name} не найден!")
    else:
        try:
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"✅ {name} установлен.")
        except Exception as e:
            print(f"⚠️ Ошибка при проверке {name}: {e}")

print("\nПроверка завершена!")
