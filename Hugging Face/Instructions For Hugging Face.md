# 🚀 Deploying News Summarization & TTS App on Hugging Face Spaces

This guide provides a step-by-step walkthrough to deploy your app (which includes web scraping, sentiment analysis, Hindi TTS, and translation features) on **Hugging Face Spaces** using a patched Google Translate integration.

---

## 📁 Files Required

Ensure the following files are ready before starting:

- `new_scraping.py` – Web scraping logic  
- `app.py` – Main frontend application  
- `requirements.txt` – Python dependencies  
- `patch_googletrans.py` – Patched version of Google Translate module  

---

## 1. 🔐 Log in to Hugging Face

- Visit: [https://huggingface.co/](https://huggingface.co/)  
- Sign in to your account, or create a new one if you don’t have one.

---

## 2. 🆕 Create a New Space

1. Click your profile icon → Select **New Space**
2. Fill in the following:
   - **Name**: Choose a unique project name  
   - **Space type**: Select `Gradio` or `Streamlit` (depending on your frontend)  
   - **Visibility**: Public or Private  
3. Click **Create Space**

---

## 3. ⬆️ Upload the Required Files (in order)

Navigate to the **Files and versions** tab of your Space and upload these files one by one:

1. `new_scraping.py`
2. `app.py`
3. `requirements.txt`
4. `patch_googletrans.py`

---

## 4. 🔧 Configure the Application

- Ensure your code is importing and using the patched `Translator` class from `patch_googletrans.py` instead of the default `googletrans` library.
- This is needed because the previous `googletrans` version had issues and a patch was applied for correct functionality.

---

## 5. 🛠️ Let Hugging Face Build the App

- Once all files are uploaded, Hugging Face will begin building the app automatically.
- The build installs packages from `requirements.txt`.
- Wait a few minutes for the process to complete.

---

## 6. ▶️ Run the Application

- After a successful build, open the **App** tab.
- Test the application’s features (web scraping, summarization, sentiment analysis, translation, TTS output, etc.).
- Use the **Logs** tab for debugging if needed.

---

## ✅ Deployment Complete!

You’ve now successfully deployed your News Summarization and Text-to-Speech application on Hugging Face Spaces, including the patched Google Translate functionality.

---

## 💡 Tips

- Keep your `requirements.txt` up to date for package versions.
- Use the **"Settings"** tab to manage app visibility and delete/restart builds.
- If you later link the project to GitHub, Hugging Face can auto-update on new commits.

---

## 📬 Need Help?

For further customization, GitHub integration, or adding a domain, feel free to reach out or consult the [Hugging Face documentation](https://huggingface.co/docs).

