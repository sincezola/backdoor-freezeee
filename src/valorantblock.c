#include <stdio.h>
#include <windows.h>
#include <tlhelp32.h>

void kill_valorant() {
  HANDLE snapshot;
  PROCESSENTRY32 pe;

  snapshot = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
  if (snapshot == INVALID_HANDLE_VALUE)
    return;

  pe.dwSize = sizeof(PROCESSENTRY32);

  if (Process32First(snapshot, &pe)) {
    do {
      if (_stricmp(pe.szExeFile, "VALORANT.exe") == 0) {
        HANDLE hProcess =
            OpenProcess(PROCESS_TERMINATE, FALSE, pe.th32ProcessID);
        if (hProcess) {
          TerminateProcess(hProcess, 0);
          CloseHandle(hProcess);
        }
      }
    } while (Process32Next(snapshot, &pe));
  }

  CloseHandle(snapshot);
}

int main() {
  while (1) {
    kill_valorant();
    Sleep(500);
  }
  return 0;
}
