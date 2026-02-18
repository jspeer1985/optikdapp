module.exports = {
  apps: [
    {
      name: 'optik-platform',
      script: 'node_modules/next/dist/bin/next',
      args: 'start -p ${PORT:-3000}',
      env_production: {
        NODE_ENV: 'production',
        PORT: 3000
      }
    }
  ]
}
