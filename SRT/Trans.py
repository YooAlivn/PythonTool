import argostranslate.package
import argostranslate.translate

def setup_translator(from_code='en', to_code='zh'):
    # 1. Update package index
    argostranslate.package.update_package_index()

    # 2. Find and download the language pack (e.g., English to Chinese)
    available_packages = argostranslate.package.get_available_packages()
    package_to_install = next(
        filter(
            lambda x: x.from_code == from_code and x.to_code == to_code,
            available_packages
        )
    )
    argostranslate.package.install_from_path(package_to_install.download())
    print(f"Successfully installed {from_code} to {to_code} pack.")

def translate_text(text, from_code='en', to_code='zh'):
    # 3. Perform translation
    translated_text = argostranslate.translate.translate(text, from_code, to_code)
    return translated_text

# --- Execution ---
# Note: You only need to run setup_translator() ONCE per machine.
# setup_translator('en', 'zh')

text_to_translate = "FFmpeg is a complete, cross-platform solution to record, convert and stream audio and video."
result = translate_text(text_to_translate, 'en', 'zh')

print(f"Original: {text_to_translate}")
print(f"Translated: {result}")
