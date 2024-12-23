/**
 * BELOW IS A LIST OF CONFIGURABLE VARIABLES
 * python-rest-directory: Path to Pyrest directory
 * interpreter-path: Path to Python Interpreter in virtual environment. Default: python
 * portnumber: portnumber of pyrest
 * python-consumer-directory: Path to Pyconsumer directory
 * nginx-path: Path to nginx directory
 * conf-file-name: NGINX conf file name
 */

module.exports = {
  apps: [
    {
      name: 'pyrest',
      cwd: 'python-rest-directory',
      script: 'uvicorn',
      args: 'server:app --port portnumber', 
      interpreter: 'interpreter-path', 
      instances: 1,
      autorestart: false,
      watch: false,
      exp_backoff_restart_delay: 100,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'development'
      },
      env_production: {
        NODE_ENV: 'production'
      }
    },
    {
      name: 'pyconsumer',
      cwd: 'python-consumer-directory',
      script: 'consumer.py',	 
      interpreter: 'interpreter-path', 
      instances: 1,
      autorestart: false,
      watch: false,
      exp_backoff_restart_delay: 100,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'development'
      },
      env_production: {
        NODE_ENV: 'production'
      }
    },
	{
      name: "nginx",
      cwd: "nginx-path",
      script: "nginx.exe",
      args: ["-c", "./conf/conf-file-name.conf"],
      exec_interpreter: "none",
      exec_mode: "fork_mode",
      instances: 1,
      watch: false,
      kill_timeout: 3000,
      exp_backoff_restart_delay: 100,
      max_memory_restart: "1G",
      env: {
        NODE_ENV: "development",
      },
      env_production: {
        NODE_ENV: "production",
      },
      "pre-setup": "taskkill /f /im nginx.exe", 
      "pre-restart": "taskkill /f /im nginx.exe", 
      "pre-stop": "taskkill /f /im nginx.exe",
    }	
  ],
};
