**LondonLAB Team — GitHub Onboarding Checklist**

Each team member should complete the following steps to be fully set up for collaborating on the Harrods forecasting repo:

---

### ✅ Step 1: Create a GitHub Account
- Go to https://github.com and sign up (if you don’t already have an account)
- Choose a username that’s easy to identify

### ✅ Step 2: Send Your GitHub Username to Miguel
- Share your username with Miguel via WhatsApp or email

### ✅ Step 3: Accept the GitHub Invite
- Miguel will add you to the repository
- GitHub will send you an invitation via email and your GitHub dashboard
- Accept it to gain full access to the repository

### ✅ Step 4: Set Up Your Local Dev Environment

#### 🔹 Install Git (if you don’t already have it)
- Download: https://git-scm.com/downloads
- After installing, configure Git:
  ```bash
  git config --global user.name "Your Name"
  git config --global user.email "your@email.com"
  ```

#### 🔹 Install Anaconda or Miniconda (recommended for environment management)
- Download: https://www.anaconda.com/products/distribution

#### 🔹 Create and Activate a New Conda Environment
```bash
conda create -n londonlab python=3.12
conda activate londonlab
```

#### 🔹 Install Core Packages
```bash
conda install -c conda-forge pandas numpy scikit-learn matplotlib seaborn scipy jupyterlab jupyterlab-git
```

---

### ✅ Step 5: Clone the Repo
Use this command (after accepting the invite):
```bash
git clone git@github.com:miguelkantor/londonlab_harrods_team2.git
```
If you haven't set up SSH yet, use HTTPS instead:
```bash
git clone https://github.com/miguelkantor/londonlab_harrods_team2.git
```

---

### ✅ Step 6: Work Inside the Repo Folder
- Navigate into the folder:
```bash
cd londonlab_harrods_team2
```
- Always make edits inside the cloned folder
- Use branches if you’re working on larger changes

---

### ✅ Step 7: Commit and Push Changes
```bash
git add .
git commit -m "Meaningful message here"
git push
```

Let Miguel know once you’re set up so we can move forward as a team.

