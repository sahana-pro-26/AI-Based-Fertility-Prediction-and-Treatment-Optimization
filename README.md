# FertiCare AI

A Django app for PCOS detection, IVF success prediction, fertility scoring, and treatment recommendation.

## Run without VS Code

1. Open PowerShell.
2. Navigate to the project folder:
   ```powershell
   cd "C:\Users\tejal\Desktop\git\AI-Based-Fertility-Prediction-and-Treatment-Optimization"
   ```
3. Start the app with one command:
   ```powershell
   .\run_app.bat
   ```

Then open `http://127.0.0.1:8000/` in your browser.

## Launch with environment variable (optional)

If you have a Kaggle IVF CSV file, set `IVF_CSV` before running:
```powershell
$env:IVF_CSV = 'C:\path\to\your\ivf_kaggle.csv'
.\run_app.bat
```
