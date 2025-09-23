# lane-detection

Lane detection experiments.

## Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
```

### 2) Initialize Git and make the first commit
Run in your project root:
```bash
cd /Users/bedia/Desktop/lane-detection
git init
git add .
git commit -m "Initial commit: lane-detection"
git branch -M main
```

### 3) Create a GitHub repo and push

- Option A — using GitHub CLI (fastest):
```bash
gh repo create lane-detection --private --source . --remote origin --push
```
Change `--private` to `--public` if you prefer.

- Option B — using the website:
  1) Create a new repository on GitHub named `lane-detection` (without initializing with README).
  2) Connect and push:
  ```bash
  git remote add origin https://github.com/<your-username>/lane-detection.git
  git push -u origin main
  ```

### 4) (Optional) Use Git LFS if you need to keep binaries
If you must version large files (videos, models):
```bash
brew install git-lfs   # or: sudo apt-get install git-lfs
git lfs install
git lfs track "*.mp4" "*.avi" "*.mov" "*.mkv" "*.pt" "*.pth" "*.onnx"
git add .gitattributes
git commit -m "Track large artifacts with Git LFS"
git push
```

Need me to run any of these with specific repo visibility or name? I can also tailor `.gitignore` further if you want to keep certain folders tracked.

- Added a project-specific `.gitignore` to exclude `venv`, caches, editor files, and your generated/output directories (`output`, `debug_frames`, `frames_rgb*`, `data`).
- Provided concise commands to init Git, create or connect a GitHub repo, and push `main`.
- Included optional `README.md` snippet and Git LFS guidance for large artifacts.







1) add an RGB recording under data/rgb_data

2) run these commands
  commands:

  1) create a venv
    source venv/bin/activate

  2) python extract_frames.py

  3) python main.py


to delete output data before rerunning:
  rm -rf frames_rgb output frames_rgb 2 output 2 frames_rgb 3 output 3
  mkdir frames_rgb output




