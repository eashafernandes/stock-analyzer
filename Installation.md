1. git clone this repository and cd into it.

2. Create a Venv.

```
python -m venv venv
```

3. Activate the Venv.

```
windows: venv\Scripts\Activate.bat
linux: source venv\bin\activate
```

3. Install Packages.

```
pip install --no-index --find-links sitepackages -r requirements.txt
```

4. Add all configurables in PM2 File.

5. Add Config files in both microservices.

