# Synchronizing Data Between Two Cyberwatch Instances

This script lets you synchronize asset data from a **source Cyberwatch instance (Instance A)** to a **destination instance (Instance B)** using the Cyberwatch Python CLI.

This process is useful for air-gapped networks, backup purposes, or centralized analysis of vulnerability data.

---

## API Key Requirements

- Instance A (source): API key with **read-only** permissions  
- Instance B (destination): API key with **full access** permissions

Make sure your Cyberwatch CLI or environment is configured with the appropriate API key for each step below.

> If you get an `"api_url not found"` error, place `sync_assets.py` inside the `examples` directory and run it again.  

---

## Step 1 – Export Data from Instance A

> Use the **read-only** API key from **Instance A**

The Python script `sync_assets.py` fetches all assets from Instance A and saves their vulnerability data in `.txt` files.

Each `.txt` file corresponds to a single asset and is saved in the `export` directory (created automatically if it doesn't exist).

Run the script with:

```bash
python3 sync_assets.py
```

Output files will be located in the `export/` folder relative to where the script is run.

---

## Step 2 – Upload Data to Instance B

> Use the **full-access** API key from **Instance B**

1. Switch your API configuration to use the **Instance B full-access** API key  
2. Go to the `export/` directory where the `.txt` files were saved  
3. Upload all `.txt` files using:

```bash
cyberwatch-cli airgap upload export/*.txt
```
or
```bash
find ./export -name "*.txt" -exec sudo cyberwatch-cli airgap upload {} \;
```

> On Windows, the CLI automatically uploads files from the `uploads` folder by default.  
> To use the `export` directory, provide the full path to your `.txt` files.

---

## Result

- All assets from Instance A are successfully transferred to Instance B  
- Instance B automatically analyzes and recalculates vulnerability information upon upload

