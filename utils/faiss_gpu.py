import faiss

try:
    num_gpus = faiss.get_num_gpus()
    if num_gpus > 0:
        print(f"✅ FAISS is using {num_gpus} GPU(s)!")
    else:
        print("⚠️ FAISS is installed but GPU support is not enabled.")
except AttributeError:
    print("❌ This FAISS build does not support GPU. Reinstall with GPU support.")
