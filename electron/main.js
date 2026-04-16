const { app, BrowserWindow, Menu, dialog, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { exec, spawn } = require('child_process');
const axios = require('axios');

let mainWindow;
let backendProcess;
let backendErrors = []; // Capturar errores del backend para mostrarlos

// Archivo de log para diagnóstico
const logFile = path.join(app.getPath('userData'), 'sgp-log.txt');

function log(msg) {
  const line = `[${new Date().toISOString()}] ${msg}\n`;
  console.log(msg);
  try { fs.appendFileSync(logFile, line); } catch(e) {}
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 850,
    title: "SGP - Dulce Nombre de Jesús",
    backgroundColor: '#f0f2f5',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      devTools: !app.isPackaged
    },
    show: true
  });

  // Pantalla de carga con spinner
  mainWindow.loadURL('data:text/html;charset=utf-8,' + encodeURI(`
    <html>
      <body style="background: #f0f2f5; display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; font-family: 'Segoe UI', sans-serif; color: #0d6e4e; margin: 0;">
        <div style="font-size: 28px; font-weight: bold; margin-bottom: 10px;">SGP - Dulce Nombre</div>
        <div style="font-size: 14px; color: #666; margin-bottom: 30px;">Sistema de Gestión Parroquial</div>
        <div style="width: 50px; height: 50px; border: 5px solid #e0e0e0; border-top-color: #fca311; border-radius: 50%; animation: spin 1s linear infinite;"></div>
        <div style="margin-top: 20px; font-size: 13px; color: #888;" id="status">Iniciando servidor...</div>
        <style>@keyframes spin { to { transform: rotate(360deg); } }</style>
      </body>
    </html>
  `));

  // Chequeo de salud del backend - 60 intentos x 1s = 60 segundos de espera
  let attempts = 0;
  const maxAttempts = 60;
  const checkBackend = setInterval(async () => {
    attempts++;
    try {
      await axios.get('http://127.0.0.1:8000/health', { timeout: 2000 });
      log('Backend is ready!');
      mainWindow.loadURL('http://127.0.0.1:8000/');
      clearInterval(checkBackend);
    } catch (e) {
      log(`Health check attempt ${attempts}/${maxAttempts} failed`);
      if (attempts >= maxAttempts) {
        clearInterval(checkBackend);
        const errorDetail = backendErrors.length > 0
          ? `\n\nErrores del servidor:\n${backendErrors.slice(-5).join('\n')}`
          : '\n\nNo se recibieron errores del servidor.';
        dialog.showErrorBox(
          "Error de Conexión",
          `El servidor no respondió después de ${maxAttempts} segundos.${errorDetail}\n\nRevise el archivo de log: ${logFile}`
        );
      }
    }
  }, 1000);

  if (!app.isPackaged) {
    // mainWindow.webContents.openDevTools();
  }
}

app.whenReady().then(() => {
  log('--- App starting ---');
  log(`App packaged: ${app.isPackaged}`);
  log(`Resources path: ${process.resourcesPath}`);

  let command;
  let args = [];

  if (app.isPackaged) {
    const backendPath = path.join(process.resourcesPath, 'backend.exe');
    log(`Backend path: ${backendPath}`);
    log(`Backend exists: ${fs.existsSync(backendPath)}`);
    command = backendPath;
    args = [];
  } else {
    const devExe = path.join(__dirname, '../backend/dist/backend.exe');
    if (fs.existsSync(devExe)) {
      command = devExe;
    } else {
      command = 'python';
      args = ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8000'];
      process.chdir(path.join(__dirname, '../backend'));
    }
  }

  log(`Starting backend: ${command} ${args.join(' ')}`);

  // Usar execFile en modo empaquetado para manejar rutas con espacios
  if (app.isPackaged) {
    const { execFile } = require('child_process');
    backendProcess = execFile(command, args, { windowsHide: true }, (error) => {
      if (error) {
        log(`Backend execFile error: ${error.message}`);
        backendErrors.push(error.message);
      }
    });
  } else {
    backendProcess = spawn(command, args, { shell: true, detached: false });
  }

  if (backendProcess.stdout) {
    backendProcess.stdout.on('data', (data) => {
      log(`Backend OUT: ${data.toString().trim()}`);
    });
  }

  if (backendProcess.stderr) {
    backendProcess.stderr.on('data', (data) => {
      const msg = data.toString().trim();
      log(`Backend ERR: ${msg}`);
      backendErrors.push(msg);
    });
  }

  backendProcess.on('error', (err) => {
    log(`Backend process error: ${err.message}`);
    backendErrors.push(err.message);
    dialog.showErrorBox("Error de Inicio", `No se pudo iniciar el servidor:\n${err.message}`);
  });

  backendProcess.on('exit', (code) => {
    log(`Backend process exited with code: ${code}`);
    if (code !== 0 && code !== null) {
        backendErrors.push(`El proceso terminó con código ${code}`);
    }
  });

  const { session } = require('electron');
  session.defaultSession.clearCache().then(() => {
    createWindow();
  });

  app.on('activate', function () {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

// IPC Handler for Directory Selection
ipcMain.handle('dialog:openDirectory', async () => {
  const { canceled, filePaths } = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory']
  });
  return canceled ? null : filePaths[0];
});

app.on('window-all-closed', function () {
  if (backendProcess) {
    log("Terminating backend...");
    try {
      if (process.platform === 'win32') {
        exec(`taskkill /pid ${backendProcess.pid} /T /F`);
      } else {
        backendProcess.kill();
      }
    } catch(e) {
      log(`Error killing backend: ${e.message}`);
    }
  }
  if (process.platform !== 'darwin') app.quit();
});
