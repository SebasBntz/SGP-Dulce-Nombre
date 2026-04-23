const { app, BrowserWindow, Menu, dialog, ipcMain } = require('electron');
const path = require('path');
const fs = require('fs');
const { exec, spawn } = require('child_process');
const axios = require('axios');

let mainWindow;
let splashWindow;
let backendProcess;
let backendErrors = [];

// Archivo de log para diagnóstico
const logFile = path.join(app.getPath('userData'), 'sgp-log.txt');

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
    show: false, // Regresamos al modo original para evitar parpadeos
    center: true,
    backgroundColor: '#00000000', // Transparente de nuevo
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true
    }
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
    title: "SGP - Dulce Nombre de Jesús",
    backgroundColor: '#ffffff',
    show: false, // Don't show until ready
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js'),
      devTools: !app.isPackaged
    }
  });

  // Health check loop
  let attempts = 0;
  const maxAttempts = 60;
  const checkBackend = setInterval(async () => {
    attempts++;
    try {
      await axios.get('http://127.0.0.1:8080/health', { timeout: 2000 });
      log('Backend is ready!');
      clearInterval(checkBackend);
      
      // Load the app
      mainWindow.loadURL('http://127.0.0.1:8080/');
      
      // Once the page is loaded, show the window and close splash
      mainWindow.once('ready-to-show', () => {
        setTimeout(() => {
          if (splashWindow) splashWindow.close();
          mainWindow.show();
          mainWindow.focus();
        }, 500); // Small extra delay for smoothness
      });

    } catch (e) {
      log(`Health check attempt ${attempts}/${maxAttempts} failed`);
      if (attempts >= maxAttempts) {
        clearInterval(checkBackend);
        if (splashWindow) splashWindow.close();
        
        const errorDetail = backendErrors.length > 0
          ? `\n\nErrores del servidor:\n${backendErrors.slice(-5).join('\n')}`
          : '\n\nNo se recibieron errores del servidor.';
        
        dialog.showErrorBox(
          "Error de Conexión",
          `El servidor no respondió después de ${maxAttempts} segundos.${errorDetail}\n\nRevise el archivo de log: ${logFile}`
        );
        app.quit();
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
      args = ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', '8080'];
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
    createSplashWindow();
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
