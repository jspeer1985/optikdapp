module.exports = {
  apps: [
    {
      name: 'optik-backend',
      cwd: __dirname,
      script: 'venv/bin/uvicorn',
      args: 'api.main:app --host 0.0.0.0 --port 8000',
      interpreter: 'none',
      autorestart: true,
      watch: false,
      max_restarts: 10,
      restart_delay: 2000,
      env: {
        PYTHONUNBUFFERED: '1',
      },
    },
  ],
};
