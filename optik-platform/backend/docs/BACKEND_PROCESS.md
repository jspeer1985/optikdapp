## Backend Process Control

### One-command control (PM2)

From `optik-platform/backend`:

```bash
./scripts/backendctl.sh start
./scripts/backendctl.sh status
./scripts/backendctl.sh logs 200
./scripts/backendctl.sh restart
./scripts/backendctl.sh stop
```

### Make PM2 survive reboot

Run once:

```bash
cd /home/kali/Dapp_Optik/optik-platform/backend
./scripts/backendctl.sh startup
```

PM2 will print a `sudo` command. Run that command, then:

```bash
./scripts/backendctl.sh save
```

### Systemd option

Service template file:

`systemd/optik-backend.service`

Install:

```bash
sudo cp /home/kali/Dapp_Optik/optik-platform/backend/systemd/optik-backend.service /etc/systemd/system/optik-backend.service
sudo systemctl daemon-reload
sudo systemctl enable --now optik-backend
sudo systemctl status optik-backend
```

### Notes

- Backend now auto-loads `backend/.env` from `api/main.py`.
- Do not run both PM2 and systemd at the same time on port `8000`.
