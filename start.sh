#!/data/data/com.termux/files/usr/bin/bash
cd ~/Keen-Cortex-Pro
source venv/bin/activate
pkill -f "python app.py" 2>/dev/null
sleep 1
nohup python app.py > server.log 2>&1 &
sleep 2
echo "======================================"
echo "      KEEN CORTEX PRO IS RUNNING"
echo "======================================"
echo "Open: http://127.0.0.1:5000"
echo
curl -s -o /dev/null -w "HTTP:%{http_code} | Time:%{time_total}s\n" http://127.0.0.1:5000/
