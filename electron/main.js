const { app, BrowserWindow, dialog, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { exec, spawn } = require('child_process');
const axios = require('axios');

let mainWindow;
let splashWindow;
let backendProcess;
let backendErrors = [];

// Log file - reset on each startup
const logFile = path.join(app.getPath('userData'), 'sgp-log.txt');
try { fs.writeFileSync(logFile, ''); } catch(e) {}

function log(msg) {
  const line = `[${new Date().toISOString()}] ${msg}\n`;
  console.log(msg);
  try { fs.appendFileSync(logFile, line); } catch(e) {}
}

function createSplashWindow() {
  splashWindow = new BrowserWindow({
    width: 500,
    height: 600,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    show: false,
    center: true,
    backgroundColor: '#00000000',
    webPreferences: { nodeIntegration: false, contextIsolation: true }
  });
  splashWindow.loadFile(path.join(__dirname, 'splash.html'));
  splashWindow.once('ready-to-show', () => {
    log('Splash window ready to show');
    splashWindow.show();
  });
  splashWindow.on('closed', () => (splashWindow = null));
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 850,
    title: 'SGP - Dulce Nombre de Jesús',
    backgroundColor: '#ffffff',
    show: false,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      devTools: !app.isPackaged
    }
  });

  let attempts = 0;
  const maxAttempts = 60;

  const checkBackend = setInterval(async () => {
    attempts++;
    try {
      await axios.get('http://127.0.0.1:8080/health', { timeout: 2000 });
      log('Backend is ready!');
      clearInterval(checkBackend);

      mainWindow.loadURL('http://127.0.0.1:8080/');
      mainWindow.once('ready-to-show', () => {
        setTimeout(() => {
          if (splashWindow) splashWindow.close();
          mainWindow.show();
          mainWindow.focus();
        }, 500);
      });

    } catch (e) {
      log(`Health check ${attempts}/${maxAttempts} failed: ${e.message}`);
      if (attempts >= maxAttempts) {
        clearInterval(checkBackend);
        if (splashWindow) splashWindow.close();
        const detail = backendErrors.length > 0
          ? `\n\nErrores:\n${backendErrors.slice(-5).join('\n')}`
          : '\n\nEl servidor no envió mensajes de error.';
        dialog.showErrorBox(
          'Error de Conexión',
          `El servidor no respondió en ${maxAttempts} segundos.${detail}\n\nLog: ${logFile}`
        );
        app.quit();
      }
    }
  }, 1000);
}

// Libera el puerto antes de arrancar — previene conflictos si la app se cerró mal
function killPort(port, callback) {
  log(`Clearing port ${port}...`);
  // Busca PIDs en ese puerto y los mata
  exec(
    `netstat -ano | findstr :${port}`,
    (err, stdout) => {
      if (!stdout) {
        log('Port already free.');
        return setTimeout(callback, 200);
      }
      const lines = stdout.split('\n');
      const pids = new Set();
      for (const line of lines) {
        const parts = line.trim().split(/\s+/);
        const pid = parts[parts.length - 1];
        if (pid && /^\d+$/.test(pid) && pid !== '0') pids.add(pid);
      }
      if (pids.size === 0) {
        log('No PIDs found on port.');
        return setTimeout(callback, 200);
      }
      let pending = pids.size;
      for (const pid of pids) {
        log(`Killing PID ${pid} on port ${port}`);
        exec(`taskkill /F /PID ${pid}`, () => {
          pending--;
          if (pending === 0) setTimeout(callback, 500); // Esperar 500ms para liberar el socket
        });
      }
    }
  );
}

// SIEMPRE usar spawn (no execFile) — execFile bloquea indefinidamente en servidores
function startBackend(command, args) {
  log(`Spawning backend: ${command} ${args.join(' ')}`);

  backendProcess = spawn(command, args, {
    shell: false,
    detached: false,
    windowsHide: true,
    stdio: ['ignore', 'pipe', 'pipe']
  });

  log(`Backend PID: ${backendProcess.pid}`);

  backendProcess.stdout.on('data', (d) => log(`Backend OUT: ${d.toString().trim()}`));
  backendProcess.stderr.on('data', (d) => {
    const msg = d.toString().trim();
    log(`Backend ERR: ${msg}`);
    backendErrors.push(msg);
  });
  backendProcess.on('error', (err) => {
    log(`Backend spawn error: ${err.message}`);
    dialog.showErrorBox('Error de Inicio', `No se pudo lanzar el servidor:\n${err.message}`);
  });
  backendProcess.on('exit', (code) => {
    log(`Backend exited with code: ${code}`);
    if (code !== 0 && code !== null) backendErrors.push(`Proceso terminó con código ${code}`);
  });
}

app.whenReady().then(async () => {
  log('--- App starting ---');
  log(`Packaged: ${app.isPackaged}`);
  log(`Resources: ${process.resourcesPath}`);

  let command, args = [];

  if (app.isPackaged) {
    command = path.join(process.resourcesPath, 'backend.exe');
    log(`Backend path: ${command} | Exists: ${fs.existsSync(command)}`);
  } else {
    const devExe = path.join(__dirname, '../backend/dist/backend.exe');
    if (fs.existsSync(devExe)) {
      log('Using dev backend.exe');
      command = devExe;
    } else {
      log('Falling back to python uvicorn');
      command = 'python';
      args = ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8080'];
    }
  }

  const { session } = require('electron');
  await session.defaultSession.clearCache();

  // Secuencia: liberar puerto → arrancar backend → crear ventanas
  killPort(8080, () => {
    log('Port 8080 cleared. Launching backend and windows...');
    startBackend(command, args);
    createSplashWindow();
    createWindow();
  });

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

ipcMain.handle('dialog:openDirectory', async () => {
  const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory']
  });
  return canceled ? null : filePaths[0];
});

ipcMain.handle('dialog:openFile', async (event, filters) => {
  const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: filters || [{ name: 'Base de Datos SQLite', extensions: ['db'] }]
  });
  return canceled ? null : filePaths[0];
});

ipcMain.handle('fs:readFileBase64', async (event, filePath) => {
  try {
    const data = fs.readFileSync(filePath);
    return data.toString('base64');
  } catch (e) {
    return null;
  }
});

app.on('window-all-closed', () => {
  if (backendProcess) {
    log('Terminating backend...');
    try { exec(`taskkill /pid ${backendProcess.pid} /T /F`); } catch(e) {}
  }
  if (process.platform !== 'darwin') app.quit();
});
