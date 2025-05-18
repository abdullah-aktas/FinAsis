module.exports = {
  apps: [{
    name: "finasis",
    script: "npm",
    args: "start",
    instances: "max",
    exec_mode: "cluster",
    env_production: {
      NODE_ENV: "production",
      PORT: 3000,
      NODE_PATH: "./src"
    },
    error_file: "./logs/err.log",
    out_file: "./logs/out.log",
    log_date_format: "YYYY-MM-DD HH:mm Z",
    max_memory_restart: "500M"
  }]
}
