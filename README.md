# DERMÉ — experimental skin insights prototype

A Streamlit web interface for the supplied Python image-analysis project.

## Run locally
```bash
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Deploy
Push the contents of this folder to a GitHub repository. On Streamlit Community Cloud, create an app using that repository, select `app.py` as the main file, and deploy.

## Important limitations
- This is an experimental image-processing prototype, not a clinically validated tool or medical device.
- Outputs depend on image lighting, pose, camera, and the project's heuristic image-processing methods.
- The app uses OpenCV Haar cascade face detection; no trained skin-diagnosis model is included in this project.
- Do not use its outputs to diagnose, treat, or make medical decisions.
- Uploaded image data is handled in app memory for the current session; hosting providers may process technical logs. Review hosting privacy terms before public use.
