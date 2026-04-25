const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  selectFolder: () => ipcRenderer.invoke('dialog:openDirectory'),
  selectFile: (filters) => ipcRenderer.invoke('dialog:openFile', filters),
  readFileAsBase64: (filePath) => ipcRenderer.invoke('fs:readFileBase64', filePath)
});
