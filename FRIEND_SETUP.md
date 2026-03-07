# BTCPOLYARB — Friend Setup & Run Instructions

## What You Need to Know First
- The project now **auto-selects nearest Deribit expiry** each run (no manual expiry updates needed).
- Cron should run **only once daily at 07:00 UTC**.
- If you use hotspot/mobile internet, direct SSH may fail; use **EC2 Instance Connect** in AWS Console.

## 1) Server Setup (Ubuntu EC2)
```bash
sudo apt update
sudo apt install -y python3 python3-venv git
cd ~
git clone https://github.com/JiggityMaggotKetamynes/BTCPOLYARB.git
cd BTCPOLYARB
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdir -p logs data/raw
```

## 2) Create `.env` (Minimal)
```bash
cat > .env << 'EOF'
DERIBIT_BASE_URL=https://www.deribit.com/api/v2
POLYMARKET_BASE_URL=https://clob.polymarket.com
BINANCE_BASE_URL=https://api.binance.com
STRIKE_INTERVAL=500
REQUEST_TIMEOUT_SECONDS=10
OUTPUT_DIR=data/raw
DERIBIT_EXPIRY=
EOF
```

`DERIBIT_EXPIRY` can be blank now.

## 3) Manual Test Run
```bash
cd ~/BTCPOLYARB
/home/ubuntu/BTCPOLYARB/.venv/bin/python main.py --date $(date -u +%Y-%m-%d)
```

## 4) Set Cron (Only 07:00 UTC)
```bash
(crontab -l 2>/dev/null; echo '0 7 * * * cd /home/ubuntu/BTCPOLYARB && /home/ubuntu/BTCPOLYARB/.venv/bin/python main.py --date $(date -u +\%Y-\%m-\%d) >> /home/ubuntu/BTCPOLYARB/logs/collection.log 2>&1') | crontab -
crontab -l
```

## 5) Daily Verification
```bash
ls -lhtr ~/BTCPOLYARB/data/raw/
tail -n 60 ~/BTCPOLYARB/logs/collection.log
```

## Important Gotchas
- If Polymarket hourly market isn’t found, script falls back to `yes_price/no_price = 0.5`.
- Never append comments (`# ...`) on the same cron command line.
- If SSH times out: update Security Group SSH source to current IP or use EC2 Instance Connect.

## Quick SSH Notes
```bash
# Your current public IP (for SG rule)
curl -s https://checkip.amazonaws.com

# Standard SSH command
ssh -i /path/to/key.pem ubuntu@<EC2_PUBLIC_IP>
```
