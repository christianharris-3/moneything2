# Money Thing 2


# Hosting

### Setup
```bash
git clone https://github.com/christianharris-3/moneything2.git
cd moneything2
source 
```

### Normal Running
```bash
cd moneything2
source venv/bin/activate
nohup streamlit run main.py &
```

### Kill Existing Process
```bash
ps aux | grep streamlit
kill 1234
```